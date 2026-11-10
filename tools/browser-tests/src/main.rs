use chromiumoxide::{
    browser::{Browser, BrowserConfig},
    handler::viewport::Viewport,
    page::{Page, ScreenshotParams},
};
use futures::StreamExt;
use std::{
    error::Error,
    fs,
    path::PathBuf,
    sync::{
        Arc,
        atomic::{AtomicBool, Ordering},
    },
    thread,
    time::{Duration, Instant},
};
use tiny_http::{Header, Response, Server};

type Result<T> = std::result::Result<T, Box<dyn Error + Send + Sync>>;

struct Assets {
    url: String,
    stop: Arc<AtomicBool>,
    worker: Option<thread::JoinHandle<()>>,
}
impl Assets {
    fn start() -> Result<Self> {
        let root = PathBuf::from("dist").canonicalize()?;
        let server = Server::http("127.0.0.1:0")?;
        let url = format!("http://{}", server.server_addr());
        let stop = Arc::new(AtomicBool::new(false));
        let flag = Arc::clone(&stop);
        let worker = thread::spawn(move || {
            while !flag.load(Ordering::Relaxed) {
                if let Ok(Some(request)) = server.recv_timeout(Duration::from_millis(50)) {
                    let path = request.url().split('?').next().unwrap_or("/");
                    let relative = if path.ends_with('/') {
                        format!("{}index.html", path)
                    } else {
                        path.to_string()
                    };
                    let file = root.join(relative.trim_start_matches('/'));
                    let response = match file
                        .canonicalize()
                        .ok()
                        .filter(|p| p.starts_with(&root))
                        .and_then(|p| fs::read(p).ok())
                    {
                        Some(bytes) => {
                            let mime = match file.extension().and_then(|s| s.to_str()) {
                                Some("js") => "text/javascript",
                                Some("css") => "text/css",
                                Some("wasm") => "application/wasm",
                                _ => "text/html",
                            };
                            Response::from_data(bytes).with_header(
                                Header::from_bytes("Content-Type", mime).expect("valid header"),
                            )
                        }
                        None => Response::from_data(b"Not found".to_vec()).with_status_code(404),
                    };
                    let _ = request.respond(response);
                }
            }
        });
        Ok(Self {
            url,
            stop,
            worker: Some(worker),
        })
    }
}
impl Drop for Assets {
    fn drop(&mut self) {
        self.stop.store(true, Ordering::Relaxed);
        if let Some(worker) = self.worker.take() {
            let _ = worker.join();
        }
    }
}

async fn check(page: &Page, expression: &str) -> Result<()> {
    let start = Instant::now();
    loop {
        if page
            .evaluate(format!("Boolean({expression})"))
            .await?
            .into_value::<bool>()?
        {
            return Ok(());
        }
        if start.elapsed() > Duration::from_secs(5) {
            return Err(format!("Browser assertion timed out: {expression}").into());
        }
        tokio::time::sleep(Duration::from_millis(40)).await;
    }
}
async fn js(page: &Page, script: &str) -> Result<()> {
    page.evaluate(script).await?;
    Ok(())
}
async fn click(page: &Page, text: &str) -> Result<()> {
    let selector = match text {
        "Slow request" => "button[type=button]:nth-child(1)",
        "Fast request" => "button[type=button]:nth-child(2)",
        "Cancel" => "button[type=button]:nth-child(3)",
        "Apply preferences" => "button[type=submit]",
        "About" => "a[href='#/about']",
        "Overview" => "a[href='#/overview']",
        "Preferences" => "a[href='#/settings']",
        "Latest response" => "a[href='#/']",
        _ => return Err(format!("Unknown action: {text}").into()),
    };
    page.find_element(selector).await?.click().await?;
    Ok(())
}
async fn input(page: &Page, value: i64) -> Result<()> {
    js(page, &format!("(() => {{const e = document.querySelector('#number'); e.value = '{value}'; e.dispatchEvent(new Event('input', {{bubbles:true}}));}})()" )).await
}
async fn capture(page: &Page, name: &str) -> Result<()> {
    // Wait for CSS and fonts before taking actual production-page captures.
    page.evaluate_function("async () => { await document.fonts.ready; await new Promise(requestAnimationFrame); return true; }").await?;
    fs::write(
        format!("artifacts/{name}.png"),
        page.screenshot(ScreenshotParams::builder().full_page(false).build())
            .await?,
    )?;
    Ok(())
}
const INIT: &str = r#"(() => {
  window.__errors = [];
  addEventListener('error', e => window.__errors.push(e.message || 'asset error'), true);
  addEventListener('unhandledrejection', e => window.__errors.push(String(e.reason)));
  const set = window.setTimeout.bind(window), clear = window.clearTimeout.bind(window), slow = new Map();
  window.__cleared = 0;
  window.setTimeout = (callback, delay, ...args) => {
    let id;
    id = set((...a) => { if (slow.has(id)) slow.set(id, true); callback(...a); }, delay, ...args);
    if (delay === 1500) slow.set(id, false);
    return id;
  };
  window.clearTimeout = id => { if (slow.get(id) === false) window.__cleared++; slow.delete(id); return clear(id); };
})()"#;

async fn suite(page: &Page, url: &str) -> Result<()> {
    page.evaluate_on_new_document(INIT).await?;
    page.goto(url).await?;
    check(page, "!!document.querySelector('#number')").await?;
    input(page, 11).await?;
    click(page, "Slow request").await?;
    input(page, 22).await?;
    click(page, "Fast request").await?;
    check(
        page,
        "document.querySelector('[role=status]')?.textContent.includes('Latest result: 22')",
    )
    .await?;
    tokio::time::sleep(Duration::from_millis(1700)).await;
    check(
        page,
        "document.querySelector('[role=status]')?.textContent.includes('Latest result: 22')",
    )
    .await?;
    js(page, "window.__cleared = 0").await?;
    input(page, 33).await?;
    click(page, "Slow request").await?;
    click(page, "Cancel").await?;
    check(page, "window.__cleared === 1").await?;
    tokio::time::sleep(Duration::from_millis(1700)).await;
    check(page, "document.querySelector('[role=status]')?.textContent.includes('Latest result: 22') && document.querySelector('[role=status]')?.textContent.includes('cancelled')").await?;
    capture(page, "response-lab").await?;
    println!("PASS: stale result rejection, observed cancellation and result retention");
    js(page, "window.__cleared = 0").await?;
    click(page, "Slow request").await?;
    click(page, "About").await?;
    check(
        page,
        "window.__cleared === 1 && document.querySelector('h1')?.textContent === 'About'",
    )
    .await?;
    tokio::time::sleep(Duration::from_millis(1700)).await;
    click(page, "Latest response").await?;
    check(
        page,
        "document.querySelector('[role=status]')?.textContent.includes('No result yet')",
    )
    .await?;
    // Exercise actual CDP keyboard input, not a JS click, for keyboard coverage.
    page.find_element("#number").await?.click().await?;
    page.find_element("#number").await?.press_key("Tab").await?;
    check(
        page,
        "document.activeElement.textContent === 'Slow request'",
    )
    .await?;
    page.find_element("button")
        .await?
        .press_key("Enter")
        .await?;
    check(
        page,
        "document.querySelector('[role=status]')?.textContent.includes('Request pending')",
    )
    .await?;
    click(page, "Cancel").await?;
    println!("PASS: navigation cleanup and keyboard activation");
    let axe = fs::read_to_string(".tools/axe.min.js")?;
    js(page, &axe).await?;
    let violations: serde_json::Value = page.evaluate_function("async () => (await axe.run()).violations.map(v => ({id:v.id, nodes:v.nodes.map(n=>n.target)}))").await?.into_value()?;
    if violations != serde_json::json!([]) {
        return Err(format!("Accessibility violations: {violations}").into());
    }
    for (route, name, heading) in [
        ("overview", "workspace-overview", "A little more clarity."),
        ("settings", "preferences", "Your space, your pace."),
    ] {
        click(
            page,
            if route == "overview" {
                "Overview"
            } else {
                "Preferences"
            },
        )
        .await?;
        check(
            page,
            &format!(
                "document.querySelector('h1')?.textContent === {}",
                serde_json::to_string(heading)?
            ),
        )
        .await?;
        if route == "settings" {
            click(page, "Apply preferences").await?;
            check(
                page,
                "document.querySelector('[role=status]')?.textContent.includes('Applied')",
            )
            .await?;
            page.find_element("#display-name")
                .await?
                .click()
                .await?
                .type_str("!")
                .await?;
            check(
                page,
                "document.querySelector('[role=status]')?.textContent.includes('No account')",
            )
            .await?;
            page.find_element("#display-name")
                .await?
                .press_key("Backspace")
                .await?;
            click(page, "Apply preferences").await?;
        }

        let violations: serde_json::Value = page
            .evaluate_function("async () => (await axe.run()).violations.map(v => v.id)")
            .await?
            .into_value()?;
        if violations != serde_json::json!([]) {
            return Err(format!("{route} accessibility violations: {violations}").into());
        }
        capture(page, name).await?;
    }
    check(page, "window.__errors.length === 0").await?;
    page.goto(format!("{url}sub/#/about")).await?;
    check(
        page,
        "document.querySelector('h1')?.textContent === 'About'",
    )
    .await?;
    click(page, "Latest response").await?;
    check(page, "!!document.querySelector('#number')").await?;
    check(page, "getComputedStyle([...document.querySelectorAll('button')].find(e=>e.textContent === 'Fast request')).backgroundColor === 'rgb(49, 87, 183)'").await?;
    input(page, 42).await?;
    click(page, "Fast request").await?;
    check(
        page,
        "document.querySelector('[role=status]')?.textContent.includes('Latest result: 42')",
    )
    .await?;
    check(page, "window.__errors.length === 0").await?;
    println!(
        "PASS: axe accessibility smoke, examples, direct URL and subpath production CSS/WASM loading"
    );
    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    fs::create_dir_all("artifacts")?;
    let assets = Assets::start()?;
    let mut config = BrowserConfig::builder().viewport(Viewport {
        width: 1440,
        height: 1000,
        ..Default::default()
    });
    if let Ok(path) = std::env::var("CHROMIUM_PATH") {
        config = config.chrome_executable(path);
    }
    if std::env::var_os("CHROMIUM_NO_SANDBOX").is_some() {
        config = config.no_sandbox();
    }
    let (mut browser, mut handler) = Browser::launch(config.build()?).await?;
    let task = tokio::spawn(async move {
        while let Some(event) = handler.next().await {
            if event.is_err() {
                break;
            }
        }
    });
    let result = async {
        let page = browser.new_page("about:blank").await?;
        suite(&page, &format!("{}/", assets.url)).await
    }
    .await;
    let _ = browser.close().await;
    let _ = task.await;
    result
}
