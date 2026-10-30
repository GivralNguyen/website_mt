#!/usr/bin/env python3
"""Browser accessibility regression checks. Requires playwright and an axe-core bundle.

Start a local server, then run:
  python tests/accessibility.py --axe /path/to/axe.min.js
"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', default='http://127.0.0.1:8765/')
parser.add_argument('--browser', default='/usr/bin/chromium')
parser.add_argument('--axe', required=True)
parser.add_argument('--report', default='/tmp/website-accessibility-results.json')
args = parser.parse_args()
results = []
errors = []


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def settle(page):
    page.wait_for_function("!document.body.classList.contains('is-preload')")
    page.wait_for_timeout(400)


def layout(page, label):
    geometry = page.evaluate('''() => ({
        width: innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
        clipped: [...document.querySelectorAll('a, button, h1, h2, h3, p, li, dt, dd')]
            .filter(e => e.getClientRects().length && !e.closest('.sr-only'))
            .filter(e => { const s = getComputedStyle(e); return ['hidden', 'clip'].includes(s.overflowY) && e.scrollHeight > e.clientHeight + 2; })
            .map(e => e.outerHTML.slice(0, 180))
    })''')
    check(geometry['scrollWidth'] <= geometry['width'] + 1, f'{label}: horizontal overflow {geometry}')
    check(not geometry['clipped'], f'{label}: clipped content {geometry["clipped"]}')
    results.append({'check': label, 'layout': 'pass'})
    print(label + ': layout passed', flush=True)


def axe(page, label):
    page.add_script_tag(path=args.axe)
    result = page.evaluate('''async () => {
        const result = await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']}});
        const summarize = entries => entries.map(v => ({id: v.id, impact: v.impact, nodes: v.nodes.map(n => ({target: n.target, summary: n.failureSummary}))}));
        return {version: result.testEngine.version, violations: summarize(result.violations), incomplete: summarize(result.incomplete), passes: result.passes.length};
    }''')
    results.append({'check': label, 'axe': result})
    print(label, 'violations:', len(result['violations']), 'manual review:', len(result['incomplete']), flush=True)
    check(not result['violations'], f'{label}: axe violations: {json.dumps(result["violations"])}')


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=args.browser, headless=True)
    context = browser.new_context(viewport={'width': 1280, 'height': 900}, reduced_motion='reduce')
    # The site uses local/sans-serif fonts; avoid unrelated third-party network delays.
    context.route('https://fonts.googleapis.com/**', lambda route: route.abort())
    page = context.new_page()
    page.on('pageerror', lambda error: errors.append(str(error)))
    for width in (1280, 320):
        page.set_viewport_size({'width': width, 'height': 900})
        for route in ('', 'welcome_', 'research_', 'teaching_', 'publication_'):
            page.goto(args.url + ('#' + route if route else ''))
            settle(page)
            label = f'{route or "home"} at {width}px'
            layout(page, label)
            axe(page, label)
            if route == 'publication_':
                page.wait_for_function("document.querySelector('#pub-filter-year').disabled === false")
                for group in ('category', 'topic'):
                    page.locator('#pub-filter-' + group).click()
                    layout(page, label + ' ' + group)
                    axe(page, label + ' ' + group)
            page.add_style_tag(content='* {line-height: 1.5 !important; letter-spacing: 0.12em !important; word-spacing: 0.16em !important;} p {margin-bottom: 2em !important;}')
            layout(page, label + ' with WCAG text spacing')
    # Real keyboard input: skip, native controls, result announcements, and closing.
    page.set_viewport_size({'width': 1280, 'height': 900})
    page.goto(args.url)
    settle(page)
    page.keyboard.press('Tab')
    check(page.locator('.skip-link').evaluate('(e) => e === document.activeElement'), 'Skip link must be first')
    page.keyboard.press('Enter')
    check(page.locator('#welcome_').evaluate('(e) => e === document.activeElement'), 'Skip must focus visible main content')
    page.keyboard.press('Tab')
    check(page.locator('#welcome_ .close').evaluate('(e) => e === document.activeElement'), 'Close must be the first section control')
    page.keyboard.press('Space')
    check(page.locator('nav a[href="#welcome_"]').evaluate('(e) => e === document.activeElement'), 'Close must restore focus')
    for _ in range(3):
        page.keyboard.press('Tab')
    page.keyboard.press('Enter')
    page.wait_for_function("document.activeElement.id === 'publication_'")
    page.keyboard.press('Tab')
    page.keyboard.press('Tab')
    check(page.locator('#pub-filter-category').evaluate('(e) => e === document.activeElement'), 'Grouping must follow Close')
    page.keyboard.press('Space')
    check(page.locator('#pub-filter-category').get_attribute('aria-pressed') == 'true', 'Space must select category')
    check('grouped by category' in page.locator('#publication-status').inner_text(), 'Grouping result must be announced')
    check(page.locator('#pub-filter-category').evaluate('(e) => e === document.activeElement'), 'Grouping must retain focus')
    page.keyboard.press('Tab')
    page.keyboard.press('Enter')
    check(page.locator('#pub-filter-year').get_attribute('aria-pressed') == 'true', 'Enter must select year')
    page.keyboard.press('Escape')
    check(page.locator('nav a[href="#publication_"]').evaluate('(e) => e === document.activeElement'), 'Escape must restore focus')
    results.append({'check': 'Keyboard skip, grouping, close, Escape and focus restoration', 'result': 'pass'})
    # Invalid fragments and rapid/back/forward navigation must never strand focus.
    for fragment in ('%ZZ', '[', 'research_', 'teaching_', 'publication_', 'welcome_', 'research'):
        page.evaluate('(hash) => { location.hash = hash; }', fragment)
        page.wait_for_timeout(20)
    page.wait_for_timeout(500)
    check(page.locator('#main > article:visible').count() == 1, 'Only one article may remain visible')
    check(page.locator('#research_').is_visible(), 'Nested fragments must expose containing article')
    page.go_back()
    page.wait_for_function("document.activeElement.id === 'welcome_'")
    page.go_forward()
    page.wait_for_function("document.activeElement.id === 'research'")
    results.append({'check': 'Malformed/nested fragments, rapid navigation and history', 'result': 'pass'})
    # Double each computed text size to emulate text-only enlargement, including px rules.
    for route in ('', 'welcome_', 'research_', 'teaching_', 'publication_'):
        page.goto(args.url + ('#' + route if route else ''))
        settle(page)
        page.evaluate('''() => {
            const elements = [...document.querySelectorAll('body, body *')];
            const sizes = elements.map(e => parseFloat(getComputedStyle(e).fontSize));
            elements.forEach((e, i) => e.style.setProperty('font-size', sizes[i] * 2 + 'px', 'important'));
        }''')
        layout(page, (route or 'home') + ' at 200% text size')
    page.emulate_media(forced_colors='active')
    page.goto(args.url + '#publication_')
    settle(page)
    check(page.locator('#publication_ .close').inner_text() == 'Close', 'Close needs visible text in forced colors')
    layout(page, 'Windows forced colors')
    page.emulate_media(forced_colors='none')
    # Loading errors and empty data have named, announced feedback and no dead controls.
    for payload in ('error', ''):
        def response(route, payload=payload):
            route.fulfill(status=503 if payload == 'error' else 200, body='')
        page.route('**/input.txt', response)
        page.goto(args.url + '?a11y-response=' + (payload or 'empty') + '#publication_')
        settle(page)
        page.wait_for_function("document.querySelector('#publication-status').textContent.includes('could not be loaded')")
        check(page.locator('#crumbs button:disabled').count() == 3, 'Unavailable grouping controls must be disabled')
        check(page.locator('#publication-status').get_attribute('role') == 'status', 'Loading failures must be announced')
        axe(page, 'Publication ' + (payload or 'empty response'))
        page.unroute('**/input.txt', response)
    check(not errors, 'JavaScript errors: ' + str(errors))
    context.close()
    nojs = browser.new_context(java_script_enabled=False, viewport={'width': 320, 'height': 900})
    nojs.route('https://fonts.googleapis.com/**', lambda route: route.abort())
    page = nojs.new_page()
    page.goto(args.url)
    check(page.locator('#main > article:visible').count() == 4, 'All sections must be readable without JavaScript')
    check(page.locator('#publication_ noscript').inner_text().strip() == 'Please enable JavaScript to view and group publications.', 'Explain the JavaScript requirement')
    layout(page, 'No JavaScript at 320px')
    nojs.close()
    browser.close()

Path(args.report).write_text(json.dumps(results, indent=2))
print(f'PASS: {len(results)} checks; report: {args.report}')
