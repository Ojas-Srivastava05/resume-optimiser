import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/router";
import { toast } from "react-toastify";
import Shell from "@/components/layout/Shell";
import { getLocalCompanyReadiness } from "@/lib/localBank";

export default function Home() {
	const router = useRouter();
	const [hasMounted, setHasMounted] = useState(false);
	const [companies, setCompanies] = useState<any[]>([]);
	const [loadingCompanies, setLoadingCompanies] = useState(true);
	const [company, setCompany] = useState("");
	const [companySearch, setCompanySearch] = useState("");
	const [strictMode, setStrictMode] = useState(false);
	const [startingMock, setStartingMock] = useState(false);
	const [scraping, setScraping] = useState(false);
	const [leads, setLeads] = useState<any[]>([]);
	const [scrapeMode, setScrapeMode] = useState("");

	useEffect(() => {
		setHasMounted(true);
		fetch("/api/companies/stats")
			.then((r) => r.json())
			.then((data) => {
				const list = data.companies || [];
				setCompanies(list);
				if (list.length > 0) setCompany(list[0].slug);
				setLoadingCompanies(false);
			})
			.catch(() => setLoadingCompanies(false));
	}, []);

	useEffect(() => {
		if (!company) return;
		let active = true;
		setScraping(true);
		setLeads([]);
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

	// Background scrape on load (batch, non-blocking)
	useEffect(() => {
		if (!hasMounted) return;
		fetch("/api/scrape-questions", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ batch: true, limit: 6, maxQuestions: 3 }),
		}).catch(() => {});
	}, [hasMounted]);

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
			<div className="min-h-screen relative">
				<div className="absolute inset-0 bg-gradient-to-b from-forge-neon/5 via-transparent to-forge-magenta/5 pointer-events-none" />
				<div className="max-w-7xl mx-auto px-6 py-16 lg:py-24 relative">
					<div className="max-w-3xl">
						<p className="forge-label mb-4 text-forge-neon animate-pulse-neon">mock_oa.init()</p>
						<h1 className="font-display text-5xl lg:text-7xl font-black text-white mb-6 tracking-wider">
							OA<span className="text-forge-neon">FORGE</span>
						</h1>
						<p className="text-xl lg:text-2xl text-forge-muted mb-8 leading-relaxed">
							966 companies · 20 questions each · C++ only · no sign-in
						</p>
						<div className="flex flex-wrap gap-4">
							<div className="flex items-center gap-2 text-forge-neon font-mono text-sm">
								<div className="w-2 h-2 rounded-full bg-forge-neon shadow-neon-sm animate-pulse" />
								<span>{companies.length || 966}+ companies ready</span>
							</div>
							<div className="flex items-center gap-2 text-forge-blue font-mono text-sm">
								<div className="w-2 h-2 rounded-full bg-forge-blue" />
								<span>live scrape on load</span>
							</div>
						</div>
					</div>
				</div>

				{/* Main Content */}
				<div className="max-w-7xl mx-auto px-6 pb-20">
					<div className="grid lg:grid-cols-[1fr_400px] gap-12">
						{/* Left Column - Company Selection */}
						<div className="space-y-8">
							{/* Company Selector */}
							<div className="space-y-6">
								<div>
									<label className="block text-sm font-medium text-forge-muted mb-3">
										Select Company
									</label>
									<select
										className="w-full bg-forge-surface border border-forge-border text-white text-lg rounded-xl px-6 py-4 focus:outline-none focus:border-forge-accent/50 transition-colors"
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
								</div>

								{/* Pool Selection */}
								<div className="grid grid-cols-2 gap-4">
									<button
										type="button"
										onClick={() => setStrictMode(false)}
										className={`p-6 rounded-xl border-2 transition-all ${
											!strictMode
												? "border-forge-accent bg-forge-accent/10 text-white"
												: "border-forge-border bg-forge-surface text-forge-muted hover:border-forge-accent/30"
										}`}
									>
										<div className="text-lg font-semibold mb-2">Training Pool</div>
										<div className="text-sm text-forge-muted">
											Tier A/B/C
										</div>
										<div className="text-xs text-forge-accent mt-2">
											{selected?.total_questions ?? 0} questions
										</div>
									</button>
									<button
										type="button"
										onClick={() => setStrictMode(true)}
										className={`p-6 rounded-xl border-2 transition-all ${
											strictMode
												? "border-forge-accent bg-forge-accent/10 text-white"
												: "border-forge-border bg-forge-surface text-forge-muted hover:border-forge-accent/30"
										}`}
									>
										<div className="text-lg font-semibold mb-2">Strict Pool</div>
										<div className="text-sm text-forge-muted">
											Tier A/B only
										</div>
										<div className="text-xs text-forge-accent mt-2">
											{selected?.strict_questions ?? 0} questions
										</div>
									</button>
								</div>

								{/* Metrics */}
								{selected && (
									<div className="grid grid-cols-3 gap-4">
										<div className="bg-forge-surface border border-forge-border rounded-xl p-6">
											<div className="text-sm text-forge-muted mb-2">Duration</div>
											<div className="text-2xl font-bold text-white">
												{selected.duration_minutes}m
											</div>
										</div>
										<div className="bg-forge-surface border border-forge-border rounded-xl p-6">
											<div className="text-sm text-forge-muted mb-2">Questions</div>
											<div className="text-2xl font-bold text-white">
												{selected.num_questions}
											</div>
										</div>
										<div className="bg-forge-surface border border-forge-border rounded-xl p-6">
											<div className="text-sm text-forge-muted mb-2">Readiness</div>
											<div className={`text-2xl font-bold ${
												canStart ? "text-forge-accent" : "text-forge-warn"
											}`}>
												{availableQuestions >= requiredQuestions ? "Ready" : "Locked"}
											</div>
										</div>
									</div>
								)}

								{/* Start Button */}
								<button
									onClick={handleStartMockOA}
									disabled={startingMock || !canStart}
									className="w-full py-5 text-lg font-display font-bold rounded-xl bg-forge-neon text-forge-bg hover:shadow-glow transition-all disabled:opacity-40 disabled:cursor-not-allowed"
								>
									{startingMock
										? "Initializing session..."
										: canStart
										? "Start Mock OA"
										: "Add questions first"}
								</button>

								{!canStart && selected && (
									<p className="text-sm text-forge-danger text-center">
										{availableQuestions === 0
											? `No questions found for ${selected.name}. Add occurrences to data/occurrences.csv`
											: `Need ${requiredQuestions} questions, only ${availableQuestions} available`}
									</p>
								)}
							</div>
						</div>

						{/* Right Column - Stats & Leads */}
						<div className="space-y-8">
							{/* Selected Company Stats */}
							{selected && (
								<div className="bg-forge-surface border border-forge-border rounded-2xl p-8">
									<h2 className="text-2xl font-bold text-white mb-6">{selected.name}</h2>
									<div className="space-y-4">
										<div className="flex justify-between items-center">
											<span className="text-forge-muted">Total Questions</span>
											<span className="text-xl font-semibold text-white">{selected.total_questions}</span>
										</div>
										<div className="flex justify-between items-center">
											<span className="text-forge-muted">Strict Questions</span>
											<span className="text-xl font-semibold text-white">{selected.strict_questions}</span>
										</div>
										<div className="h-px bg-forge-border" />
										<div className="grid grid-cols-3 gap-4">
											<div className="text-center">
												<div className="text-3xl font-bold text-tier-a">{selected.tier_a}</div>
												<div className="text-xs text-forge-muted mt-1">Tier A</div>
											</div>
											<div className="text-center">
												<div className="text-3xl font-bold text-tier-b">{selected.tier_b}</div>
												<div className="text-xs text-forge-muted mt-1">Tier B</div>
											</div>
											<div className="text-center">
												<div className="text-3xl font-bold text-tier-c">{selected.tier_c}</div>
												<div className="text-xs text-forge-muted mt-1">Tier C</div>
											</div>
										</div>
									</div>
								</div>
							)}

							{/* Real-time Leads */}
							<div className="bg-forge-surface border border-forge-border rounded-2xl p-8">
								<div className="flex justify-between items-center mb-6">
									<h3 className="text-lg font-semibold text-white">Live OA Reports</h3>
									<span className="text-sm text-forge-accent">{leads.length} leads</span>
								</div>
								{scraping ? (
									<div className="flex items-center justify-center py-12">
										<div className="flex items-center gap-3 text-forge-muted">
											<div className="w-3 h-3 rounded-full bg-forge-accent animate-pulse" />
											<span>Scanning sources...</span>
										</div>
									</div>
								) : leads.length === 0 ? (
									<div className="text-center py-12 text-forge-muted">
										<p>No reports found</p>
										<p className="text-sm mt-2">Try manual refresh</p>
									</div>
								) : (
									<div className="space-y-3 max-h-96 overflow-y-auto">
										{leads.slice(0, 8).map((lead) => (
											<a
												key={lead.url}
												href={lead.url}
												target="_blank"
												rel="noreferrer"
												className="block p-4 rounded-lg bg-forge-bg border border-forge-border hover:border-forge-accent/50 transition-colors"
											>
												<div className="flex items-center gap-2 mb-2">
													<span className="text-xs font-mono px-2 py-1 rounded bg-forge-surface text-forge-accent">
														{lead.source_type}
													</span>
													<span className="text-xs font-mono text-forge-muted">
														{lead.confidence_hint}
													</span>
												</div>
												<p className="text-sm font-medium text-white line-clamp-2">{lead.title}</p>
											</a>
										))}
									</div>
								)}
							</div>
						</div>
					</div>

					{/* Company Grid */}
					<div className="mt-16">
						<div className="flex justify-between items-center mb-8">
							<h2 className="text-2xl font-bold text-white">All Companies</h2>
							<input
								value={companySearch}
								onChange={(event) => setCompanySearch(event.target.value)}
								placeholder="Search companies..."
								className="w-64 bg-forge-surface border border-forge-border rounded-xl px-4 py-3 text-white focus:outline-none focus:border-forge-accent/50"
							/>
						</div>
						<div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
							{visibleCompanies.map((c) => (
								<button
									key={c.slug}
									onClick={() => setCompany(c.slug)}
									className={`p-6 rounded-xl border-2 text-left transition-all ${
										company === c.slug
											? "border-forge-accent bg-forge-accent/10 text-white"
											: "border-forge-border bg-forge-surface text-forge-muted hover:border-forge-accent/30"
									}`}
								>
									<div className="font-semibold text-lg mb-2">{c.name}</div>
									<div className="text-sm text-forge-muted">
										{c.total_questions} curated · {c.strict_questions} strict
									</div>
								</button>
							))}
						</div>
					</div>
				</div>
			</div>
		</Shell>
	);
}
