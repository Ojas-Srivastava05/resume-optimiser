import { Html, Head, Main, NextScript } from "next/document";

export default function Document() {
	return (
		<Html lang="en" className="bg-forge-bg">
			<Head>
				<link rel="preconnect" href="https://fonts.googleapis.com" />
				<link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
				<link
					href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap"
					rel="stylesheet"
				/>
			</Head>
			<body className="bg-forge-bg text-forge-text antialiased">
				<Main />
				<NextScript />
			</body>
		</Html>
	);
}
