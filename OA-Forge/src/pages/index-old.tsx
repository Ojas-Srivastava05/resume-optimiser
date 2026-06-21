import Shell, { SectionTag } from "@/components/layout/Shell";
import useHasMounted from "@/hooks/useHasMounted";
import { OACompanyReadiness } from "@/lib/types/oa";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";

type RealtimeLead = {
	title: string;
	url: string;
	snippet: string;
	source_type: string;
	confidence_hint: string;
};

export default function Home() {
	const [loadingCompanies, setLoadingCompanies] = useState(true);
	const [startingMock, setStartingMock] = useState(false);
	const [companies, setCompanies] = useState<OACompanyReadiness[]>([]);
	const [company, setCompany] = useState("");
	const [companySearch, setCompanySearch] = useState("");
	const [strictMode, setStrictMode] = useState(false);
	const [scraping, setScraping] = useState(false);
	const [leads, setLeads] = useState<RealtimeLead[]>([]);
	const [scrapeMode, setScrapeMode] = useState("");
	const hasMounted = useHasMounted();
	const router = useRouter();

	useEffect(() => {
		fetch("/api/companies/stats")
			.then((r) => r.json())
			.then((data) => {
				const rows = data.companies ?? [];
				setCompanies(rows);
				if (rows.length > 0) setCompany(rows[0].slug);
				setLoadingCompanies(false);
			})
			.catch(() => setLoadingCompanies(false));
	}, []);

	useEffect(() => {
		if (!company) return;
		let active = true;
		setScraping(true);
		setLeads([]);
		// Add a small delay to show loading state
		setTimeout(() => {
			fetch(`/api/realtime-oa?companySlug=${encodeURIComponent(company)}`)
				.then((r) => r.json())
				.then((data) => {
					if (!active) return;
					setLeads(data.leads ?? []);
					setScrapeMode(data.mode ?? "");
				})
				.catch((err) => {
					if (active) {
						console.error('Realtime scrape failed:', err);
						setLeads([]);
					}
				})
				.finally(() => {
					if (active) setScraping(false);
				});
		}, 300);
		return () => {
			active = false;
		};
	}, [company]);

	const handleStartMockOA = async () => {
		if (!company) {
			toast.error("Select a company to start a mock OA");
			return;
		}

		setStartingMock(true);
		try {
			const res = await fetch("/api/mock-oa/start", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ companySlug: company, strictMode }),
			});
			const data = await res.json();
			if (!res.ok) {
				throw new Error(data.error ?? "Failed to start mock OA");
			}
			router.push(`/mock/${data.sessionId}`);
		} catch (e) {
			const errorMessage = e instanceof Error ? e.message : "Failed to start mock OA";
			toast.error(errorMessage, {
				position: "top-center",
				autoClose: 5000,
				theme: "dark",
			});
		} finally {
			setStartingMock(false);
		}
	};

	if (!hasMounted) return null;

	const selected = companies.find((c) => c.slug === company);
	const visibleCompanies = companies.filter((c) =>
		`${c.name} ${c.slug}`.toLowerCase().includes(companySearch.trim().toLowerCase())
	);
	const availableQuestions = strictMode ? selected?.strict_questions ?? 0 : selected?.total_questions ?? 0;
	const requiredQuestions = selected?.num_questions ?? 2;
	const canStart = Boolean(selected) && availableQuestions >= requiredQuestions;

	return (
		<Shell>
			<div className="max-w-6xl mx-auto px-4 py-8 sm:py-12">
				<div className="grid lg:grid-cols-[1.15fr_0.85fr] gap-6 items-start">
					<section className="forge-panel overflow-hidden">
						<div className="p-6 sm:p-8 border-b border-forge-border bg-[radial-gradient(circle_at_20%_0%,rgba(52,211,153,0.12),transparent_28%),linear-gradient(135deg,rgba(255,255,255,0.06),transparent)]">
							<SectionTag index="01 · launch" title="Company mock OA console" />
							<p className="text-forge-muted leading-relaxed max-w-2xl">
								Pick a company, choose the evidence level, and start a timed assessment. Titles
								and topics stay hidden during the OA; metadata is revealed only in debrief.
							</p>
						</div>

						<div className="p-6 sm:p-8 space-y-6">
							<label className="block space-y-2">
								<span className="forge-label">Target company</span>
								<select
									className="w-full bg-forge-elevated border border-forge-border text-forge-text text-sm rounded-lg px-3 py-3 focus:outline-none focus:border-forge-accent/50"
									value={company}
									onChange={(e) => setCompany(e.target.value)}
									disabled={loadingCompanies}
								>
									{companies.map((c) => (
										<option key={c.slug} value={c.slug}>
											{c.name}
										</option>
									))}
								</select>
							</label>

							<div className="grid sm:grid-cols-2 gap-3">
								<button
									type="button"
									onClick={() => setStrictMode(false)}
									className={`forge-choice ${!strictMode ? "forge-choice-active" : ""}`}
								>
									<span className="forge-label">Training pool</span>
									<span className="block text-sm mt-2">Tier A/B/C, transparent labels</span>
									<span className="block text-xs text-forge-muted mt-1">
										{selected?.total_questions ?? 0} usable questions
									</span>
								</button>
								<button
									type="button"
									onClick={() => setStrictMode(true)}
									className={`forge-choice ${strictMode ? "forge-choice-active" : ""}`}
								>
									<span className="forge-label">Strict pool</span>
									<span className="block text-sm mt-2">Tier A/B only</span>
									<span className="block text-xs text-forge-muted mt-1">
										{selected?.strict_questions ?? 0} verified/corroborated
									</span>
								</button>
							</div>

							{selected && (
								<div className="grid grid-cols-3 gap-3">
									<Metric label="Duration" value={`${selected.duration_minutes}m`} />
									<Metric label="Questions" value={`${selected.num_questions}`} />
									<Metric
										label="Readiness"
										value={strictMode && !canStart ? "Locked" : availableQuestions >= requiredQuestions ? "Ready" : "Live"}
										tone={canStart ? "good" : "warn"}
									/>
								</div>
							)}

							<button
								onClick={handleStartMockOA}
								disabled={startingMock || !canStart}
								className="forge-btn-primary w-full py-3"
							>
								{startingMock
									? "Forging session..."
									: canStart
									? "Start timed mock OA"
									: "No curated questions available"}
							</button>

							{!canStart && selected && (
								<p className="text-xs text-forge-danger leading-relaxed mt-3">
									{availableQuestions === 0
										? `No company-specific questions found for ${selected.name}. Add occurrences to data/occurrences.csv first.`
										: `Need ${requiredQuestions} questions, only ${availableQuestions} available. ${strictMode ? 'Try training mode.' : 'Add more occurrences.'}`}
								</p>
							)}
						</div>
					</section>

					<aside className="space-y-4">
						<div className="forge-panel p-5">
							<p className="forge-label mb-4">Selected bank</p>
							{selected ? (
								<div className="space-y-4">
									<div>
										<h1 className="text-2xl font-semibold">{selected.name}</h1>
										<p className="text-sm text-forge-muted mt-1">
											{selected.total_questions} curated rows · {selected.strict_questions} strict ·{" "}
											{scraping ? "scraping live..." : `${leads.length} live leads`}
										</p>
									</div>
									<div className="grid grid-cols-3 gap-2">
										<MiniTier label="A" value={selected.tier_a} />
										<MiniTier label="B" value={selected.tier_b} />
										<MiniTier label="C" value={selected.tier_c} />
									</div>
								</div>
							) : (
								<p className="text-sm text-forge-muted">Loading companies...</p>
							)}
						</div>

						<div className="forge-panel p-5 font-mono text-xs text-forge-muted leading-relaxed">
							<p className="text-forge-accent mb-3">{"// oa_forge.rules"}</p>
							<pre className="whitespace-pre-wrap">{`question_identity = hidden_during_mock
topic_tags = hidden_during_mock
strict_pool = tier_a + tier_b
training_pool = strict_pool + tier_c
live_scrape = on_company_select
fallback = live_pattern_oa
fake_exact_claims = rejected`}</pre>
						</div>
					</aside>
				</div>

				<section className="mt-6 forge-panel p-5">
					<div className="flex flex-wrap items-center justify-between gap-3 mb-4">
						<div>
							<p className="forge-label">Realtime public OA scrape</p>
							<p className="text-sm text-forge-muted mt-1">
								{selected?.name ?? "Company"} · {scraping ? "searching current public sources" : scrapeMode || "idle"}
							</p>
						</div>
						<span className="forge-chip">{leads.length} leads</span>
					</div>
					{scraping ? (
						<div className="flex items-center justify-center py-8">
							<div className="flex items-center gap-3 text-forge-muted">
								<div className="w-2 h-2 rounded-full bg-forge-accent animate-pulse" />
								<span className="text-sm">Scanning public sources for authentic OA reports...</span>
							</div>
						</div>
					) : leads.length === 0 ? (
						<div className="text-sm text-forge-muted py-4 space-y-2">
							{scrapeMode === "research-only" ? (
								<>
									<p>No OA reports found in initial search.</p>
									<p className="text-xs">Try running a manual refresh: <code>npm run refresh:oa-leads -- --company={company}</code></p>
								</>
							) : (
								<>
									<p>No public leads found.</p>
									<p className="text-xs">Try selecting a different company or add occurrences manually.</p>
								</>
							)}
						</div>
					) : (
						<div className="grid md:grid-cols-2 gap-3">
							{leads.slice(0, 12).map((lead) => (
								<a
									key={lead.url}
									href={lead.url}
									target="_blank"
									rel="noreferrer"
									className="rounded-lg border border-forge-border bg-forge-elevated p-4 hover:border-forge-accent/40 transition-colors"
								>
									<div className="flex items-center gap-2 mb-2">
										<span className="forge-label">{lead.source_type}</span>
										<span className="text-[10px] font-mono text-forge-accent">{lead.confidence_hint}</span>
									</div>
									<p className="text-sm font-medium line-clamp-2">{lead.title}</p>
									<p className="text-xs text-forge-muted mt-2 line-clamp-2">{lead.snippet}</p>
								</a>
							))}
						</div>
					)}
				</section>

				<section className="mt-6">
					<div className="flex items-center justify-between mb-3">
						<div>
							<p className="forge-label">Company readiness</p>
							<p className="text-xs text-forge-muted mt-1">
								{visibleCompanies.length} / {companies.length} companies · internship-scout synced
							</p>
						</div>
						<input
							value={companySearch}
							onChange={(event) => setCompanySearch(event.target.value)}
							placeholder="Search company..."
							className="w-52 bg-forge-elevated border border-forge-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-forge-accent/50"
						/>
					</div>
					<div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
						{visibleCompanies.map((c) => (
							<button
								key={c.slug}
								onClick={() => setCompany(c.slug)}
								className={`forge-company-card ${
									company === c.slug ? "border-forge-accent/50 bg-forge-accent/5" : ""
								}`}
							>
								<span className="font-medium">{c.name}</span>
								<span className="font-mono text-[11px] text-forge-muted">
									{c.total_questions} curated · {c.strict_questions} strict · live-ready
								</span>
							</button>
						))}
					</div>
				</section>
			</div>
		</Shell>
	);
}

function Metric({ label, value, tone }: { label: string; value: string; tone?: "good" | "warn" }) {
	return (
		<div className="rounded-lg border border-forge-border bg-forge-elevated p-4">
			<p className="forge-label mb-2">{label}</p>
			<p
				className={
					tone === "good"
						? "text-forge-accent font-semibold"
						: tone === "warn"
						? "text-forge-warn font-semibold"
						: "font-semibold"
				}
			>
				{value}
			</p>
		</div>
	);
}

function MiniTier({ label, value }: { label: string; value: number }) {
	return (
		<div className="rounded-lg border border-forge-border bg-forge-elevated p-3 text-center">
			<p className="forge-label">Tier {label}</p>
			<p className="font-mono text-lg mt-1">{value}</p>
		</div>
	);
}
