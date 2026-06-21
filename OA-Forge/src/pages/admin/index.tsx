import Shell, { SectionTag } from "@/components/layout/Shell";
import useHasMounted from "@/hooks/useHasMounted";
import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { ConfidenceTier } from "@/lib/types/oa";

type Company = { slug: string; name: string };

const TIERS: ConfidenceTier[] = ["A", "B", "C"];

export default function AdminIngestPage() {
	const hasMounted = useHasMounted();
	const [companies, setCompanies] = useState<Company[]>([]);
	const [submitting, setSubmitting] = useState(false);
	const [form, setForm] = useState({
		companySlug: "",
		questionSlug: "",
		year: new Date().getFullYear(),
		season: "Summer Intern",
		confidenceTier: "B" as ConfidenceTier,
		sourceNotes: "",
		sourceUrl: "",
	});

	useEffect(() => {
		fetch("/api/companies")
			.then((r) => r.json())
			.then((d) => setCompanies(d.companies ?? []));
	}, []);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setSubmitting(true);
		try {
			const res = await fetch("/api/admin/ingest", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(form),
			});
			const data = await res.json();
			if (!res.ok) throw new Error(data.error);
			toast.success("Occurrence ingested — visible in bank after refresh");
			setForm((f) => ({ ...f, sourceNotes: "", sourceUrl: "" }));
		} catch (err) {
			toast.error(err instanceof Error ? err.message : "Ingest failed");
		} finally {
			setSubmitting(false);
		}
	};

	if (!hasMounted) return null;

	return (
		<Shell>
			<div className="max-w-xl mx-auto px-4 py-12">
				<SectionTag index="Admin · ingest" title="Add company occurrence" />
				<p className="text-forge-muted text-sm mb-8 leading-relaxed">
					Record a sourced OA report. Question must already exist in{" "}
					<code className="text-forge-accent">oa_questions</code> (slug). No gimmick tags —
					every row needs tier + source notes.
				</p>

				<form onSubmit={handleSubmit} className="forge-panel p-6 space-y-5">
					<label className="block space-y-1.5">
						<span className="forge-label">Company</span>
						<select
							required
							className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2.5 text-sm"
							value={form.companySlug}
							onChange={(e) => setForm({ ...form, companySlug: e.target.value })}
						>
							<option value="">Select…</option>
							{companies.map((c) => (
								<option key={c.slug} value={c.slug}>
									{c.name}
								</option>
							))}
						</select>
					</label>

					<label className="block space-y-1.5">
						<span className="forge-label">Question slug</span>
						<input
							required
							placeholder="two-sum"
							className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2.5 text-sm font-mono"
							value={form.questionSlug}
							onChange={(e) => setForm({ ...form, questionSlug: e.target.value })}
						/>
					</label>

					<div className="grid sm:grid-cols-2 gap-4">
						<label className="block space-y-1.5">
							<span className="forge-label">Year</span>
							<input
								type="number"
								required
								className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2.5 text-sm"
								value={form.year}
								onChange={(e) => setForm({ ...form, year: Number(e.target.value) })}
							/>
						</label>
						<label className="block space-y-1.5">
							<span className="forge-label">Season / role</span>
							<input
								className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2.5 text-sm"
								value={form.season}
								onChange={(e) => setForm({ ...form, season: e.target.value })}
							/>
						</label>
					</div>

					<label className="block space-y-1.5">
						<span className="forge-label">Confidence tier</span>
						<select
							className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2.5 text-sm"
							value={form.confidenceTier}
							onChange={(e) =>
								setForm({ ...form, confidenceTier: e.target.value as ConfidenceTier })
							}
						>
							{TIERS.map((t) => (
								<option key={t} value={t}>
									Tier {t}
								</option>
							))}
						</select>
					</label>

					<label className="block space-y-1.5">
						<span className="forge-label">Source notes (required)</span>
						<textarea
							required
							rows={3}
							placeholder="LC Discuss thread + friend OA report, Summer 2025 intern…"
							className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2.5 text-sm"
							value={form.sourceNotes}
							onChange={(e) => setForm({ ...form, sourceNotes: e.target.value })}
						/>
					</label>

					<label className="block space-y-1.5">
						<span className="forge-label">Source URL (optional)</span>
						<input
							type="url"
							className="w-full bg-forge-elevated border border-forge-border rounded-lg px-3 py-2.5 text-sm"
							value={form.sourceUrl}
							onChange={(e) => setForm({ ...form, sourceUrl: e.target.value })}
						/>
					</label>

					<button type="submit" disabled={submitting} className="forge-btn-primary w-full">
						{submitting ? "Saving…" : "Ingest occurrence"}
					</button>
				</form>
			</div>
		</Shell>
	);
}
