import Link from "next/link";
import { useEffect, useState } from "react";

function istClock() {
	return new Date().toLocaleTimeString("en-IN", {
		timeZone: "Asia/Kolkata",
		hour: "2-digit",
		minute: "2-digit",
		second: "2-digit",
		hour12: false,
	});
}

type ShellProps = {
	children: React.ReactNode;
	problemPage?: boolean;
};

export default function Shell({ children, problemPage }: ShellProps) {
	const [time, setTime] = useState("");

	useEffect(() => {
		setTime(istClock());
		const t = setInterval(() => setTime(istClock()), 1000);
		return () => clearInterval(t);
	}, []);

	return (
		<div className="min-h-screen bg-forge-bg flex flex-col">
			<header className="border-b border-forge-border bg-forge-surface/80 backdrop-blur-md sticky top-0 z-50">
				<div className="max-w-6xl mx-auto px-4 h-12 flex items-center justify-between gap-4">
					<div className="flex items-center gap-3 min-w-0">
						<Link href="/" className="font-display text-sm font-bold tracking-widest shrink-0">
							<span className="text-forge-accent">OA</span>
							<span className="text-forge-magenta">CRUCIBLE</span>
						</Link>
						<span className="hidden sm:inline forge-label text-[10px] truncate text-forge-muted">
							c++ · mock oa · no auth
						</span>
					</div>

					<div className="hidden md:flex items-center gap-3 font-mono text-[10px] text-forge-muted uppercase tracking-wider">
						<span className="flex items-center gap-1.5">
							<span className="w-1.5 h-1.5 rounded-full bg-forge-accent animate-pulse-slow" />
							ready
						</span>
						<span>SURAT, IN</span>
						<span>{time || "—:—:—"} IST</span>
					</div>

					<nav className="flex items-center gap-2 text-sm shrink-0">
						{!problemPage && (
							<>
								<Link href="/admin" className="forge-btn-ghost py-1.5 px-3 text-xs hidden sm:inline-flex">
									Ingest
								</Link>
								<a
									href="https://ojas-srivastava.vercel.app"
									target="_blank"
									rel="noreferrer"
									className="forge-btn-ghost py-1.5 px-3 text-xs hidden sm:inline-flex"
								>
									Portfolio ↗
								</a>
							</>
						)}
						{problemPage && (
							<Link href="/" className="forge-btn-ghost py-1.5 px-3 text-xs">
								← Problem bank
							</Link>
						)}
					</nav>
				</div>
			</header>
			<main className="flex-1">{children}</main>
			<footer className="border-t border-forge-border py-4 mt-auto">
				<div className="max-w-6xl mx-auto px-4 flex flex-wrap items-center justify-between gap-2 text-xs font-mono text-forge-muted">
					<span>{"// ojas.srivastava — OA Crucible v1"}</span>
					<span>● UTF-8 · questions from Supabase · tiers A/B/C</span>
				</div>
			</footer>
		</div>
	);
}

export function TierBadge({ tier }: { tier: "A" | "B" | "C" }) {
	const config = {
		A: { label: "Tier A · Verified", className: "text-tier-a border-tier-a/30 bg-tier-a/10" },
		B: { label: "Tier B · Corroborated", className: "text-tier-b border-tier-b/30 bg-tier-b/10" },
		C: { label: "Tier C · Similar", className: "text-tier-c border-tier-c/40 bg-zinc-800/50" },
	};
	const c = config[tier];
	return (
		<span className={`forge-chip ${c.className}`}>{c.label}</span>
	);
}

export function SectionTag({ index, title }: { index: string; title: string }) {
	return (
		<div className="mb-6">
			<p className="forge-label mb-1">{index}</p>
			<h2 className="text-xl sm:text-2xl font-semibold tracking-tight text-forge-text">{title}</h2>
		</div>
	);
}
