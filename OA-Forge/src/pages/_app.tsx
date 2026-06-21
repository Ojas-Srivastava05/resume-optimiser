import "@/styles/globals.css";
import type { AppProps } from "next/app";
import Head from "next/head";
import { RecoilRoot } from "recoil";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export default function App({ Component, pageProps }: AppProps) {
	return (
		<RecoilRoot>
			<Head>
				<title>OA Forge — Company OA Practice</title>
				<meta name="viewport" content="width=device-width, initial-scale=1" />
				<link rel="icon" href="/favicon.png" />
				<meta
					name="description"
					content="Practice company-specific online assessment questions with sourced metadata and mock OA sessions"
				/>
			</Head>
			<ToastContainer theme="dark" toastClassName="!bg-forge-elevated !text-forge-text !border-forge-border" />
			<Component {...pageProps} />
		</RecoilRoot>
	);
}
