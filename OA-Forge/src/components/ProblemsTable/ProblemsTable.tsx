import Link from "next/link";
import React, { useEffect, useState } from "react";
import { BsCheckCircle } from "react-icons/bs";
import { OAQuestionWithMeta } from "@/lib/types/oa";
import { getSolvedSlugs } from "@/lib/progress";
import { TierBadge } from "@/components/layout/Shell";

type ProblemsTableProps = {
	setLoadingProblems: React.Dispatch<React.SetStateAction<boolean>>;
	company: string;
	strictMode: boolean;
};

const diffClass = (d: string) =>
	d === "Easy" ? "text-forge-accent" : d === "Medium" ? "text-forge-warn" : "text-forge-danger";

const ProblemsTable: React.FC<ProblemsTableProps> = ({
	setLoadingProblems,
	company,
	strictMode,
}) => {
	const [problems, setProblems] = useState<OAQuestionWithMeta[]>([]);
	const [error, setError] = useState<string | null>(null);
	const [solved, setSolved] = useState<string[]>([]);

	useEffect(() => {
		setSolved(getSolvedSlugs());
		const onStorage = () => setSolved(getSolvedSlugs());
		window.addEventListener("storage", onStorage);
		return () => window.removeEventListener("storage", onStorage);
	}, []);

	useEffect(() => {
		const fetchProblems = async () => {
			setLoadingProblems(true);
			setError(null);

			try {
				if (company === "all") {
					const res = await fetch("/api/companies");
					const { companies } = await res.json();
					const all: OAQuestionWithMeta[] = [];
					const seen = new Set<string>();

					for (const c of companies) {
						const qRes = await fetch(`/api/problems?company=${c.slug}&strict=${strictMode}`);
						const { questions } = await qRes.json();
						for (const q of questions ?? []) {
							if (!seen.has(q.slug)) {
								seen.add(q.slug);
								all.push(q);
							}
						}
					}
					setProblems(all.sort((a, b) => a.question_order - b.question_order));
				} else {
					const res = await fetch(`/api/problems?company=${company}&strict=${strictMode}`);
					if (!res.ok) throw new Error("Failed to load questions");
					const { questions } = await res.json();
					setProblems(questions ?? []);
				}
			} catch (e) {
				setError(e instanceof Error ? e.message : "Failed to load");
				setProblems([]);
			} finally {
				setLoadingProblems(false);
			}
		};

		fetchProblems();
	}, [company, strictMode, setLoadingProblems]);

	if (error) {
		return (
			<tbody>
				<tr>
					<td colSpan={6} className="px-6 py-8 text-center text-forge-danger">
						{error}
					</td>
				</tr>
			</tbody>
		);
	}

	if (problems.length === 0) {
		return (
			<tbody>
				<tr>
					<td colSpan={6} className="px-6 py-8 text-center text-forge-muted font-mono text-sm">
						No questions in pool
						{strictMode ? " (strict: Tier A/B only)" : ""}.
					</td>
				</tr>
			</tbody>
		);
	}

	return (
		<tbody>
			{problems.map((problem) => (
				<tr className="forge-table-row" key={`${problem.slug}-${problem.confidence_tier}`}>
					<td className="px-3 py-4 w-10">
						{solved.includes(problem.slug) && (
							<BsCheckCircle className="text-forge-accent" size={16} />
						)}
					</td>
					<td className="px-4 py-4">
						<Link
							className="text-forge-text hover:text-forge-accent transition-colors font-medium"
							href={`/problems/${problem.slug}`}
						>
							{problem.title}
						</Link>
					</td>
					<td className={`px-4 py-4 font-mono text-xs ${diffClass(problem.difficulty)}`}>
						{problem.difficulty}
					</td>
					<td className="px-4 py-4 text-forge-muted text-sm">{problem.category}</td>
					<td className="px-4 py-4">
						<div className="flex flex-col gap-1">
							<TierBadge tier={problem.confidence_tier} />
							<span className="font-mono text-[10px] text-forge-muted">
								{problem.year}
								{problem.season ? ` · ${problem.season}` : ""}
							</span>
						</div>
					</td>
					<td className="px-4 py-4 text-forge-muted text-xs max-w-[220px] truncate" title={problem.source_notes ?? ""}>
						{problem.source_notes ?? "—"}
					</td>
				</tr>
			))}
		</tbody>
	);
};

export default ProblemsTable;
