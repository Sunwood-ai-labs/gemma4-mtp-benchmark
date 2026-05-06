# Design: Gemma 4 and DFlash Experiment Slides

## Style Prompt

Professional Japanese benchmark briefing for a technical audience. The slides should feel like a polished internal research deck: dark lab canvas, precise data typography, restrained teal for verified speed, copper for baseline or slowdown, and amber for caveats. Layouts should be dense enough for engineering review but visually calm, with clear hierarchy, large Japanese headlines, and chart-first storytelling. Use thin rules, terminal-style labels, benchmark tables, and acceptance-length diagrams. The mood is analytical, confident, and honest about negative results.

## Colors

- Background: `#101418`
- Panel: `#171d24`
- Foreground: `#edf2f7`
- Muted text: `#aeb9c5`
- Line: `#2a3440`
- Speed accent: `#33c9bd`
- Baseline accent: `#fb923c`
- Caveat accent: `#f6c85f`
- Deep ink: `#0b0f13`

## Typography

- Japanese display: `Hiragino Mincho ProN`, `Yu Mincho`, serif
- Japanese body: `Hiragino Sans`, `Yu Gothic`, sans-serif
- Data and commands: `IBM Plex Mono`, `SFMono-Regular`, monospace

## Motion

- Each slide enters with staggered title, chart, and note motion.
- Use fast horizontal wipe transitions between slides.
- Animate bars by `scaleX`.
- Keep chart labels stable and readable at 1080p.
- No infinite repeats.

## What NOT to Do

- Do not imply DFlash was universally faster.
- Do not hide the Gemma 4 31B negative result.
- Do not use marketing-style hero imagery.
- Do not use purple-blue gradients or decorative orbs.
- Do not make the slides a wall of tiny table text.
