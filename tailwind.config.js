/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Nunito', 'Gill Sans', 'Century Gothic', 'Futura', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Courier New', 'monospace'],
      },
      colors: {
        palette: {
          1: '#8e3a59', // Deep Berry Wine (Primary)
          2: '#a5617a', // Rich Mauve Rose (Hover/Accent)
          3: '#bb899b', // Dusty Rose (Medium Accent)
          4: '#d2b0bd', // Soft Rose Mist (Borders/Badges)
          5: '#e8d8de', // Pale Rose Tint (Surfaces)
        },
        brand: {
          DEFAULT: '#8e3a59',
          hover: '#752d48',
          mauve: '#a5617a',
          rose: '#bb899b',
          mist: '#d2b0bd',
          pale: '#e8d8de',
          tint: '#f7eef2',
        },
        sand:   '#a5617a',
        sage:   '#8e3a59',
        taupe:  '#6e5963',
        cream:  '#f8f2f5',
        offwhite: '#fbf8f9',
        light:  '#f6eff2',
        dark:   '#1a0f15',
        mid:    '#2c1b23',
      },
    },
  },
  plugins: [],
};
