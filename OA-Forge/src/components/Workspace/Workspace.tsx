import { useState } from "react";
import Split from "react-split";
import OProblemPanel from "./OProblemPanel";
import Playground from "./Playground/Playground";
import { Problem } from "@/utils/types/problem";
import Confetti from "react-confetti";
import useWindowSize from "@/hooks/useWindowSize";
import { useRouter } from "next/router";

type WorkspaceProps = {
	problem: Problem;
};

const Workspace: React.FC<WorkspaceProps> = ({ problem }) => {
	const { width, height } = useWindowSize();
	const [success, setSuccess] = useState(false);
	const [solved, setSolved] = useState(false);
	const router = useRouter();
	const mockSession = (router.query.mockSession || router.query.sessionId) as string | undefined;
	const qOrder = (router.query.q || router.query.order) as string | undefined;
	const mockMode = Boolean(mockSession);

	return (
		<Split className="split" minSize={0}>
			<OProblemPanel
				problem={problem}
				mockMode={mockMode}
				questionLabel={mockMode && qOrder ? `Question ${qOrder}` : undefined}
			/>
			<div className="bg-forge-elevated">
				<Playground problem={problem} setSuccess={setSuccess} setSolved={setSolved} />
				{success && (
					<Confetti gravity={0.3} tweenDuration={4000} width={width - 1} height={height - 1} />
				)}
			</div>
		</Split>
	);
};
export default Workspace;
