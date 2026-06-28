# FRIDAY Design System — Internal UI Safety Rules

**Use this before any visual change.** FRIDAY is the dark Automation Hub aesthetic (Linear/Vercel-inspired slate + coral accent).

## Palette

| Role | Value | Usage |
|------|-------|--------|
| Background | `#0B0F19` | Page base |
| Surface | `#111827` | Inputs, empty states |
| Card | `#151C2F` | Panels, cards, metrics |
| Border | `#1F2937` / `#2A3144` | Card & input borders |
| Text primary | `#FFFFFF` / `#E8EAEF` | Headings, body |
| Text muted | `#8B93A7` / `#6B7280` | Captions, meta |
| Accent | `#FF6D5A` → `#FF8F7A` | Primary buttons, highlights |
| Success | `#34D399` | Running, valid JSON |
| Warning | `#FBBF24` | Starting, partial state |
| Neutral | `#9CA3AF` | Stopped, inactive |
| Error | `#F87171` | Failures only (not “stopped”) |

## Typography

- **UI:** Inter (400–700)
- **Code / logs:** JetBrains Mono
- Section titles: `#####` markdown or `.section-card h3` (~1.1rem, semibold)
- Captions: 0.75–0.85rem, muted color

## Components (reuse — do not reinvent)

| Pattern | CSS class | When |
|---------|-----------|------|
| Page section intro | `section_header()` → `.section-card` | Page tops |
| Hub panel block | `.hub-panel` | Generator, Docker sub-sections |
| Status pill | `.status-pill` + `.ok` / `.warn` / `.neutral` / `.err` | Sidebar, header |
| Empty state | `empty_state()` → `.empty-state` | No data |
| KPI row | `kpi_cards()` → `.kpi-card` | Stats |
| Template tile | `.template-tile` | Ready-made templates |
| History row | `.history-item` | Workflow history |

## Buttons

- **Primary** (`type="primary"`): one main action per area — Generate, Push, Start n8n
- **Secondary** (default): Format JSON, Copy, View, Cancel, Delete
- Global styles in `CUSTOM_CSS` — no inline button CSS unless unavoidable (FAB)

## Spacing

- Card padding: `1.25rem–1.75rem`
- Card radius: `12–14px`
- Section gap: `1.25rem` margin-bottom
- Pill padding: `6px 12px` (header), `8px 14px` (sidebar)

## Rules

1. Do not break the dark theme or introduce new accent colors.
2. Prefer existing classes over new CSS.
3. Stopped ≠ error — use **neutral gray**, not red.
4. Keep animations subtle (opacity pulse only).
5. When in doubt, simplify — remove extra shadows and borders.
