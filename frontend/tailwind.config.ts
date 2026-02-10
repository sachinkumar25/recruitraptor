import type { Config } from "tailwindcss";

const config: Config = {
    darkMode: ["class", '[data-theme="dark"]'],
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
            },
            colors: {
                success: {
                    DEFAULT: "hsl(160 84% 39%)",
                    foreground: "hsl(0 0% 100%)",
                },
                warning: {
                    DEFAULT: "hsl(38 92% 50%)",
                    foreground: "hsl(0 0% 0%)",
                },
                info: {
                    DEFAULT: "hsl(199 89% 48%)",
                    foreground: "hsl(0 0% 100%)",
                },
            },
            boxShadow: {
                'glow': '0 0 20px rgba(79, 70, 229, 0.3)',
                'glow-lg': '0 0 40px rgba(79, 70, 229, 0.4)',
                'card': '0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1)',
                'card-hover': '0 12px 24px -8px rgba(0, 0, 0, 0.15)',
                'elevated': '0 20px 40px -12px rgba(0, 0, 0, 0.2)',
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'gradient-primary': 'linear-gradient(135deg, hsl(239 84% 67%) 0%, hsl(271 91% 65%) 100%)',
                'gradient-success': 'linear-gradient(135deg, hsl(160 84% 39%) 0%, hsl(142 71% 45%) 100%)',
                'gradient-sidebar': 'linear-gradient(180deg, hsl(224 71% 8%) 0%, hsl(224 71% 4%) 100%)',
            },
            animation: {
                'fade-in': 'fade-in 0.3s ease-out',
                'slide-up': 'slide-up 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
                'slide-down': 'slide-down 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
                'scale-in': 'scale-in 0.2s ease-out',
                'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
                'score-ring': 'score-ring 1s ease-out forwards',
                'shimmer': 'shimmer 1.5s infinite',
            },
            keyframes: {
                'fade-in': {
                    from: { opacity: '0' },
                    to: { opacity: '1' },
                },
                'slide-up': {
                    from: { opacity: '0', transform: 'translateY(10px)' },
                    to: { opacity: '1', transform: 'translateY(0)' },
                },
                'slide-down': {
                    from: { opacity: '0', transform: 'translateY(-10px)' },
                    to: { opacity: '1', transform: 'translateY(0)' },
                },
                'scale-in': {
                    from: { opacity: '0', transform: 'scale(0.95)' },
                    to: { opacity: '1', transform: 'scale(1)' },
                },
                'pulse-glow': {
                    '0%, 100%': { boxShadow: '0 0 5px rgba(79, 70, 229, 0.3)' },
                    '50%': { boxShadow: '0 0 20px rgba(79, 70, 229, 0.6)' },
                },
                'score-ring': {
                    from: { strokeDashoffset: '283' },
                    to: { strokeDashoffset: 'var(--score-offset)' },
                },
                'shimmer': {
                    '0%': { backgroundPosition: '-200% 0' },
                    '100%': { backgroundPosition: '200% 0' },
                },
            },
            transitionTimingFunction: {
                'out-expo': 'cubic-bezier(0.16, 1, 0.3, 1)',
            },
        },
    },
    plugins: [require("tailwindcss-animate")],
};

export default config;
