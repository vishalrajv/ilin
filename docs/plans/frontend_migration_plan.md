# Implementation Plan: Frontend & Reactivity Migration

**Objective:** Modernize the ILIN frontend by migrating from custom CSS and vanilla JS to a tech stack featuring Bulma CSS, Tailwind CSS, Alpine.js, and Chart.js, while preserving the existing FastAPI backend and authentication logic.

---

### **Phase 1: Infrastructure & Shared Components**
*   **Task 1.1: Project Structure Update**
    *   Create `docs/plans/` directory in the project root.
    *   Move this plan into the new `docs/plans/` directory.
*   **Task 1.2: Base Template Refactor (`base.html`)**
    *   Add CDNs for **Bulma CSS**, **Tailwind CSS** (via Play CDN for dev), **Alpine.js**, and **Chart.js**.
    *   Standardize the HTML shell with a high-contrast "Intelligence" color palette.
    *   Define global Tailwind `@layer base` styles if needed for standard typography.

---

### **Phase 2: Authentication UI Migration**
*   **Task 2.1: Login Page Update (`login.html`)**
    *   Replace custom `.login-container` and `.card` with Bulma's `hero` and `card` components.
    *   Apply Tailwind utility classes for precise spacing and mobile responsiveness.
    *   Refactor form submission to use Alpine.js `x-data` for error handling and loading states.

---

### **Phase 3: Chat Interface & Reactivity Migration**
*   **Task 3.1: Chat Layout Refactor (`chat.html`)**
    *   Use Bulma’s `columns` system for the sidebar/main-content layout.
    *   Implement Alpine.js `x-data` to manage UI state (current section, topic list, chat messages).
*   **Task 3.2: Message Streaming Migration (`chat.js` to Alpine)**
    *   Port the SSE (Server-Sent Events) streaming logic into an Alpine component.
    *   Use Alpine's `x-for` to render messages and sources dynamically.
    *   Improve message bubble aesthetics using Tailwind utilities (rounded corners, subtle gradients).

---

### **Phase 4: Admin Dashboard & Analytics Integration**
*   **Task 4.1: Admin Layout Refactor (`admin.html`)**
    *   Use Bulma tabs for "Topics" and "Users" navigation.
    *   Refactor modals (Create Topic, Create User) using Alpine.js `x-show` and `@click.away`.
*   **Task 4.2: Data Visualization (Chart.js)**
    *   Integrate Chart.js on the Admin homepage.
    *   Add a chart showing **"Document Distribution by Topic"** to provide immediate system insight.
*   **Task 4.3: Table & List Modernization**
    *   Use Bulma’s `table` component for the user list.
    *   Implement "empty state" illustrations using Tailwind.

---

### **Phase 5: Refinement & Cleanup**
*   **Task 5.1: Style Consolidation (`style.css`)**
    *   Identify and remove custom CSS rules now handled by Bulma/Tailwind.
    *   Refine custom "Deep Intelligence" theme (dark mode optimizations, glassmorphism effects).
*   **Task 5.2: Final Verification**
    *   Test all responsive breakpoints (Mobile/Tablet/Desktop).
    *   Verify chat streaming performance and error handling.

---

### **Verification & Testing**
1.  **UI Consistency:** Ensure all buttons, forms, and cards follow the new Bulma/Tailwind design tokens.
2.  **Reactivity:** Verify that Alpine.js handles modal toggles and section switching without page reloads.
3.  **Data Integrity:** Confirm that Chat and Admin API calls still work correctly with the existing backend.
4.  **Performance:** Check page load times and Chart.js rendering efficiency.
