# Design: Gemma 4 MTP Speed Comparison

## Style Prompt

Technical but readable benchmark explainer. The video should feel like a precise local-lab readout rather than a marketing reel: dark ink canvas, teal as the verified-speed accent, copper as the baseline/wait-time accent, and pale blue-gray text. Motion should make speed tangible through race bars, numeric counters, and task-fit contrast. Use restrained depth, thin grid lines, and data labels that stay readable at 1080p.

## Colors

- Background: `#101418`
- Panel: `#171d24`
- Foreground: `#edf2f7`
- Muted text: `#aeb9c5`
- Line: `#2a3440`
- MTP accent: `#33c9bd`
- Baseline accent: `#fb923c`
- Caution accent: `#f6c85f`

## Typography

- Display: `Fraunces`, fallback serif
- Data and UI: `IBM Plex Mono`, fallback monospace
- Japanese/system fallback: `Hiragino Sans`, `Yu Gothic`, sans-serif

## Motion

- Medium-energy technical motion.
- Use push-wipe transitions between scenes.
- Animate bars by `scaleX`, not width.
- Numbers should snap into place with tabular numeric styling.
- Persistent grid/decorative elements can breathe or drift slowly, but repeat counts must be finite.

## What NOT to Do

- Do not use neon cyberpunk colors or purple-blue gradients.
- Do not make every scene a card grid.
- Do not hide the caveat that MTP can be flat or slower on open-ended prompts.
- Do not use tiny table text; the video should work without pausing.
