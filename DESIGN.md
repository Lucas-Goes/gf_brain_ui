---
name: Cyber-Professional AI
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#e3bfb1'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#aa8a7d'
  outline-variant: '#5a4136'
  surface-tint: '#ffb596'
  primary: '#ffb596'
  on-primary: '#581e00'
  primary-container: '#ff6600'
  on-primary-container: '#561d00'
  inverse-primary: '#a33e00'
  secondary: '#c7c6c6'
  on-secondary: '#2f3131'
  secondary-container: '#484949'
  on-secondary-container: '#b8b8b8'
  tertiary: '#c8c6c5'
  on-tertiary: '#313030'
  tertiary-container: '#989696'
  on-tertiary-container: '#2f2f2f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdbcd'
  primary-fixed-dim: '#ffb596'
  on-primary-fixed: '#360f00'
  on-primary-fixed-variant: '#7c2e00'
  secondary-fixed: '#e3e2e2'
  secondary-fixed-dim: '#c7c6c6'
  on-secondary-fixed: '#1a1c1c'
  on-secondary-fixed-variant: '#464747'
  tertiary-fixed: '#e5e2e1'
  tertiary-fixed-dim: '#c8c6c5'
  on-tertiary-fixed: '#1c1b1b'
  on-tertiary-fixed-variant: '#474746'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display-xl:
    fontFamily: Hanken Grotesk
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.1em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-desktop: 64px
  margin-mobile: 16px
  max-width-chat: 800px
---

## Brand & Style

This design system is built for a high-performance AI agent, prioritizing speed, precision, and technical authority. The "Cyber-Professional" aesthetic blends the utilitarian rigor of developer tools with the premium finish of high-end enterprise software.

The emotional response is one of **calculated intelligence**. We use a deep-space black foundation to eliminate visual noise, allowing the vibrant orange accents to act as functional beacons for action and status. The style combines **Minimalism** with subtle **Glassmorphism**, using translucent overlays and micro-glows to simulate a high-tech terminal interface that feels both futuristic and dependable.

## Colors

The palette is rooted in a pure nocturnal base to maximize contrast and reduce eye strain during deep-work sessions.

- **Primary (#FF6600):** Used exclusively for interactive states, primary actions, and brand-identifying markers. It represents the "spark" of AI intelligence.
- **Secondary (#A0A0A0):** A cool, silver-grey used for primary typography and iconography to maintain a professional, low-glare reading experience.
- **Surface & Background:** The background is a deep `#050505`. Elevated surfaces (cards, inputs) use `#121212` with a subtle `#FFFFFF0A` (4% white) stroke to define edges without heavy shadows.
- **Status:** Use the primary orange for "Active" or "Processing" states. Success is indicated by a desaturated mint, and errors by a high-chroma red-orange.

## Typography

The typography system utilizes a trio of typefaces to distinguish between brand presence, content readability, and technical data.

- **Hanken Grotesk** is used for display and headlines. Its sharp, contemporary geometry mirrors the precision of the AI.
- **Inter** handles the bulk of message flows and body content, chosen for its exceptional legibility in dark mode and high-density environments.
- **JetBrains Mono** is utilized for "Scope" selectors, status labels, and code blocks. It provides the "Cyber" edge, signaling to the user that they are interacting with a logical, data-driven system.

## Layout & Spacing

The layout follows a **Fixed-Fluid hybrid model**. 
- **Centralized Focus:** For the initial state, the chat input is centered both vertically and horizontally within a constrained 800px container to focus user intent.
- **Message Flow:** Once a session begins, the input transitions to the bottom of the viewport, and the content flows in a standard vertical stack.
- **Rhythm:** We use a 4px base grid. Components are separated by `32px` (8 units) to maintain a spacious, professional feel, while internal component padding is tight (`12px` to `16px`) to emphasize efficiency.
- **Breakpoints:** 
    - Desktop (1200px+): 12-column grid, 64px margins.
    - Tablet (768px - 1199px): 8-column grid, 32px margins.
    - Mobile (<767px): 4-column grid, 16px margins.

## Elevation & Depth

In a "Cyber-Professional" dark theme, we avoid traditional drop shadows which can look muddy. Instead, depth is communicated through **Tonal Luminance** and **Inner Glows**.

- **Z-Index 0 (Background):** Pure black `#050505`.
- **Z-Index 1 (Cards/Containers):** Slightly lighter `#121212`. Borders are `1px solid #1A1A1A`.
- **Z-Index 2 (Active/Hover):** When an element is focused (like the chat input), it gains a subtle outer glow: `box-shadow: 0 0 15px rgba(255, 102, 0, 0.15)`.
- **Glass Effects:** Overlays and modals use a `backdrop-filter: blur(12px)` with a desaturated tint to maintain context of the underlying data flow.

## Shapes

The shape language is **Technical and Precise**. 

We use **Soft (0.25rem)** rounding for standard components like inputs and message bubbles. This prevents the UI from feeling too aggressive (sharp) or too consumer-grade (pill-shaped). 

Specialty "Scope" buttons use a "clipped-corner" aesthetic or a very small radius to emphasize their role as high-tech selectors. Action buttons that are secondary may use a 0px radius for a more brutalist, functional look.

## Components

### Centralized Chat Input
- **Initial State:** A large, 64px tall input field with a `1px` orange border. Placeholder text is in `label-caps`. 
- **Transition:** Upon first submit, the input shrinks and slides to the bottom bar, anchored with a subtle glassmorphism background.

### Scope Selectors (Code, Architecture, Business, Automations)
- **Styling:** Styled as segmented controls or "Toggle Chips." 
- **Inactive:** Transparent background, `#A0A0A0` border, `jetbrainsMono` labels.
- **Active:** Background becomes `#FF6600`, text becomes `#050505`. Add a small orange "active" dot icon next to the text.
- **Visual:** Use a subtle scan-line texture or a very faint glow when a scope is selected.

### Message Bubbles
- **User:** Right-aligned, no background, just a thin grey right-border to indicate ownership.
- **AI Agent:** Left-aligned, `#121212` background. The orange accent color appears as a 2px vertical "status bar" on the far left of the bubble to signal the AI is the source.

### Buttons & Inputs
- **Primary Button:** Solid `#FF6600` with black text. On hover, increase brightness.
- **Inputs:** Dark grey background `#0A0A0A` with a focus state that illuminates the bottom border in orange.