# Style Rules & Design Guidelines

This document defines the style rules and design guidelines for the Stock AI Dashboard to ensure consistency across future enhancements.

## 1. Core Principles
- **Modern & Premium**: Use a dark-themed, sleek aesthetic (Glassmorphism, subtle gradients, and rounded corners).
- **Responsive**: All components must be fully responsive, from mobile (320px) to large desktops (1200px+).
- **Interactive**: Use hover effects, transitions, and micro-animations to enhance user engagement.

## 2. Color Palette
- **Background**: `#0f172a` (Slate-900)
- **Card Background**: `#1e293b` (Slate-800)
- **Primary Accent**: `#2563eb` (Blue-600)
- **Success/Bullish**: `#22c55e` (Green-500)
- **Danger/Bearish**: `#ef4444` (Red-500)
- **Secondary Text**: `#94a3b8` (Slate-400)

## 3. Typography
- **Font Family**: `Inter, sans-serif`
- **Headings**: Use `Inter` with semi-bold or bold weights.
- **Body**: Use `Inter` with normal or medium weights.

## 4. Components
- **Cards**:
    - Border-radius: `12px`
    - Padding: `20px`
    - Box-shadow: `0 10px 30px rgba(0, 0, 0, 0.3)`
- **Badges**:
    - Rounded corners (radius `4px` or `20px` for scores).
    - Semi-transparent background with a solid border for a premium feel.
- **Modals**:
    - Backdrop blur: `5px`
    - Border-radius: `16px`
    - Max-width should adapt to screen size.

## 5. Responsiveness Guidelines
- **Desktop (1024px and up)**: Standard 1200px container.
- **Tablet (768px - 1023px)**: Adjust container padding and potentially switch grid layouts.
- **Mobile (below 768px)**:
    - Stack flex items vertically.
    - Tables should be horizontally scrollable or converted to card views.
    - Reduce font sizes and padding.
    - Maximize width for cards.

## 6. Coding Standards
- Use semantic HTML tags.
- Prefer CSS Flexbox and Grid for layouts.
- Use CSS variables for colors if global changes are expected.
- Maintain `style.css` with clear section headers.
