import Shell, { TierBadge } from "@/components/layout/Shell";
import useHasMounted from "@/hooks/useHasMounted";
import { useRouter } from "next/router";
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { toast } from "react-toastify";
import { ConfidenceTier } from "@/lib/types/oa";

type SessionQuestion = {
	order: number;
	slug: string;
	title: string | null;
	difficulty: string;
	verdict: string | null;
	confidenceTier?: ConfidenceTier;
};

type SessionData = {
	id: string;
	status: string;
	durationMinutes: number;
	startedAt: string;
	company: { slug: string; name: string };
};

export default function MockOAPage() {
	const router = useRouter();
	const { sessionId } = router.query;
	const hasMounted = useHasMounted();

	const [session, setSession] = useState<SessionData | null>(null);
	const [questions, setQuestions] = useState<SessionQuestion[]>([]);
	const [loading, setLoading] = useState(true);
	const [secondsLeft, setSecondsLeft] = useState(0);
	const [currentIndex, setCurrentIndex] = useState(0);
	const [completed, setCompleted] = useState(false);

	const loadSession = useCallback(async () => {
		if (!sessionId || typeof sessionId !== "string") return;
		setLoading(true);
		try {
			const res = await fetch(`/api/mock-oa/session?sessionId=${sessionId}`);
			const data = await res.json();
			if (!res.ok) throw new Error(data.error);

			setSession(data.session);
			setQuestions(data.questions);

			const started = new Date(data.session.startedAt).getTime();
			const end = started + data.session.durationMinutes * 60 * 1000;
			const remaining = Math.max(0, Math.floor((end - Date.now()) / 1000));
			setSecondsLeft(remaining);

			if (data.session.status === "completed" || remaining === 0) {
				setCompleted(true);
			}
		} catch (e) {
			toast.error(e instanceof Error ? e.message : "Failed to load session");
		} finally {
			setLoading(false);
		}
	}, [sessionId]);

	useEffect(() => {
		loadSession();
	}, [loadSession]);

	useEffect(() => {
		if (completed || secondsLeft <= 0) return;
		const t = setInterval(() => {
			setSecondsLeft((s) => {
				if (s <= 1) {
					setCompleted(true);
					return 0;
				}
				return s - 1;
			});
		}, 1000);
		return () => clearInterval(t);
	}, [completed, secondsLeft]);

	const formatTime = (s: number) => {
		const h = Math.floor(s / 3600);
		const m = Math.floor((s % 3600) / 60);
		const sec = s % 60;
		return `${h.toString().padStart(2, "0")}:${m.toString().padStart(2, "0")}:${sec
			.toString()
			.padStart(2, "0")}`;
	};

	if (!hasMounted || loading) {
		return (
			<Shell>
				<div className="flex items-center justify-center min-h-[60vh] font-mono text-forge-muted">
					Loading mock OA session…
				</div>
			</Shell>
		);
	}

	if (!session) {
		return (
			<Shell>
				<div className="max-w-lg mx-auto mt-20 text-center space-y-4">
					<p className="text-forge-danger">Session not found</p>
					<Link href="/" className="forge-btn-ghost inline-flex">
						← Back to bank
					</Link>
				</div>
			</Shell>
		);
	}

	const current = questions[currentIndex];
	const active = !completed;

	return (
		<Shell>
			<div className="border-b border-forge-border bg-forge-surface/90">
				<div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between gap-4">
					<div>
						<p className="forge-label">{session.company.name} · mock OA</p>
						<p className="font-mono text-2xl text-forge-accent tabular-nums">{formatTime(secondsLeft)}</p>
					</div>
					<div className="text-right font-mono text-sm text-forge-muted">
						Question {currentIndex + 1} / {questions.length}
					</div>
				</div>
			</div>

			<div className="max-w-2xl mx-auto px-4 py-12">
				{completed ? (
					<div className="space-y-8">
						<div>
							<p className="forge-label mb-2">Debrief</p>
							<h1 className="text-2xl font-semibold">Mock OA complete</h1>
							<p className="text-forge-muted mt-2 text-sm">
								Time ended. Titles and tiers revealed below — same transparency you wanted
								post-assessment.
							</p>
						</div>

						<ul className="space-y-3">
							{questions.map((q) => (
								<li
									key={q.slug}
									className="forge-panel p-4 flex flex-wrap items-center justify-between gap-3"
								>
									<div>
										<p className="font-mono text-xs text-forge-muted mb-1">Q{q.order}</p>
										<p className="font-medium">{q.title}</p>
										<div className="flex items-center gap-2 mt-2">
											<span className="text-xs text-forge-muted">{q.difficulty}</span>
											{q.confidenceTier && <TierBadge tier={q.confidenceTier} />}
										</div>
									</div>
									<Link
										href={`/mock/${sessionId}/question/${q.order}`}
										className="forge-btn-ghost text-xs"
									>
										Review →
									</Link>
								</li>
							))}
						</ul>

						<Link href="/" className="forge-btn-primary inline-flex">
							Back to problem bank
						</Link>
					</div>
				) : (
					<div className="forge-panel p-8 shadow-glow border-forge-accent/10">
						<p className="forge-label mb-2">Active question</p>
						<h2 className="text-2xl font-semibold font-mono text-forge-text mb-1">
							Question {current?.order}
						</h2>
						<p className="text-forge-muted text-sm mb-6">
							Title, topic, difficulty, and source metadata are hidden until debrief.
						</p>
						<Link
							href={`/mock/${sessionId}/question/${current?.order}`}
							className="forge-btn-primary"
						>
							Open editor →
						</Link>

						<div className="flex gap-3 mt-8">
							<button
								disabled={currentIndex === 0}
								onClick={() => setCurrentIndex((i) => i - 1)}
								className="forge-btn-ghost disabled:opacity-40"
							>
								← Previous
							</button>
							<button
								disabled={currentIndex >= questions.length - 1}
								onClick={() => setCurrentIndex((i) => i + 1)}
								className="forge-btn-ghost disabled:opacity-40"
							>
								Next →
							</button>
						</div>
					</div>
				)}

				{active && (
					<p className="text-center font-mono text-[10px] text-forge-muted mt-8 uppercase tracking-widest">
						Timer cannot pause · tab away at your own risk
					</p>
				)}
			</div>
		</Shell>
	);
}
