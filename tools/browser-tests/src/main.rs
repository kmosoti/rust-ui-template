use chromiumoxide::{
    browser::{Browser, BrowserConfig},
    cdp::browser_protocol::{
        emulation::SetDeviceMetricsOverrideParams, page::Viewport as CaptureViewport,
    },
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
                                Some("svg") => "image/svg+xml",
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
        "About" => "nav[aria-label='Main navigation'] a[href='#/about']",
        "Library" => "nav[aria-label='Main navigation'] a[href='#/overview']",
        "Preferences" => "nav[aria-label='Main navigation'] a[href='#/settings']",
        "Latest response" => "nav[aria-label='Main navigation'] a[href='#/']",
        _ => return Err(format!("Unknown action: {text}").into()),
    };
    check(
        page,
        &format!(
            "((e) => e && (e.getAttribute('aria-label') || e.textContent.trim()) === {})(document.querySelector({}))",
            serde_json::to_string(text)?,
            serde_json::to_string(selector)?
        ),
    )
    .await?;
    page.find_element(selector).await?.click().await?;
    Ok(())
}
async fn input(page: &Page, value: i64) -> Result<()> {
    js(page, &format!("(() => {{const e = document.querySelector('#number'); e.value = '{value}'; e.dispatchEvent(new Event('input', {{bubbles:true}}));}})()" )).await
}
async fn capture(page: &Page, name: &str) -> Result<()> {
    // Wait for CSS and fonts before taking actual production-page captures.
    page.evaluate_function("async () => { await document.fonts.ready; await new Promise(requestAnimationFrame); return true; }").await?;
    let width: f64 = page.evaluate("innerWidth").await?.into_value()?;
    let height: f64 = page
        .evaluate("document.documentElement.scrollHeight")
        .await?
        .into_value()?;
    fs::write(
        format!("artifacts/{name}.png"),
        page.screenshot(
            ScreenshotParams::builder()
                .full_page(false)
                .capture_beyond_viewport(true)
                .clip(CaptureViewport {
                    x: 0.0,
                    y: 0.0,
                    width,
                    height,
                    scale: 1.0,
                })
                .build(),
        )
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
    check(
        page,
        "document.querySelector('h1')?.textContent === 'Your library'",
    )
    .await?;
    check(page, "document.querySelector('[data-testid=featured-art]')?.naturalWidth > 0 && document.querySelector('nav [aria-current=page]')?.textContent.includes('Library')").await?;
    js(page, "document.querySelector('.skip-link').focus()").await?;
    check(page, "document.activeElement.matches('.skip-link') && document.activeElement.getBoundingClientRect().width > 100 && document.activeElement.getBoundingClientRect().left >= 0").await?;
    page.find_element(".skip-link")
        .await?
        .press_key("Enter")
        .await?;
    check(
        page,
        "document.activeElement.id === 'workspace-content' && location.hash === ''",
    )
    .await?;
    page.find_element("[data-testid=launch-example]")
        .await?
        .click()
        .await?;
    check(page, "location.hash === '#/' && document.querySelector('nav [aria-current=page]')?.textContent.includes('Latest response')").await?;
    println!(
        "PASS: default library, bundled original artwork, active navigation and keyboard skip/launch"
    );
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
    check(
        page,
        "document.querySelector('[role=status]')?.dataset.tone === 'warning'",
    )
    .await?;
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
    check(page, "document.querySelector('[data-testid=host-info]')?.textContent.includes('unavailable in browser mode')").await?;
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
    js(page, "document.querySelector('#number').value = ''; document.querySelector('#number').dispatchEvent(new Event('input', {bubbles:true}))").await?;
    click(page, "Fast request").await?;
    check(page, "document.querySelector('[role=status]')?.dataset.tone === 'danger' && document.querySelector('[role=status]').textContent.includes('Enter a whole number')").await?;
    println!("PASS: navigation cleanup, keyboard activation and text-labeled feedback tones");
    let axe = fs::read_to_string(".tools/axe.min.js")?;
    js(page, &axe).await?;
    let violations: serde_json::Value = page.evaluate_function("async () => (await axe.run()).violations.map(v => ({id:v.id, nodes:v.nodes.map(n=>n.target)}))").await?.into_value()?;
    if violations != serde_json::json!([]) {
        return Err(format!("Accessibility violations: {violations}").into());
    }
    for (route, name, heading) in [
        ("overview", "workspace-overview", "Your library"),
        ("settings", "preferences", "Preferences"),
    ] {
        click(
            page,
            if route == "overview" {
                "Library"
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
    for (width, height) in [(1440, 1000), (390, 844), (320, 812)] {
        for (link, name, heading) in [
            ("Latest response", "response", "Latest response"),
            ("Library", "overview", "Your library"),
            ("Preferences", "preferences", "Preferences"),
            ("About", "about", "About"),
        ] {
            page.execute(SetDeviceMetricsOverrideParams::new(
                width, height, 1.0, false,
            ))
            .await?;
            click(page, link).await?;
            check(
                page,
                &format!(
                    "document.querySelector('h1')?.textContent === {}",
                    serde_json::to_string(heading)?
                ),
            )
            .await?;
            if name == "about" {
                check(page, "document.querySelector('[data-testid=host-info]')?.textContent.includes('unavailable in browser mode')").await?;
            }
            page.evaluate_function("async () => { await document.fonts.ready; await new Promise(requestAnimationFrame); return true; }").await?;
            let metrics: serde_json::Value = page
                .evaluate_function(include_str!("../../../tests/layout-audit.js"))
                .await?
                .into_value()?;
            fs::write(
                format!("artifacts/layout-{name}-{width}.json"),
                serde_json::to_vec_pretty(&metrics)?,
            )?;
            capture(page, &format!("layout-{name}-{width}")).await?;
            if metrics["horizontalOverflow"] == true
                || metrics["clippedText"] != serde_json::json!([])
                || metrics["overlaps"] != serde_json::json!([])
                || metrics["escapedControls"] != serde_json::json!([])
            {
                return Err(format!("Layout defect at {width}px on {name}: {metrics}").into());
            }
            let violations: serde_json::Value = page
                .evaluate_function("async () => (await axe.run()).violations.map(v => v.id)")
                .await?
                .into_value()?;
            if violations != serde_json::json!([]) {
                return Err(format!("Accessibility at {width}px on {name}: {violations}").into());
            }
        }
    }
    // 200% text at the narrow reflow viewport; all routes must remain reachable.
    page.execute(SetDeviceMetricsOverrideParams::new(320, 812, 1.0, false))
        .await?;
    js(page, "document.documentElement.style.fontSize = '200%'").await?;
    for link in ["Library", "Latest response", "Preferences", "About"] {
        click(page, link).await?;
        let heading = if link == "Library" {
            "Your library"
        } else {
            link
        };
        check(
            page,
            &format!(
                "document.querySelector('h1')?.textContent === {}",
                serde_json::to_string(heading)?
            ),
        )
        .await?;
        page.evaluate_function("async () => { await document.fonts.ready; await new Promise(requestAnimationFrame); return true; }").await?;
        let metrics: serde_json::Value = page
            .evaluate_function(include_str!("../../../tests/layout-audit.js"))
            .await?
            .into_value()?;
        if metrics["horizontalOverflow"] == true
            || metrics["clippedText"] != serde_json::json!([])
            || metrics["escapedControls"] != serde_json::json!([])
        {
            return Err(format!("200% text reflow defect on {link}: {metrics}").into());
        }
    }
    capture(page, "text-zoom-about-320").await?;
    js(page, "document.documentElement.style.fontSize = ''").await?;
    page.execute(SetDeviceMetricsOverrideParams::new(1440, 1000, 1.0, false))
        .await?;
    click(page, "Preferences").await?;
    check(page, "!!document.querySelector('#color-scheme')").await?;
    // A real native select keyboard interaction, in addition to exhaustive change events.
    page.find_element("#color-scheme").await?.click().await?;
    page.find_element("#color-scheme")
        .await?
        .press_key("ArrowDown")
        .await?;
    page.find_element("#color-scheme")
        .await?
        .press_key("Enter")
        .await?;
    check(
        page,
        "document.querySelector('[data-palette]')?.dataset.palette === 'signal-blue'",
    )
    .await?;
    for palette in [
        "nocturne",
        "signal-blue",
        "butter-iris",
        "lime-graphite",
        "sulu-fir",
        "blooming-romance",
        "desert-dusk",
    ] {
        for width in [1440, 320] {
            page.execute(SetDeviceMetricsOverrideParams::new(width, 1000, 1.0, false))
                .await?;
            click(page, "Preferences").await?;
            check(page, "!!document.querySelector('#color-scheme')").await?;
            js(page, &format!("(() => {{ const e = document.querySelector('#color-scheme'); e.value = {}; e.dispatchEvent(new Event('change', {{bubbles:true}})); }})()", serde_json::to_string(palette)?)).await?;
            check(
                page,
                &format!(
                    "document.querySelector('[data-palette]')?.dataset.palette === {}",
                    serde_json::to_string(palette)?
                ),
            )
            .await?;
            page.find_element("#color-scheme").await?.focus().await?;
            page.find_element("#color-scheme")
                .await?
                .press_key("Tab")
                .await?;
            check(page, "document.activeElement.id === 'display-name' && document.activeElement.matches(':focus-visible') && parseFloat(getComputedStyle(document.activeElement).outlineWidth) >= 2").await?;
            page.find_element("button[type=submit]")
                .await?
                .hover()
                .await?;
            check(
                page,
                "document.querySelector('button[type=submit]').matches(':hover')",
            )
            .await?;
            page.evaluate_function(
                "async () => { await new Promise(requestAnimationFrame); return true; }",
            )
            .await?;
            let contrast: serde_json::Value = page
                .evaluate_function(include_str!("../../../tests/palette-contrast.js"))
                .await?
                .into_value()?;
            fs::write(
                format!("artifacts/contrast-{palette}-{width}.json"),
                serde_json::to_vec_pretty(&contrast)?,
            )?;
            if contrast["failures"] != serde_json::json!([])
                || contrast["hoverMatches"] != true
                || contrast["focusMatches"] != true
            {
                return Err(format!("Palette contrast defect: {contrast}").into());
            }
            for (link, heading) in [
                ("Preferences", "Preferences"),
                ("Library", "Your library"),
                ("Latest response", "Latest response"),
                ("About", "About"),
            ] {
                click(page, link).await?;
                check(
                    page,
                    &format!(
                        "document.querySelector('h1')?.textContent === {}",
                        serde_json::to_string(heading)?
                    ),
                )
                .await?;
                check(
                    page,
                    &format!(
                        "document.querySelector('[data-palette]')?.dataset.palette === {}",
                        serde_json::to_string(palette)?
                    ),
                )
                .await?;
                if link == "About" {
                    check(page, "document.querySelector('[data-testid=host-info]')?.textContent.includes('unavailable in browser mode')").await?;
                }
                page.evaluate_function("async () => { await document.fonts.ready; await new Promise(requestAnimationFrame); return true; }").await?;
                let metrics: serde_json::Value = page
                    .evaluate_function(include_str!("../../../tests/layout-audit.js"))
                    .await?
                    .into_value()?;
                if metrics["horizontalOverflow"] == true
                    || metrics["clippedText"] != serde_json::json!([])
                    || metrics["escapedControls"] != serde_json::json!([])
                    || metrics["overlaps"] != serde_json::json!([])
                {
                    return Err(format!("{palette}/{link}/{width} layout: {metrics}").into());
                }
                let violations: serde_json::Value = page
                    .evaluate_function("async () => (await axe.run()).violations.map(v => v.id)")
                    .await?
                    .into_value()?;
                if violations != serde_json::json!([]) {
                    return Err(
                        format!("{palette}/{link}/{width} accessibility: {violations}").into(),
                    );
                }
                if link == "Preferences" {
                    check(
                        page,
                        &format!(
                            "document.querySelector('#color-scheme')?.value === {}",
                            serde_json::to_string(palette)?
                        ),
                    )
                    .await?;
                    capture(page, &format!("palette-settings-{palette}-{width}")).await?;
                }
                if link == "Library" {
                    capture(page, &format!("palette-{palette}-{width}")).await?;
                }
            }
        }
        click(page, "Preferences").await?;
        check(page, "!!document.querySelector('#color-scheme')").await?;
        js(page, "document.documentElement.style.fontSize = '200%'").await?;
        let metrics: serde_json::Value = page
            .evaluate_function(include_str!("../../../tests/layout-audit.js"))
            .await?
            .into_value()?;
        if metrics["horizontalOverflow"] == true
            || metrics["clippedText"] != serde_json::json!([])
            || metrics["escapedControls"] != serde_json::json!([])
        {
            return Err(format!("{palette} 200% text: {metrics}").into());
        }
        js(page, "document.documentElement.style.fontSize = ''").await?;
    }
    // Reload resets the app-session choice, including the subpath production smoke below.
    page.goto(url).await?;
    check(
        page,
        "document.querySelector('[data-palette]')?.dataset.palette === 'nocturne'",
    )
    .await?;
    println!(
        "PASS: seven palettes, rendered contrast, 56 route/viewport axe/layout checks, session navigation and reload reset"
    );
    page.execute(SetDeviceMetricsOverrideParams::new(1440, 1000, 1.0, false))
        .await?;
    println!("PASS: desktop/390px/320px layout metrics, captures and axe smoke");
    check(page, "window.__errors.length === 0").await?;
    page.goto(format!("{url}sub/#/about")).await?;
    check(
        page,
        "document.querySelector('h1')?.textContent === 'About'",
    )
    .await?;
    click(page, "Library").await?;
    check(
        page,
        "document.querySelector('[data-testid=featured-art]')?.naturalWidth > 0",
    )
    .await?;
    click(page, "Latest response").await?;
    check(page, "!!document.querySelector('#number')").await?;
    check(page, "getComputedStyle([...document.querySelectorAll('button')].find(e=>e.textContent === 'Fast request')).backgroundColor === 'rgb(182, 156, 255)'").await?;
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
        let probe = browser.new_page("about:blank").await?;
        js(&probe, r#"document.body.innerHTML='<div style="width:2200px;height:20px">overflow sentinel</div><div style="width:12px;height:12px;overflow:hidden;white-space:nowrap">clipped sentinel text</div><div data-layout-region="a" style="position:absolute;left:0;top:100px;width:100px;height:100px"></div><div data-layout-region="b" style="position:absolute;left:20px;top:120px;width:100px;height:100px"></div>'"#).await?;
        let detected: serde_json::Value = probe.evaluate_function(include_str!("../../../tests/layout-audit.js")).await?.into_value()?;
        if detected["horizontalOverflow"] != true || detected["clippedText"] == serde_json::json!([]) || detected["overlaps"] == serde_json::json!([]) {
            return Err("Layout audit failed to detect the deliberate defect fixture".into());
        }
        js(&probe, r#"document.body.innerHTML='<div style="width:120px"><input style="width:250px" aria-label="probe"></div>'"#).await?;
        let contained: serde_json::Value = probe.evaluate_function(include_str!("../../../tests/layout-audit.js")).await?.into_value()?;
        if contained["horizontalOverflow"] != false || contained["escapedControls"] == serde_json::json!([]) {
            return Err("Layout audit failed to detect a control escaping its parent inside the viewport".into());
        }
        probe.close().await?;
        println!("PASS: deliberate overflow, clipping and region-overlap fixture rejected");
        let page = browser.new_page("about:blank").await?;
        suite(&page, &format!("{}/", assets.url)).await
    }
    .await;
    let _ = browser.close().await;
    let _ = task.await;
    result
}
