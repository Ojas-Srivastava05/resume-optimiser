/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		"./pages/**/*.{js,ts,jsx,tsx}",
		"./components/**/*.{js,ts,jsx,tsx}",
		"./src/**/*.{js,ts,jsx,tsx}",
	],
	theme: {
		extend: {
			fontFamily: {
				sans: ["Inter", "system-ui", "sans-serif"],
				mono: ["JetBrains Mono", "ui-monospace", "monospace"],
				display: ["Space Grotesk", "Inter", "sans-serif"],
			},
			colors: {
				forge: {
					bg: "#09090b",
					surface: "#18181b",
					elevated: "#27272a",
					border: "rgba(255,85,0,0.15)",
					muted: "#a1a1aa",
					text: "#ffffff",
					accent: "#ff5500",
					neon: "#ff5500",
					"accent-dim": "#cc4400",
					magenta: "#ffaa00",
					warn: "#ffb400",
					danger: "#ff3366",
					blue: "#ff8800",
				},
				tier: {
					a: "#ff5500",
					b: "#ffaa00",
					c: "#a1a1aa",
				},
				"dark-layer-1": "#18181b",
				"dark-layer-2": "#09090b",
				"dark-fill-2": "rgba(255,85,0,0.08)",
				"dark-fill-3": "rgba(255,85,0,0.04)",
				"dark-gray-7": "rgba(255,255,255,0.55)",
				"dark-gray-8": "rgba(255,255,255,0.95)",
				"brand-orange": "#ff5500",
				"dark-green-s": "#ff5500",
				"dark-yellow": "#ffb400",
				"dark-pink": "#ff3366",
			},
			boxShadow: {
				glow: "0 0 30px rgba(255,85,0,0.15), 0 0 60px rgba(255,170,0,0.05)",
				"glow-sm": "0 0 15px rgba(255,85,0,0.2)",
				card: "0 0 0 1px rgba(255,85,0,0.1), inset 0 1px 0 rgba(255,255,255,0.04)",
				neon: "0 0 5px #ff5500, 0 0 20px rgba(255,85,0,0.3)",
				"neon-sm": "0 0 8px rgba(255,85,0,0.4)",
			},
			animation: {
				"pulse-slow": "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
				"scan-line": "scanLine 8s linear infinite",
			},
			keyframes: {
				scanLine: {
					"0%": { transform: "translateY(-100%)" },
					"100%": { transform: "translateY(100vh)" },
				},
			},
		},
	},
	plugins: [],
};
