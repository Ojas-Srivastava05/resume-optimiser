import { Problem } from "@/utils/types/problem";
import { useEffect, useState } from "react";
import { BsCheck2Circle } from "react-icons/bs";
import { TierBadge } from "@/components/layout/Shell";
import { ConfidenceTier } from "@/lib/types/oa";
import { isSolved } from "@/lib/progress";

type Occurrence = {
	confidence_tier: ConfidenceTier;
	year: number;
	season: string | null;
	round_type: string;
	source_notes: string | null;
	source_url: string | null;
	oa_companies: { slug: string; name: string };
};

type OProblemPanelProps = {
	problem: Problem;
	mockMode?: boolean;
	questionLabel?: string;
};

const diffClass = (d: string) =>
	d === "Easy" ? "text-forge-accent" : d === "Medium" ? "text-forge-warn" : "text-forge-danger";

export default function OProblemPanel({ problem, mockMode, questionLabel }: OProblemPanelProps) {
	const [occurrences, setOccurrences] = useState<Occurrence[]>([]);
	const [difficulty, setDifficulty] = useState<string>("");
	const [loading, setLoading] = useState(true);
	const solved = isSolved(problem.id);

	useEffect(() => {
		fetch(`/api/question-meta?slug=${problem.id}`)
			.then((r) => r.json())
			.then((data) => {
				setOccurrences(data.occurrences ?? []);
				if (data.question?.difficulty) setDifficulty(data.question.difficulty);
			})
			.finally(() => setLoading(false));
	}, [problem.id]);

	return (
		<div className="bg-forge-surface border-r border-forge-border h-[calc(100vh-48px)] overflow-auto">
			<div className="p-6 max-w-2xl">
				<div className="flex items-start justify-between gap-4 mb-6">
					<div>
						<p className="forge-label mb-2">
							{mockMode ? questionLabel ?? "Mock OA Question" : "Problem statement"}
						</p>
						<h1 className="text-xl font-semibold text-forge-text">
							{mockMode ? questionLabel ?? "Question" : problem.title}
						</h1>
						{!mockMode && <p className={`font-mono text-sm mt-1 ${diffClass(difficulty)}`}>{difficulty}</p>}
					</div>
					{solved && (
						<span className="forge-chip text-forge-accent border-forge-accent/30">
							<BsCheck2Circle className="inline mr-1" /> Accepted
						</span>
					)}
				</div>

				{!mockMode && !loading && occurrences.length > 0 && (
					<div className="forge-panel p-4 mb-6 space-y-3">
						<p className="forge-label">Sourced occurrences</p>
						{occurrences.map((o, i) => (
							<div key={i} className="text-sm border-t border-forge-border/50 pt-3 first:border-0 first:pt-0">
								<div className="flex flex-wrap items-center gap-2 mb-1">
									<TierBadge tier={o.confidence_tier} />
									<span className="font-mono text-xs text-forge-muted">
										{o.oa_companies.name} · {o.year} · {o.season ?? o.round_type}
									</span>
								</div>
								<p className="text-forge-muted text-xs leading-relaxed">
									{o.source_notes ?? "—"}
									{o.source_url && (
										<>
											{" "}
											<a
												href={o.source_url}
												target="_blank"
												rel="noreferrer"
												className="text-forge-blue hover:underline"
											>
												source ↗
											</a>
										</>
									)}
								</p>
							</div>
						))}
					</div>
				)}

				{mockMode && (
					<div className="forge-panel p-4 mb-6 border-forge-accent/20">
						<p className="font-mono text-xs text-forge-accent">
							{"// Mock OA mode — problem metadata hidden until debrief"}
						</p>
					</div>
				)}

				<div className="prose-forge text-sm">
					<div dangerouslySetInnerHTML={{ __html: problem.problemStatement }} />
				</div>

				<div className="mt-6 space-y-4">
					<p className="forge-label">Examples</p>
					{problem.examples.map((example, index) => (
						<div key={example.id} className="example-card">
							<p className="font-mono text-xs text-forge-muted mb-2">Example {index + 1}</p>
							<pre>
								<strong>Input:</strong> {example.inputText}
								{"\n"}
								<strong>Output:</strong> {example.outputText}
								{example.explanation && (
									<>
										{"\n"}
										<strong>Explanation:</strong> {example.explanation}
									</>
								)}
							</pre>
						</div>
					))}
				</div>

				<div className="mt-8 pb-8">
					<p className="forge-label mb-2">Constraints</p>
					<ul className="text-sm text-forge-muted ml-4 list-disc">
						<div dangerouslySetInnerHTML={{ __html: problem.constraints }} />
					</ul>
				</div>
			</div>
		</div>
	);
}
