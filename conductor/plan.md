# Implementation Plan: Bootstrap Light Theme Migration

## Objective
Convert the frontend UI to fully utilize Bootstrap 5 components and a Light theme. The project must function entirely offline, requiring all external assets (Bootstrap, Alpine.js, Chart.js) to be hosted locally. All previous styling frameworks (Bulma, Tailwind) will be removed.

## Key Files & Context
- **Assets:** `ilin/frontend/static/css/`, `ilin/frontend/static/js/`
- **Templates:** 
  - `ilin/frontend/templates/base.html`
  - `ilin/frontend/templates/admin.html`
  - `ilin/frontend/templates/chat.html`
  - `ilin/frontend/templates/login.html`
- **Current Styling:** Mixed Bulma, Tailwind via CDN, and custom CSS in `style.css`.

## Implementation Steps

### Phase 1: Localize External Assets
1. Download **Bootstrap 5 (minified CSS & JS)** and save to `ilin/frontend/static/css/bootstrap.min.css` and `ilin/frontend/static/js/bootstrap.bundle.min.js`.
2. Download **Alpine.js** and save to `ilin/frontend/static/js/alpine.min.js`.
3. Download **Chart.js** and save to `ilin/frontend/static/js/chart.min.js`.

### Phase 2: Template Refactoring & Light Theme Enforcements
1. **`base.html`**:
   - Remove CDN links for Bulma and Tailwind.
   - Add local links for Bootstrap CSS, Bootstrap JS, Alpine.js, and Chart.js.
   - Remove `is-dark-mode` from body and ensure standard Bootstrap background/text colors are used (Light theme by default).
2. **`style.css`**:
   - Strip all dark mode variables (`--bg-card: #1a1c23`, etc.).
   - Remove custom UI components (`.card`, `.btn`) as they are replaced by Bootstrap equivalents.
   - Keep only necessary custom layout classes that Bootstrap grid doesn't easily cover (e.g., `.chat-layout`).

### Phase 3: Bootstrap Component Integration
1. **`login.html`**: Replace Tailwind/Bulma grid/form classes with Bootstrap `.container`, `.card`, `.form-control`, `.btn-primary`.
2. **`chat.html`**: Update chat bubbles, sidebars, and input areas using Bootstrap flexbox utilities and `.form-control`.
3. **`admin.html`**: Convert existing tables, modals, and metric cards to Bootstrap equivalents (`.table`, `.modal`, `.card`). Ensure responsiveness using the Bootstrap grid (`.row`, `.col-md-X`).

## Verification & Testing
- Start the FastAPI server locally.
- Disconnect from the internet and verify that the application still loads correctly (no missing asset 404s).
- Verify the UI across all pages (Login, Admin Dashboard, Chat) displays the new light theme and Bootstrap styling correctly.
- Test UI responsiveness on both desktop and mobile views.
- Ensure Alpine.js interactivity and Chart.js rendering still function smoothly.