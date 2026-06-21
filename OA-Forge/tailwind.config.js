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
				display: ["Orbitron", "Inter", "sans-serif"],
			},
			colors: {
				forge: {
					bg: "#050508",
					surface: "#0a0a12",
					elevated: "#12121f",
					border: "rgba(0,240,255,0.12)",
					muted: "rgba(180,200,255,0.55)",
					text: "rgba(230,240,255,0.95)",
					accent: "#00f0ff",
					neon: "#00f0ff",
					"accent-dim": "#00a8b8",
					magenta: "#ff00aa",
					warn: "#ffd700",
					danger: "#ff3366",
					blue: "#7b61ff",
				},
				tier: {
					a: "#00f0ff",
					b: "#7b61ff",
					c: "#4a5568",
				},
				"dark-layer-1": "#12121f",
				"dark-layer-2": "#0a0a12",
				"dark-fill-2": "rgba(0,240,255,0.08)",
				"dark-fill-3": "rgba(0,240,255,0.04)",
				"dark-gray-7": "rgba(180,200,255,0.55)",
				"dark-gray-8": "rgba(230,240,255,0.95)",
				"brand-orange": "#00f0ff",
				"dark-green-s": "#00f0ff",
				"dark-yellow": "#ffd700",
				"dark-pink": "#ff3366",
			},
			boxShadow: {
				glow: "0 0 30px rgba(0,240,255,0.15), 0 0 60px rgba(255,0,170,0.05)",
				"glow-sm": "0 0 15px rgba(0,240,255,0.2)",
				card: "0 0 0 1px rgba(0,240,255,0.1), inset 0 1px 0 rgba(255,255,255,0.04)",
				neon: "0 0 5px #00f0ff, 0 0 20px rgba(0,240,255,0.3)",
				"neon-sm": "0 0 8px rgba(0,240,255,0.4)",
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
