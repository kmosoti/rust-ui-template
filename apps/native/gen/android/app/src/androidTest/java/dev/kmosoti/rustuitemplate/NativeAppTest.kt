package dev.kmosoti.rustuitemplate

import android.graphics.Bitmap
import android.graphics.Rect
import android.graphics.Color
import android.os.Handler
import android.os.Looper
import android.view.PixelCopy
import android.os.SystemClock
import android.view.MotionEvent
import android.content.pm.ActivityInfo
import android.view.View
import android.view.ViewGroup
import android.webkit.WebView
import androidx.lifecycle.Lifecycle
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.test.core.app.ActivityScenario
import androidx.test.espresso.Espresso
import androidx.test.espresso.web.sugar.Web.onWebView
import androidx.test.espresso.web.webdriver.DriverAtoms.findElement
import androidx.test.espresso.web.webdriver.DriverAtoms.webClick
import androidx.test.espresso.web.webdriver.Locator
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.json.JSONObject
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicReference

@RunWith(AndroidJUnit4::class)
class NativeAppTest {
    private lateinit var scenario: ActivityScenario<MainActivity>
    private lateinit var web: WebView
    private var phase = "startup"
    private val instrumentation get() = InstrumentationRegistry.getInstrumentation()

    private fun findWeb(view: View): WebView? {
        if (view is WebView) return view
        if (view is ViewGroup) for (i in 0 until view.childCount) {
            val found = findWeb(view.getChildAt(i)); if (found != null) return found
        }
        return null
    }

    @Before fun launch() {
        scenario = ActivityScenario.launch(MainActivity::class.java)
        val deadline = System.currentTimeMillis() + 60000
        while (!::web.isInitialized && System.currentTimeMillis() < deadline) {
            scenario.onActivity { activity -> findWeb(activity.findViewById(android.R.id.content))?.let { web = it } }
            if (!::web.isInitialized) Thread.sleep(100)
        }
        assertTrue("WebView did not initialize", ::web.isInitialized)
        val version = WebView.getCurrentWebViewPackage()?.versionName ?: "0"
        assertTrue("Tailwind4 requires WebView Chromium111+; actual=$version", version.substringBefore('.').toInt() >= 111)
        waitFor("document.querySelector('h1')?.textContent === 'Your library'", 60000)
        waitFor("document.querySelector('[data-testid=featured-art]')?.naturalWidth > 0")
        assertEquals("\"https:\"", js("location.protocol"))
        assertEquals("1", js("document.querySelectorAll('link[rel=stylesheet]').length"))
        waitFor("getComputedStyle(document.body).backgroundColor === 'rgb(17, 18, 22)'")
        js(instrumentation.context.assets.open("axe.min.js").bufferedReader().use { it.readText() })
        accessibility(); layout(); capture("library")
        js("window.__nativeErrors=[]; addEventListener('error',e=>window.__nativeErrors.push(e.message)); addEventListener('unhandledrejection',e=>window.__nativeErrors.push(String(e.reason))); true")
    }

    private fun js(script: String): String {
        val value = AtomicReference<String>()
        val ready = CountDownLatch(1)
        instrumentation.runOnMainSync { web.evaluateJavascript(script) { value.set(it); ready.countDown() } }
        assertTrue("JS timeout in $phase", ready.await(10, TimeUnit.SECONDS))
        return value.get()
    }

    private fun waitFor(predicate: String, timeout: Long = 15000) {
        val deadline = System.currentTimeMillis() + timeout
        while (js("Boolean($predicate)") != "true") {
            if (System.currentTimeMillis() > deadline) fail("$phase: timed out: $predicate")
            Thread.sleep(50)
        }
    }

    private fun click(selector: String) {
        onWebView().withElement(findElement(Locator.CSS_SELECTOR, selector)).perform(webClick())
    }

    private fun route(hash: String, heading: String) {
        click("nav[aria-label='Main navigation'] a[href='$hash']")
        waitFor("document.querySelector('h1')?.textContent === ${JSONObject.quote(heading)}")
    }

    private fun invoke(payload: String): JSONObject {
        js("window.__probe=null; window.__TAURI_INTERNALS__.invoke('app_info',{request:$payload}).then(value=>window.__probe={ok:true,value}).catch(error=>window.__probe={ok:false,error:String(error)}); true")
        waitFor("window.__probe !== null")
        return JSONObject(js("window.__probe"))
    }

    private fun input(number: Int) {
        js("document.querySelector('#number').value='$number'; document.querySelector('#number').dispatchEvent(new Event('input',{bubbles:true})); true")
    }

    private fun tapInput() {
        js("document.querySelector('#number').scrollIntoView({block:'center'}); true")
        val box = JSONObject(js("(()=>{const r=document.querySelector('#number').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2,width:innerWidth}})()"))
        val location = IntArray(2)
        var scale = 1f
        instrumentation.runOnMainSync { web.getLocationOnScreen(location); scale = web.width.toFloat()/box.getDouble("width").toFloat() }
        val x = location[0] + box.getDouble("x").toFloat()*scale
        val y = location[1] + box.getDouble("y").toFloat()*scale
        val now = SystemClock.uptimeMillis()
        for ((action, time) in listOf(MotionEvent.ACTION_DOWN to now, MotionEvent.ACTION_UP to now+50)) {
            val event = MotionEvent.obtain(now, time, action, x, y, 0)
            instrumentation.sendPointerSync(event); event.recycle()
        }
    }

    private fun evidence(name: String, value: String) {
        val directory = File(instrumentation.targetContext.filesDir, "evidence").apply { mkdirs() }
        File(directory, name).writeText(value)
    }

    private fun accessibility() {
        js("window.__axeResult=null; axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}).then(r=>window.__axeResult={violations:r.violations}).catch(e=>window.__axeResult={error:String(e)}); true")
        waitFor("window.__axeResult !== null", 30000)
        val result = JSONObject(js("window.__axeResult"))
        evidence("axe-${phase.replace(' ', '-')}.json", result.toString())
        assertFalse(result.toString(), result.has("error"))
        assertEquals(result.toString(), 0, result.getJSONArray("violations").length())
    }

    private fun waitForIme(visible: Boolean) {
        val deadline = System.currentTimeMillis() + 15000
        while (true) {
            var shown = false
            scenario.onActivity { activity ->
                shown = ViewCompat.getRootWindowInsets(activity.findViewById(android.R.id.content))?.isVisible(WindowInsetsCompat.Type.ime()) ?: false
            }
            if (shown == visible) return
            if (System.currentTimeMillis() > deadline) fail("IME visibility did not become $visible")
            Thread.sleep(50)
        }
    }

    private fun layout() {
        val audit = instrumentation.context.assets.open("layout-audit.js").bufferedReader().use { it.readText() }
        val result = JSONObject(js("($audit)()"))
        evidence("layout-${phase.replace(' ', '-')}.json", result.toString())
        assertFalse(result.toString(), result.getBoolean("horizontalOverflow"))
        for (key in listOf("clippedText", "escapedControls", "overlaps")) assertEquals(result.toString(), 0, result.getJSONArray(key).length())
    }

    @Test fun bundledUiAndNativeBoundary() {
        phase = "native command"
        val response = invoke("{schema_version:1}")
        val denial = InstrumentationRegistry.getArguments().getString("denial") == "true"
        if (denial) {
            assertFalse(response.toString(), response.getBoolean("ok"))
            assertTrue(response.toString(), response.getString("error").lowercase().let { "not allowed" in it || "denied" in it })
            route("#/about", "About")
            waitFor("document.querySelector('[data-testid=host-info]')?.textContent === 'Application information could not be read.'")
            return
        }
        assertTrue(response.toString(), response.getBoolean("ok"))
        val info = response.getJSONObject("value")
        assertEquals(1, info.getInt("schema_version")); assertEquals("android", info.getString("platform"))
        assertEquals("rust-ui-template", info.getString("name"))
        for (payload in listOf("{}", "{schema_version:0}", "{schema_version:1,path:'/etc/passwd'}")) {
            val invalid = invoke(payload)
            assertFalse(invalid.toString(), invalid.getBoolean("ok"))
        }
        phase = "stale result and cancellation"
        route("#/", "Latest response")
        input(11); click("button[type=button]:nth-child(1)")
        input(22); click("button[type=button]:nth-child(2)")
        waitFor("document.querySelector('[role=status]')?.textContent.includes('Latest result: 22')")
        Thread.sleep(1700)
        waitFor("document.querySelector('[role=status]')?.textContent.includes('Latest result: 22')")
        input(33); click("button[type=button]:nth-child(1)"); click("button[type=button]:nth-child(3)")
        Thread.sleep(1700)
        waitFor("document.querySelector('[role=status]')?.textContent.includes('cancelled') && document.querySelector('[role=status]').textContent.includes('Latest result: 22')")
        click("button[type=button]:nth-child(1)"); route("#/about", "About")
        Thread.sleep(1700); route("#/", "Latest response")
        waitFor("document.querySelector('[role=status]')?.textContent.includes('No result yet')")
        phase = "IME and layout"
        tapInput(); waitForIme(true); waitFor("(()=>{const r=document.querySelector('#number').getBoundingClientRect();return r.top>=0 && r.bottom<=innerHeight})()"); layout(); capture("keyboard")
        Espresso.closeSoftKeyboard(); waitForIme(false); layout()
        phase = "palette navigation"
        route("#/settings", "Preferences")
        js("const e=document.querySelector('#color-scheme'); e.value='signal-blue'; e.dispatchEvent(new Event('change',{bubbles:true})); true")
        waitFor("document.querySelector('[data-palette]')?.dataset.palette === 'signal-blue'")
        accessibility(); layout()
        route("#/about", "About")
        waitFor("document.querySelector('[data-testid=host-info]')?.textContent.includes('android')")
        waitFor("document.querySelector('[data-palette]')?.dataset.palette === 'signal-blue'")
        phase = "rotation"
        scenario.onActivity { it.requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE }
        waitFor("innerWidth > innerHeight"); layout(); capture("landscape")
        scenario.onActivity { it.requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT }
        waitFor("innerHeight > innerWidth"); layout(); capture("portrait")
        phase = "back and lifecycle"
        Espresso.pressBack()
        waitFor("document.querySelector('h1')?.textContent === 'Preferences'")
        scenario.moveToState(Lifecycle.State.CREATED); scenario.moveToState(Lifecycle.State.RESUMED)
        waitFor("document.querySelector('[data-palette]')?.dataset.palette === 'signal-blue'")
        phase = "CSP"
        js("window.__inlineProbe=false; window.__cspEvents=0; addEventListener('securitypolicyviolation',()=>window.__cspEvents++); const s=document.createElement('script'); s.textContent='window.__inlineProbe=true'; document.head.append(s); true")
        waitFor("window.__cspEvents>0"); assertEquals("false", js("window.__inlineProbe"))
        assertEquals("[]", js("window.__nativeErrors")); accessibility(); layout()
    }

    private fun capture(name: String) {
        // PixelCopy reads this window's presented WebView surface rather than
        // UiAutomation's occasionally stale full-display rotation buffer.
        val directory = File(instrumentation.targetContext.filesDir, "evidence").apply { mkdirs() }
        val deadline = SystemClock.uptimeMillis() + 10000
        var diagnostics = "no sample"
        var consecutive = 0
        while (SystemClock.uptimeMillis() < deadline) {
            val painted = CountDownLatch(1)
            instrumentation.runOnMainSync {
                web.postVisualStateCallback(0L, object : WebView.VisualStateCallback() {
                    override fun onComplete(requestId: Long) { web.postOnAnimation { painted.countDown() } }
                })
            }
            assertTrue("WebView did not paint $name", painted.await((deadline-SystemClock.uptimeMillis()).coerceAtLeast(1), TimeUnit.MILLISECONDS))
            val map = JSONObject(js("""(()=>{
              const canvas=document.createElement('canvas');canvas.width=canvas.height=1;
              const ctx=canvas.getContext('2d');
              const points=[];
              for(const fx of [.1,.3,.5,.7,.9]) for(const fy of [.15,.4,.65,.85]) {
                const x=innerWidth*fx,y=innerHeight*fy;
                let el=document.elementFromPoint(x,y),color=null;
                // Avoid foreground pixels: only sample padding/empty areas.
                const range=document.createRange();
                let covered=false;
                for(const child of el?.childNodes??[]) if(child.nodeType===Node.TEXT_NODE && child.textContent.trim()) {
                  range.selectNodeContents(child);
                  for(const r of range.getClientRects()) if(x>=r.left-2&&x<=r.right+2&&y>=r.top-2&&y<=r.bottom+2) covered=true;
                }
                if(covered||el?.closest('img,svg,input,button,select,textarea')) continue;
                while(el&&!color){ctx.clearRect(0,0,1,1);ctx.fillStyle=getComputedStyle(el).backgroundColor;ctx.fillRect(0,0,1,1);const c=Array.from(ctx.getImageData(0,0,1,1).data);if(c[3]===255)color=c;el=el.parentElement;}
                if(color)points.push({x,y,r:color[0],g:color[1],b:color[2]});
              }
              const markers=Array.from(document.querySelectorAll('h1,nav a[aria-current="page"],input:focus')).map(e=>e.getBoundingClientRect().toJSON()).filter(r=>r.top>=0&&r.bottom<=innerHeight&&r.width>20&&r.height>10);
              return {width:innerWidth,height:innerHeight,points,markers};
            })()"""))
            var bitmap: Bitmap? = null
            val copied = CountDownLatch(1)
            var result = -1
            scenario.onActivity { activity ->
                val position = IntArray(2); web.getLocationInWindow(position)
                if (web.width > 0 && web.height > 0) {
                    bitmap = Bitmap.createBitmap(web.width, web.height, Bitmap.Config.ARGB_8888)
                    PixelCopy.request(activity.window, Rect(position[0], position[1], position[0]+web.width, position[1]+web.height), bitmap!!, { code -> result=code; copied.countDown() }, Handler(Looper.getMainLooper()))
                } else copied.countDown()
            }
            assertTrue("PixelCopy timeout: $name", copied.await((deadline-SystemClock.uptimeMillis()).coerceAtLeast(1), TimeUnit.MILLISECONDS))
            val frame = bitmap
            var valid = result == PixelCopy.SUCCESS && frame != null
            if (valid && frame != null) {
                val sx=frame.width/map.getDouble("width");val sy=frame.height/map.getDouble("height")
                valid = kotlin.math.abs(sx-sy)<0.05
                val points=map.getJSONArray("points")
                var checked=0;var mismatches=0;var right=0
                for(i in 0 until points.length()) {
                    val point=points.getJSONObject(i);val x=(point.getDouble("x")*sx).toInt().coerceIn(0,frame.width-1);val y=(point.getDouble("y")*sy).toInt().coerceIn(0,frame.height-1)
                    val pixel=frame.getPixel(x,y)
                    if(kotlin.math.abs(Color.red(pixel)-point.getInt("r"))>18||kotlin.math.abs(Color.green(pixel)-point.getInt("g"))>18||kotlin.math.abs(Color.blue(pixel)-point.getInt("b"))>18)mismatches++
                    checked++;if(x>frame.width*.65)right++
                }
                var hasText=false;val markers=map.getJSONArray("markers")
                for(i in 0 until markers.length()) {
                    val r=markers.getJSONObject(i);val colors=HashSet<Int>()
                    val left=(r.getDouble("left")*sx).toInt().coerceIn(0,frame.width-1);val top=(r.getDouble("top")*sy).toInt().coerceIn(0,frame.height-1)
                    val rightEdge=(r.getDouble("right")*sx).toInt().coerceIn(left+1,frame.width);val bottom=(r.getDouble("bottom")*sy).toInt().coerceIn(top+1,frame.height)
                    for(y in top until bottom step 2) for(x in left until rightEdge step 2)colors.add(frame.getPixel(x,y))
                    if(colors.size>12)hasText=true
                }
                valid=valid&&checked>=4&&right>=1&&mismatches==0&&hasText
                diagnostics="copy=$result size=${frame.width}x${frame.height} scale=$sx/$sy samples=$checked right=$right mismatches=$mismatches text=$hasText"
                File(directory,"capture-$name.json").writeText(map.toString())
                File(directory,"$name.png").outputStream().use { assertTrue("PNG write failed: $name",frame.compress(Bitmap.CompressFormat.PNG,100,it)) }
                frame.recycle()
            } else { diagnostics="copy=$result null=${frame==null}"; frame?.recycle() }
            consecutive=if(valid)consecutive+1 else 0
            File(directory,"capture-$name.txt").writeText(diagnostics)
            if(consecutive>=2) {
                // Retain whole-display keyboard/inset evidence separately from
                // the validated WebView-only crop; do not confuse the two.
                if(name=="keyboard") {
                    val display=instrumentation.uiAutomation.takeScreenshot()
                    assertNotNull("Missing IME display screenshot",display)
                    display!!.let { full ->
                        File(directory,"keyboard-display.png").outputStream().use { assertTrue("IME PNG write failed",full.compress(Bitmap.CompressFormat.PNG,100,it)) }
                        full.recycle()
                    }
                }
                return
            }
            Thread.sleep(100)
        }
        fail("No validated presented frame for $name: $diagnostics")
    }

    @After fun evidenceAndClose() {
        try {
            val directory = File(instrumentation.targetContext.filesDir, "evidence").apply { mkdirs() }
            File(directory, "phase.txt").writeText(phase)
            File(directory, "runtime.json").writeText(js("({userAgent:navigator.userAgent, width:innerWidth,height:innerHeight,scrollY,focused:document.activeElement?.id,focusedBounds:document.activeElement?.getBoundingClientRect().toJSON(),webview:${JSONObject.quote(WebView.getCurrentWebViewPackage()?.versionName ?: "unknown")}})"))
            capture("screen")
        } catch (error: Throwable) { android.util.Log.e("RustUiE2E", "Diagnostic capture unavailable", error) }
        // Closing the last Tauri Activity exits this instrumentation process.
        // The host force-stops the owned package after JUnit reports and evidence is collected.
    }
}
