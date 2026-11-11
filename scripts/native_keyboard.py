"""Real WebDriver key input with bounded, read-only DOM observations."""
import json
import time
from pathlib import Path

TAB, SHIFT, CONTROL, ENTER, SPACE = '\ue004', '\ue008', '\ue009', '\ue007', '\ue00d'
HOME, DOWN = '\ue011', '\ue015'
RELEASE_TIMEOUT = 3

# Whitelist diagnostic fields; never serialize DOM, arbitrary attributes or input data.
FOCUS = """return (() => {const e=document.activeElement,r=e.getBoundingClientRect(),s=getComputedStyle(e);return {
 tag:e.tagName,id:e.id.slice(0,100),href:e.getAttribute('href')?.slice(0,200),label:(e.getAttribute('aria-label')||e.textContent||'').trim().slice(0,100),
 rect:{x:r.x,y:r.y,width:r.width,height:r.height},visible:r.width>0&&r.height>0&&r.top>=0&&r.left>=0&&r.bottom<=innerHeight&&r.right<=innerWidth,
 focus_visible:e.matches(':focus-visible'),outline:{style:s.outlineStyle,width:s.outlineWidth,color:s.outlineColor}}})()"""


class Keyboard:
    def __init__(self, request, prefix, execute, wait, artifact_prefix):
        self.request, self.prefix, self._execute, self.wait = request, prefix, execute, wait
        self.deadline = None
        self.path = Path('artifacts')/(artifact_prefix+'-keyboard.json')
        self.artifact_prefix = artifact_prefix
        self.report = dict(schema_version=1, input_mechanism='WebDriver W3C key actions',
                           passed_checkpoints=[], current_checkpoint=None, failed_checkpoint=None,
                           focus_trace=[], status='running', failure_summary=None,
                           manual_keyboard_verified=False, orca_verified=False)

    def save(self):
        try:
            self.path.write_text(json.dumps(self.report, indent=2)+'\n')
        except Exception as error:
            # Diagnostic failure must not mask an input/assertion failure.
            print('Keyboard artifact unavailable:', type(error).__name__)

    def timeout(self):
        if self.deadline is None:
            return 40
        remaining = self.deadline-time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Focus traversal deadline expired')
        return remaining

    def execute(self, script):
        return self._execute(script, timeout=self.timeout())

    def keys(self, *values):
        actions = []
        for value in values:
            actions.extend([{'type':'keyDown','value':value}, {'type':'keyUp','value':value}])
        self.request('POST', self.prefix+'/actions', {'actions':[{'type':'key','id':'keyboard','actions':actions}]}, timeout=self.timeout())

    def chord(self, modifier, value):
        self.request('POST', self.prefix+'/actions', {'actions':[{'type':'key','id':'keyboard','actions':[
            {'type':'keyDown','value':modifier}, {'type':'keyDown','value':value},
            {'type':'keyUp','value':value}, {'type':'keyUp','value':modifier}]}]}, timeout=self.timeout())

    def observe(self):
        row = self.execute(FOCUS)
        self.report['focus_trace'].append(row)
        self.report['focus_trace'] = self.report['focus_trace'][-240:]
        self.save()
        return row

    def matches(self, selector):
        return self.execute('return document.activeElement.matches('+json.dumps(selector)+')')

    def reach(self, selector, reverse=False):
        self.deadline = time.monotonic()+15
        trace = []
        try:
            for step in range(41):
                row = self.observe(); trace.append(row)
                if self.matches(selector):
                    assert row['visible'], f'Focused target outside viewport: {row}'
                    return row
                if step == 40 or time.monotonic() >= self.deadline:
                    break
                if reverse:
                    self.chord(SHIFT, TAB)
                else:
                    self.keys(TAB)
            raise AssertionError(f'Focus target unreachable: {selector}; last focus={trace[-1]}; trace={trace}')
        except TimeoutError as error:
            raise AssertionError(f'Focus deadline exceeded: target={selector}; last focus={trace[-1] if trace else None}; trace={trace}') from error
        finally:
            self.deadline = None

    def checkpoint(self, name, operation):
        self.report['current_checkpoint'] = name; self.save()
        operation()
        self.report['passed_checkpoints'].append(name); self.save()

    def outlined(self, name):
        row = self.observe()
        assert row['visible'] and row['focus_visible'], row
        outline = row['outline']
        assert outline['style'] not in ('none','hidden') and float(outline['width'].removesuffix('px')) > 0 and outline['color'] not in ('transparent','rgba(0, 0, 0, 0)'), row
        import base64
        Path('artifacts', self.artifact_prefix+'-keyboard-'+name+'.png').write_bytes(
            base64.b64decode(self.request('GET', self.prefix+'/screenshot')))

    def run(self):
        original = None
        started = time.monotonic()
        try:
            self.report['viewport'] = self.execute('return {width:innerWidth,height:innerHeight,dpr:devicePixelRatio}')
            self.checkpoint('fresh-window-skip-link', self.skip)
            self.checkpoint('library-launch', self.launch)
            self.checkpoint('request-freshness', self.freshness)
            self.checkpoint('reverse-adjacent-tab', self.reverse)
            self.checkpoint('cancel', self.cancel)
            self.checkpoint('palette-navigation-and-persistence', self.palette)
            self.report['status'] = 'passed'
        except BaseException as error:
            original = error
            self.report.update(status='failed', failed_checkpoint=self.report['current_checkpoint'],
                               failure_summary=f'{type(error).__name__}: {str(error)[:1500]}')
            raise
        finally:
            try:
                self.request('DELETE', self.prefix+'/actions', timeout=RELEASE_TIMEOUT)
            except Exception as error:
                if original is None:
                    self.report.update(status='failed', failed_checkpoint='release-actions', failure_summary=str(error)[:1500])
                    self.save()
                    raise
                print('Key release failed after original error:', type(error).__name__)
            finally:
                self.report['elapsed_seconds'] = time.monotonic()-started
                self.save()

    def skip(self):
        route = self.execute('return location.hash')
        self.observe()  # Record fresh focus; do not assume a first tab stop.
        self.reach('a[href="#workspace-content"]')
        self.outlined('skip-link')
        self.keys(ENTER)
        assert self.matches('#workspace-content')
        assert self.execute('return location.hash') == route

    def launch(self):
        self.reach('a[data-testid="launch-example"]')
        self.keys(ENTER)
        self.wait("document.querySelector('h1')?.textContent === 'Latest response'")
        self.reach('#number')
        self.outlined('number')

    def number(self, value, reverse=False):
        self.reach('#number', reverse=reverse); self.chord(CONTROL, 'a'); self.keys(*str(value))
        assert self.execute("return document.querySelector('#number').value") == str(value)

    def button(self, name):
        # Existing semantic classes/text; no DOM writes or synthetic events.
        self.reach('button'+{'Slow request':'.primary-action:first-child', 'Fast request':'.primary-action:nth-child(2)', 'Cancel':'.secondary-action'}[name])
        assert self.execute('return document.activeElement.textContent') == name

    def freshness(self):
        self.number(11); self.button('Slow request')
        slow_started = time.monotonic()
        self.keys(ENTER)
        self.wait("document.querySelector('[role=status]')?.textContent.includes('Request pending.')")
        self.number(22, reverse=True); self.button('Fast request')
        assert self.execute("return document.querySelector('[role=status]').textContent.includes('Request pending.')"), 'Slow request completed before Fast activation'
        self.keys(SPACE)
        self.report['freshness_timing'] = {'slow_to_fast_seconds': time.monotonic()-slow_started, 'slow_delay_seconds':1.5, 'fast_delay_seconds':.15, 'slow_pending_before_fast':True}
        self.wait("document.querySelector('[role=status]')?.textContent.includes('Latest result: 22')")
        latest_observed = time.monotonic()-slow_started
        self.report['freshness_timing']['latest22_observed_seconds'] = latest_observed
        assert latest_observed < 1.5, f'Fast result arrived after original slow deadline: {latest_observed}'
        time.sleep(1.7)
        self.wait("document.querySelector('[role=status]')?.textContent.includes('Latest result: 22') && !document.querySelector('[role=status]')?.textContent.includes('Request pending.')")

    def reverse(self):
        self.button('Fast request'); self.chord(SHIFT, TAB)
        assert self.matches('button.primary-action:first-child'), self.observe()
        assert self.execute('return document.activeElement.textContent') == 'Slow request'
        self.observe()

    def cancel(self):
        self.keys(ENTER)
        self.wait("document.querySelector('[role=status]')?.textContent.includes('Request pending.')")
        self.button('Cancel'); self.keys(ENTER)
        self.wait("document.querySelector('[role=status]')?.textContent.includes('Request cancelled.') && !document.querySelector('[role=status]')?.textContent.includes('Request pending.')")
        cancelled = self.execute("return document.querySelector('[role=status]').textContent")
        time.sleep(1.7)
        assert self.execute("return document.querySelector('[role=status]').textContent") == cancelled

    def navigate(self, route):
        self.reach('nav[aria-label="Main navigation"] a[href="'+route+'"]')
        self.keys(ENTER)

    def palette(self):
        self.navigate('#/settings'); self.reach('#color-scheme')
        self.keys(HOME, DOWN, ENTER)
        self.wait("document.querySelector('[data-palette]')?.dataset.palette === 'signal-blue'")
        self.navigate('#/overview')
        self.wait("document.querySelector('h1')?.textContent === 'Your library'")
        assert self.execute("return document.querySelector('[data-palette]').dataset.palette") == 'signal-blue'
        # Restore through the same real select for the existing Nocturne checks.
        self.navigate('#/settings'); self.reach('#color-scheme'); self.keys(HOME, ENTER)
        self.wait("document.querySelector('[data-palette]')?.dataset.palette === 'nocturne'")
        self.navigate('#/overview')
        self.wait("document.querySelector('h1')?.textContent === 'Your library'")
