# TalentScope design audit

**Audit date:** 2026-10-11
**Scope:** public routes, B2C workspace, B2B workspace, shared layout and interaction primitives.

## Executive summary

TalentScope already has a strong functional skeleton: the routes are clear, the API state model is explicit, the brand color is consistent, and the most important forms have labels and keyboard affordances. The product currently feels like a well-structured internal tool rather than a premium AI product because the visual language stops at rounded white cards, generic badges, and isolated hover effects. The redesign should make the product feel like a calm, high-signal workspace: darker navigation chrome, richer page headers, fewer but more intentional surfaces, and motion that communicates progress.

The current app was rendered in-browser for the public landing and authentication routes. Protected routes were audited from their complete route components, including loading, empty, error, and success branches; they require an authenticated API session to render real data.

## What already works

- The information architecture is easy to understand: public marketing, individual workspace, and organization workspace are separated cleanly.
- React Router route boundaries and the `ProtectedRoute` model keep account-specific pages scoped.
- Primary actions are generally visible near the top of each page: analyze, create batch, export, and settings actions are not hidden.
- Forms use real labels, native inputs, semantic buttons, and `role="alert"`/`role="status"` in important feedback states.
- Loading and error branches exist on data-heavy pages instead of relying on blank screens.
- The brand color `#4F46E5` is recognizable and already has a useful supporting indigo scale.
- The landing page communicates the product promise quickly and includes an understandable preview of an ATS result.

## Page and component audit

### Public pages

#### Landing (`LandingPage`)

- **Hierarchy:** The headline and CTA are clear. The right-side analysis preview competes slightly with the headline because it has similar visual weight.
- **Spacing/rhythm:** Generous section spacing works, but the page alternates between large white bands and large pale bands without enough connective rhythm.
- **Typography:** The display headline is strong; supporting copy and section headings are closer to default SaaS styling than an editorial premium system.
- **Color:** Indigo is used as both signal and decoration. The gradient preview and multiple pastel accents dilute the sense of a focused brand.
- **Interaction/motion:** There are several hover and entrance classes, but the motion feels attached to components rather than to a narrative. The preview floats continuously without explaining anything.
- **States/mobile:** Marketing states are complete. On small screens the header hides navigation correctly, but the first viewport is dominated by the hero without a compact proof point or product signal.
- **Accessibility/consistency:** Good semantic headings and links. Decorative animation needs a calmer reduced-motion fallback and links should not receive global underlines when they are navigation controls.

#### Login and Register (`LoginPage`, `RegisterPage`)

- **Hierarchy:** Clear form-first structure and a helpful split layout at desktop widths.
- **Spacing/rhythm:** Balanced, but the visual panel is mostly a gradient with text; it feels generic and does not reinforce what the product actually does.
- **Typography/color:** Readable and consistent, but the left panel uses a large gradient block where a more distinctive data motif would create memory.
- **Interaction:** Inputs and submission states work, yet invalid state is only expressed after submit and there is no password affordance or field-level guidance.
- **Mobile/accessibility:** The mobile form remains usable and labels are present. The account type toggle needs stronger selected-state semantics and a clearer focus treatment.

#### Not found (`NotFoundPage`)

- **Hierarchy:** Clear and centered.
- **Weakness:** The oversized “404” is visually familiar but generic; the page misses a reassuring route back into the product and does not share the new workspace tone.

### B2C workspace

#### Dashboard (`B2CDashboardPage`)

- **Hierarchy:** The “next best action” banner is useful, but it reads as a large static rectangle above stats rather than a guided starting point.
- **Spacing/rhythm:** Repeated rounded cards create a uniform grid with no dominant metric or visual anchor.
- **Data states:** Loading skeletons and no-history state exist. The error state is too terse and offers no retry action.
- **Interaction:** Recent rows have a hover state but no meaningful destination; activity should make the next action obvious.
- **Mobile:** The stat grid collapses well, but the hero CTA and activity row need stronger stacking and scanability.

#### Analyze (`AnalyzeResumePage`)

- **Hierarchy:** The two-step flow is one of the stronger pages. Upload and job description are easy to find.
- **Weakness:** The drop zone, tips card, action bar, loading panel, and result card are all competing bordered surfaces. The result reveal is not yet a signature moment.
- **Interaction/motion:** Drag feedback and skeleton loading are good foundations. The score reveal should be staged: completion, score, then breakdown.
- **Accessibility:** The upload region is keyboard reachable. It should expose clearer status text and keep motion optional.

#### History (`HistoryPage`)

- **Hierarchy:** Filters are clear; the list is understandable.
- **Weakness:** Rows lack a strong score visual and the expanded details feel like an implementation detail rather than a useful summary.
- **Empty/error:** Both are present, but the empty state uses emoji and a generic icon treatment that does not match a premium product.
- **Mobile:** The two-column row becomes a stack, but secondary information is still dense on narrow widths.

#### Settings (`SettingsPage`)

- **Hierarchy:** Sections are logically grouped.
- **Weakness:** Three identical cards flatten the page and the “security” section has no actionable content.
- **Interaction:** Sign out is clear; there is little feedback or affordance for profile/security details.

### B2B workspace

#### Shared B2B shell (`B2BShell`, `AppLayout`, `Sidebar`)

- **Hierarchy:** The sidebar is predictable and nav labels are understandable.
- **Weakness:** The shell has no responsive mobile navigation; a fixed 256px sidebar is squeezed into small viewports. The white sidebar and white cards create very little depth separation.
- **Typography/color:** Small uppercase section labels are consistent but overused. Active navigation relies mostly on a pale indigo background.
- **Interaction:** Hover translations are subtle and somewhat mechanical. There is no active workspace context or mobile menu state.
- **Accessibility:** Nav links are semantic and focusable. The mobile omission is a usability gap, and the account area needs a stronger visible boundary.

#### B2B dashboard (`B2BDashboardPage`)

- **Hierarchy:** The CTA, metrics, quick actions, recent batches, and distribution are all reasonable pieces, but all appear at the same visual level.
- **Weakness:** Quick actions use emoji icons and duplicate navigation destinations; this makes the product feel less premium and less intentional.
- **Data states:** Loading, error, and populated branches exist. The error state should provide retry and a more contextual explanation.

#### Batches (`B2BBatchesPage`)

- **Hierarchy:** Search, status filter, metrics, and list are arranged sensibly.
- **Weakness:** The list is text-heavy and progress is too small to read as an operational dashboard. The “new batch” modal is functional but dense and does not guide the user through a confident upload flow.
- **Interaction/mobile:** Rows collapse acceptably, but the list has no stronger selected/processing treatment. Modal focus management is not explicit.

#### Batch details (`B2BBatchDetailsPage`)

- **Hierarchy:** Breadcrumb, job title, progress, filters, and candidate list are in the correct order.
- **Weakness:** The page has many actions in one header and no clear “what should I do next?” hierarchy. The progress block is a generic bar rather than a live processing signal.
- **States:** Auto-refresh is a good product behavior, but it needs a visible “updating” cue and a better zero-result state.

#### Candidates (`B2BCandidatesPage`)

- **Hierarchy:** Filters are easy to locate, but the page has no summary context before the table.
- **Weakness:** Candidate rows look like plain database records. Score, name, status, and batch need stronger visual grouping.
- **Mobile:** The responsive stack is serviceable but information order is not optimized for quick triage.

#### Analytics overview (`B2BAnalyticsOverviewPage`)

- **Hierarchy:** Metrics and distribution are present, but there is no clear headline insight.
- **Weakness:** The “Best score” tile is always `—`, which is a product-quality defect in a premium surface. Progress bars are useful but visually repetitive.
- **States:** Loading/error branches exist; empty insight states need designed explanations.

#### Batch analytics (`B2BAnalyticsPage`)

- **Hierarchy:** Good placement of batch context, metrics, operational view, distribution, and missing keywords.
- **Weakness:** The charts are basic bars and segmented strips with no explanatory annotation or focal insight.
- **Interaction:** Export and compare actions are present, but the header is action-dense. The page needs a primary insight card and calmer secondary controls.

#### Compare (`B2BComparePage`)

- **Hierarchy:** Candidate cards are easy to scan and the rank is visible.
- **Weakness:** Cards do not create a clear comparison matrix; score is visually detached from the candidate identity and the page lacks a shared baseline for comparing criteria.
- **Mobile:** Cards stack, which is safe, but the comparison experience becomes a list rather than a deliberate ranked review.

#### Resume details (`B2BResumeDetailsPage`)

- **Hierarchy:** Candidate identity, score, breakdown, keywords, and suggestions are the right content model.
- **Weakness:** The score area is not a strong focal point and the report feels like another card stack. Primary review and export actions should be visually separated.
- **States/accessibility:** Error/not-found/retry branches are present. Semantic grouping and heading levels should be more explicit.

#### Exports (`B2BExportsPage`)

- **Hierarchy:** Straightforward table and explanation.
- **Weakness:** Export actions are visually equal to navigation and the page lacks recent/download context.
- **Empty/loading:** Present but generic; the empty state could turn into a useful “create your first batch” invitation.

#### Organization settings (`B2BSettingsPage`)

- **Hierarchy:** Account, current routing, and BYOK configuration are logically separated.
- **Weakness:** Dense form surface, especially on mobile. Provider/model/key/base URL lack progressive disclosure and security reassurance.
- **Interaction:** Test/save feedback exists. Destructive/reverting confirmations rely on `window.confirm`, which is functional but visually disconnected from the system.

### Shared components

- **`Logo`:** Recognizable mark, but the current gradient tile and scale behavior feel like a starter brand treatment. It needs a more controlled mark, intentional light/dark handling, and no global link underline side effect.
- **`PublicHeader`:** Good sticky behavior and auth-aware actions. It is visually light and lacks a clear mobile navigation strategy; the landing nav simply disappears.
- **`PublicLayout`:** Correct structural wrapper. The footer is intentionally out of scope and should remain untouched.
- **`Sidebar`:** Good route grouping, semantic links, and auth account block. It needs a dark/ink surface, responsive mobile trigger, richer active-state treatment, and an explicit workspace label.
- **`AppLayout` / `B2BShell`:** Duplicated shell responsibility. Both should use the same content-width and page-enter conventions for consistency.
- **`FullPageLoading`:** Functional but generic. It should communicate the TalentScope mark and keep the visual language consistent with route loading.
- **`Footer` / `DeveloperCard`:** Reviewed for consistency only; hard constraint says not to modify either file.

## Missed opportunities

1. Make the score the product’s visual language: circular score, confidence, and quality bands should feel uniquely TalentScope.
2. Use a shared “signal” motif—small radar/scan rings, gradient rules, and data-led accents—across landing, analysis, and hiring views.
3. Turn loading into progress communication instead of generic shimmer: “Parsing resume”, “Matching signals”, “Preparing recommendations”.
4. Give every page a consistent page header pattern with eyebrow, title, supporting line, and one primary action.
5. Make empty states directional: each should say what is missing and offer the single next action.
6. Treat mobile as a first-class workspace with a compact top bar and drawer-like navigation.
7. Use the API data already available to surface meaningful insight, including the missing best-score calculation in analytics overview.

## Priority fixes

### P0 — Cohesion and mobile usability

1. Establish one tokenized surface, motion, focus, and page-entry system.
2. Rebuild the authenticated shell with responsive navigation and stronger active context.
3. Make page headers and primary actions consistent across B2C and B2B.

### P1 — Product character and signal hierarchy

4. Redesign the landing hero/product preview around “signal, not noise”.
5. Upgrade analysis/result reveal and B2B score surfaces with a signature score treatment.
6. Replace emoji action tiles with a shared icon/metric language.

### P2 — Operational polish

7. Improve loading, empty, error, and retry messaging across the dashboards and lists.
8. Correct analytics overview’s best-score tile and strengthen chart annotation.
9. Tighten form states, modal surfaces, focus rings, and mobile density.

### P3 — Follow-up opportunities

10. Add keyboard shortcuts and command-style navigation for power users.
11. Add richer candidate comparison by criterion once the API exposes normalized dimensions.
12. Add route-level visual regression snapshots and an automated accessibility pass.
