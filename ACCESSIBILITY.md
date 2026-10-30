# Accessibility audit — October 30, 2026

The accessibility issues identified in this local audit have been fixed. This is not a certification of ADA compliance or a claim that every WCAG success criterion has been independently verified. Full WCAG 2.1 AA conformance requires meeting every applicable A and AA criterion across the complete experience; automated tests alone cannot establish that.

Scope: `index.html`, its home screen and four section views, all three publication groupings, and the local CSS, JavaScript, portrait, and publication data. External websites and linked publications were not audited. Changes are local and have not been deployed.

## Fixes

- **Structure and relationships (1.3.1):** Converted 164 visually bulleted entries to real list items and made contact, service, and course group labels headings. Added descriptive article names.
- **Text resizing, reflow, and spacing (1.4.4, 1.4.10, 1.4.12):** Removed fixed-height controls, conflicting line heights, excessive publication indents, and absolute vertical positioning that could clip the home screen. Narrow layouts stack their columns, text wraps, and font sizing respects the browser's default size.
- **Keyboard and focus (2.1.1, 2.1.2, 2.4.1, 2.4.3, 2.4.7):** Native Close and grouping buttons, a working skip link, deterministic section changes, focus restoration on Close/Escape, and visible focus rings. Malformed and nested URL fragments no longer break navigation.
- **Page identification and controls (2.4.2, 4.1.2):** Section-specific document titles, named sections, native button behavior, and an exposed selected grouping state.
- **Status messages (4.1.3):** A separate live status announces publication loading, grouping results, and errors without reading the entire publication collection. Successful grouping messages are visually hidden while remaining available to screen readers; loading and error messages stay visible. Controls remain disabled when data is unavailable.
- **Non-text contrast (1.4.11):** Focused navigation links have an opaque dark backing. Selected grouping has an underline as well as a color change. Forced-colors mode retains visible Close text and focus indicators.
- **JavaScript availability:** The plain-text publication link was removed at the owner’s request. Publications require JavaScript; when it is disabled, an explanatory message appears. Other section content remains visible, and publication loading failures receive an announced error with reload instructions.

## Verification

Chromium with Playwright 1.64.1 and axe-core 4.10.2 completed **49 regression checks**, including **16 WCAG 2.1 A/AA scans with zero violations**.

Coverage includes:

- Home, Welcome, Research, Teaching, and Publications at 1280px and 320px widths; publications grouped by year, category, and topic.
- 320 CSS-pixel reflow, equivalent to the available width at 400% zoom on a 1280px viewport. This checks layout; it is not an actual browser-zoom test.
- WCAG text-spacing overrides and simulated 200% text-only enlargement, including text originally sized in pixels.
- Keyboard activation with Tab, Enter, Space, and Escape; focus retention/restoration; malformed fragments, nested fragments, rapid navigation, and browser history.
- Publication fetch failure and empty responses, forced-colors layout, and the 320px layout with JavaScript disabled.
- HTML tag nesting, duplicate IDs, list structure, visible content preservation, and whitespace checks.

Axe reported incomplete **color-contrast** checks where backgrounds contain images. These were reviewed separately using the CSS compositing bounds and rendered screenshots: white text on the home content panel is at least **6.19:1**, white article text **13.57:1**, the red research link **4.89:1**, black selected-group text **6.19:1**, and the focused-navigation yellow ring against its backing **12.20:1**. The 2px heading-divider images sit below the text, separated by padding. Contrast must be rechecked if colors, opacity, or imagery change.

No audio/video, forms, time limits, flashing content, or complex pointer gestures were found in the audited content. An actual screen-reader review (for example NVDA/Firefox and VoiceOver/Safari), additional browser/device checks, and an audit of any externally hosted documents are still needed before making a full conformance claim.

## Running the regression checks

Use an environment with Python, `playwright==1.64.1`, Chromium, and an axe-core 4.10.2 `axe.min.js` bundle. No browser or test dependency is added to the website runtime.

From this directory, start the preview in one terminal:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Then run in another terminal:

```sh
python tests/accessibility.py --axe /absolute/path/to/axe.min.js
```

Use `--browser` for a different Chromium executable, `--url` for a different local port, or `--report` to choose the JSON report path. The default report is `/tmp/website-accessibility-results.json`. The test blocks the unused remote Google Fonts stylesheet to keep results independent of third-party network availability; local fonts and assets remain enabled.

References: [WCAG 2.1 conformance requirements](https://www.w3.org/TR/WCAG21/#conformance-reqs) and [U.S. Department of Justice guidance on web accessibility and the ADA](https://www.ada.gov/resources/web-guidance/).
