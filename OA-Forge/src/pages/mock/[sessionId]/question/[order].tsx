import Shell from "@/components/layout/Shell";
import Workspace from "@/components/Workspace/Workspace";
import { getLocalMockSession } from "@/lib/localBank";
import { supabase } from "@/supabase/supabase";
import { problems } from "@/utils/problems";
import { Problem } from "@/utils/types/problem";
import { GetServerSideProps } from "next";

type MockQuestionPageProps = {
	problem: Problem;
};

export default function MockQuestionPage({ problem }: MockQuestionPageProps) {
	return (
		<Shell problemPage>
			<Workspace problem={problem} />
		</Shell>
	);
}

export const getServerSideProps: GetServerSideProps<MockQuestionPageProps> = async ({ params }) => {
	const sessionId = String(params?.sessionId ?? "");
	const order = Number(params?.order ?? 0);
	let slug: string | null = null;

	if (sessionId.startsWith("local-")) {
		const session = getLocalMockSession(sessionId);
		slug = session?.questions.find((q) => q.order === order)?.slug ?? null;
	} else {
		const { data } = await supabase
			.from("oa_session_questions")
			.select("question_order, oa_questions ( slug )")
			.eq("session_id", sessionId)
			.eq("question_order", order)
			.single();
		const question = data?.oa_questions as unknown as { slug: string } | null;
		slug = question?.slug ?? null;
	}

	if (!slug || !problems[slug]) return { notFound: true };

	const problem = { ...problems[slug] };
	problem.handlerFunction = problem.handlerFunction.toString();
	return { props: { problem } };
};
