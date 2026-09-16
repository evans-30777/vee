# VEE Agency Website — Design System, Motion & Accessibility Guidelines

## 1. Visual Direction

The current agreed direction is:

- premium digital agency aesthetic
- dark/black base
- orange/red brand accents
- strong typography
- restrained glass effects
- high contrast
- modern editorial spacing
- purposeful motion

The design should feel **confident, technical and commercial**, not like a gaming site and not like a template.

The DeepSeek source proposed `#0A0A0A` / `#111111` surfaces, orange `#FF4500`, dark red `#8B0000`, white text and muted greys. These can remain the baseline visual tokens while being refined during implementation. fileciteturn5file0L31-L46

---

## 2. Brand Color Tokens

Recommended baseline:

```css
:root {
  --color-bg: #0A0A0A;
  --color-surface: #111111;
  --color-surface-2: #1A1A1A;
  --color-border: rgba(255, 255, 255, 0.08);
  --color-border-hover: rgba(255, 69, 0, 0.4);

  --color-primary: #FF4500;
  --color-primary-hover: #FF6B33;
  --color-secondary: #8B0000;

  --color-text: #FFFFFF;
  --color-text-muted: #A1A1A1;
  --color-text-dim: #6B6B6B;

  --color-success: #25D366;
  --color-error: #EF4444;
  --color-warning: #F59E0B;

  --focus-ring: 0 0 0 3px rgba(255, 69, 0, 0.6);
}
```

The source also specified separate glow tokens and overlay tokens. Use glow sparingly. A glow should reinforce hierarchy, not become the background of the entire website. fileciteturn5file0L31-L46

---

## 3. Typography

Baseline font direction:

- **Headings:** Space Grotesk
- **Body:** Inter

The source proposed these fonts with fluid type scales. fileciteturn5file0L794-L1044

Rules:

- Hero headline: very large, strong, short line lengths
- Section headings: bold but not oversized to the point of waste
- Body copy: readable line height and width
- Small labels: uppercase, tracking, used sparingly
- Do not use more than the two primary font families unless a specific display treatment is justified

---

## 4. Layout

Use a fluid, responsive container system with a sensible max width.

Baseline from the source:

```css
--container-max: 1280px;
--container-pad: clamp(1rem, 4vw, 2rem);
```

Use an 8px spacing logic, with fluid section spacing. fileciteturn5file0L17-L29

Avoid cramped desktop layouts and excessive full-screen section heights.

---

## 5. Cards

Recommended card system:

- border radius roughly 12–20px
- subtle 1px border
- quiet shadow
- clear hover state
- visible keyboard focus state
- consistent internal padding

The original source used 12px base radius and 20px large radius, with modest transitions and shadows. fileciteturn5file0L31-L46

Cards should communicate hierarchy; do not use a different visual treatment for every card type.

---

## 6. Buttons

Primary CTA:

- strong orange background
- dark text when contrast is sufficient
- rounded/pill treatment
- minimum touch target around 44px
- subtle hover translate/glow

Secondary CTA:

- transparent or dark surface
- visible border
- clear hover state

WhatsApp CTA:

- WhatsApp green
- only used for WhatsApp actions
- do not use green as a general brand color

The source baseline used 44px minimum button height and pill-shaped controls. fileciteturn5file0L48-L96

---

## 7. Header

Desktop:

- sticky header
- subtle glass effect
- VEE logo
- Home / Services / Packages / Web Development / About / Blog / Contact
- WhatsApp CTA
- Free Audit CTA

Mobile:

- compact logo
- menu button with a strong focus state
- full-screen or near-full-screen overlay
- clear close button
- keyboard accessible

Do not let the header become visually heavy.

---

## 8. Hero

The hero is the highest-priority visual section.

Preferred elements:

- short eyebrow
- strong headline
- two lines or a deliberately broken headline
- concise support text
- two CTAs
- high-quality visual/motion treatment

A video background may be used, but it must never compromise content readability or performance. On mobile, use a static poster where appropriate.

---

## 9. Motion Philosophy

Motion should explain structure and hierarchy.

Use animation for:

- page entrance
- section reveals
- navigation transitions
- interactive cards
- modal open/close
- subtle parallax where it adds depth

Do not animate everything.

Avoid:

- constant floating motion
- large cursor chases
- excessive scroll hijacking
- animation that delays access to content
- animation that changes layout after text becomes visible

---

## 10. GSAP / ScrollTrigger

The source proposed GSAP + ScrollTrigger. This remains appropriate if implemented carefully.

Preferred defaults:

- ease-out reveals
- 300–800ms durations depending on complexity
- small vertical distances
- `once: true` for content reveals
- avoid animating layout properties where transform/opacity will work

The source used `top 85%` / `top 80%` style triggers and small stagger intervals. fileciteturn5file1L722-L729

---

## 11. Lenis / Smooth Scrolling

Lenis may be used on desktop where it materially improves the visual experience.

Rules:

- never require Lenis for core functionality
- do not enable it on coarse pointer/mobile if it degrades usability
- always support normal browser scrolling
- verify focus, anchor links, keyboard navigation and back-button behavior
- disable or simplify on reduced-motion preferences

The original concept explicitly called for mobile fallbacks and reduced-motion handling. fileciteturn4file9L8750-L8759

---

## 12. Preloader

Use a short branded preloader only when it does not delay meaningful content.

Suggested sequence:

1. logo appears
2. progress/fill cue
3. fade away
4. page becomes fully interactive

Reduced-motion users should skip or receive an almost immediate transition.

Do not allow the preloader to create perceived slowness.

---

## 13. Page Transitions

Optional short same-site transition:

- outgoing page fades slightly
- navigation proceeds
- new page enters quickly

Critical rule: do not break:

- back button
- open-in-new-tab behavior
- external URLs
- download links
- anchor navigation
- form submissions
- browser history

A simpler approach is preferable to a fragile transition system.

---

## 14. Package Cards

Desktop-only tilt can be used as an enhancement.

Rules:

- subtle 3D movement only
- no tilt on touch devices
- no tilt when reduced motion is requested
- hover should never alter pricing readability
- keep the featured plan visually distinct but not manipulative

The source proposed desktop-only 3D package tilt. fileciteturn5file1L8161-L8402

---

## 15. Services Modal

A service card may open a modal with:

- service name
- short explanation
- deliverables
- relevant package(s)
- CTA

Accessibility requirements:

- real dialog semantics
- focus trap
- Escape closes
- backdrop closes where appropriate
- focus returns to triggering element
- keyboard operation without a mouse

---

## 16. Floating Controls

Required/future controls may include:

- WhatsApp floating button
- Tawk.to chat
- back-to-top

Collision rules:

- controls must never overlap
- controls must remain within safe viewport margins
- mobile spacing must be tested on small screens
- hide or reposition lower-priority controls when space becomes constrained

The source explicitly called for collision handling.

---

## 17. Accessibility

Target WCAG 2.2 AA as the working standard.

Minimum requirements:

- semantic headings in correct order
- keyboard navigation
- visible focus state
- skip link
- descriptive link text
- accessible forms
- labels associated with controls
- errors announced clearly where practical
- meaningful alt text
- decorative images marked appropriately
- sufficient color contrast
- no keyboard traps
- reduced-motion support

Never communicate meaning using color alone.

---

## 18. Responsive Strategy

Build mobile-first.

Suggested breakpoints can remain around:

- 640px
- 768px
- 1024px
- 1280px

But components should respond to available space, not blindly to breakpoint numbers.

Test at minimum:

- small mobile
- typical Android phone
- iPhone-sized viewport
- tablet portrait
- tablet landscape
- 1366px desktop
- 1440px desktop
- wide desktop

---

## 19. Reduced Motion

Respect:

```css
@media (prefers-reduced-motion: reduce) {
  /* simplify or disable non-essential motion */
}
```

All JavaScript animation systems must check the same preference before initializing motion-heavy behavior.

The source explicitly required a reduced-motion gate and early return from animation functions. fileciteturn5file0L120-L125

---

## 20. Performance Rules

### Images

- use responsive `srcset`/`picture` where useful
- compress aggressively without visible quality loss
- lazy-load below-the-fold images
- eager-load only critical hero assets
- always reserve image dimensions

### JavaScript

- load non-essential scripts after critical content
- avoid large animation bundles when simple CSS works
- initialize plugins only on pages that use them

### Fonts

- preconnect appropriately
- use `font-display: swap`
- do not load unused weights

### Third-party services

Load only when they provide real value. Tawk, analytics and ad pixels must not become the reason the site is slow.

---
