import { useState, useEffect } from "react";
import PreferenceNav from "./PreferenceNav/PreferenceNav";
import Split from "react-split";
import CodeMirror from "@uiw/react-codemirror";
import { vscodeDark } from "@uiw/codemirror-theme-vscode";
import EditorFooter from "./EditorFooter";
import { Problem } from "@/utils/types/problem";
import { toast } from "react-toastify";
import useLocalStorage from "@/hooks/useLocalStorage";
import { useRouter } from "next/router";
import { markSolved } from "@/lib/progress";
import { cppStarters } from "@/lib/cppTemplates";

type PlaygroundProps = {
	problem: Problem;
	setSuccess: React.Dispatch<React.SetStateAction<boolean>>;
	setSolved: React.Dispatch<React.SetStateAction<boolean>>;
};

export interface ISettings {
	fontSize: string;
	settingsModalIsOpen: boolean;
	dropdownIsOpen: boolean;
}

const Playground: React.FC<PlaygroundProps> = ({ problem, setSuccess, setSolved }) => {
	const [activeTestCaseId, setActiveTestCaseId] = useState<number>(0);
	const [userCode, setUserCode] = useState<string>(cppStarters[problem.id] ?? problem.starterCode);
	const [fontSize, setFontSize] = useLocalStorage("oa-forge-fontSize", "14px");

	const [settings, setSettings] = useState<ISettings>({
		fontSize: fontSize,
		settingsModalIsOpen: false,
		dropdownIsOpen: false,
	});

	const {
		query: { pid },
	} = useRouter();
	const problemSlug = typeof pid === "string" ? pid : problem.id;

	const handleSubmit = async () => {
		try {
			const res = await fetch("/api/judge", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ slug: problemSlug, code: userCode, language: "cpp" }),
			});
			const result = await res.json();

			if (result.passed) {
				toast.success("Accepted — all test cases passed!", {
					position: "top-center",
					autoClose: 3000,
					theme: "dark",
				});
				setSuccess(true);
				setTimeout(() => setSuccess(false), 4000);
				markSolved(problemSlug);
				setSolved(true);
			} else {
				toast.error(result.verdict === "Wrong Answer" ? "Wrong Answer" : result.message ?? "Failed", {
					position: "top-center",
					autoClose: 3000,
					theme: "dark",
				});
			}
		} catch (error: unknown) {
			const message = error instanceof Error ? error.message : "Submit failed";
			toast.error(message, {
				position: "top-center",
				autoClose: 3000,
				theme: "dark",
			});
		}
	};

	useEffect(() => {
		const key = `oa-code-cpp-${problemSlug}`;
		const code = localStorage.getItem(key);
		setUserCode(code ? JSON.parse(code) : cppStarters[problem.id] ?? problem.starterCode);
	}, [problem.id, problemSlug, problem.starterCode]);

	const onChange = (value: string) => {
		setUserCode(value);
		localStorage.setItem(`oa-code-cpp-${problemSlug}`, JSON.stringify(value));
	};

	return (
		<div className='flex flex-col bg-forge-surface relative overflow-x-hidden'>
			<PreferenceNav settings={settings} setSettings={setSettings} />

			<Split className='h-[calc(100vh-94px)]' direction='vertical' sizes={[60, 40]} minSize={60}>
				<div className='w-full overflow-auto'>
					<CodeMirror
						value={userCode}
						theme={vscodeDark}
						onChange={onChange}
						style={{ fontSize: settings.fontSize }}
					/>
				</div>
				<div className='w-full px-5 overflow-auto'>
					<div className='flex h-10 items-center space-x-6'>
						<div className='relative flex h-full flex-col justify-center cursor-pointer'>
							<div className='text-sm font-medium leading-5 text-white'>Testcases</div>
							<hr className='absolute bottom-0 h-0.5 w-full rounded-full border-none bg-forge-accent' />
						</div>
					</div>

					<div className='flex'>
						{problem.examples.map((example, index) => (
							<div className='mr-2 items-start mt-2 ' key={example.id} onClick={() => setActiveTestCaseId(index)}>
								<div className='flex flex-wrap items-center gap-y-4'>
									<div
										className={`font-medium items-center transition-all focus:outline-none inline-flex bg-dark-fill-3 hover:bg-dark-fill-2 relative rounded-lg px-4 py-1 cursor-pointer whitespace-nowrap
										${activeTestCaseId === index ? "text-forge-accent" : "text-gray-500"}
									`}
									>
										Case {index + 1}
									</div>
								</div>
							</div>
						))}
					</div>

					<div className='font-semibold my-4'>
						<p className='text-sm font-medium mt-4 text-white'>Input:</p>
						<div className='w-full cursor-text rounded-lg border px-3 py-[10px] bg-dark-fill-3 border-forge-border/40 text-white mt-2 font-mono text-sm'>
							{problem.examples[activeTestCaseId].inputText}
						</div>
						<p className='text-sm font-medium mt-4 text-white'>Output:</p>
						<div className='w-full cursor-text rounded-lg border px-3 py-[10px] bg-dark-fill-3 border-forge-border/40 text-white mt-2 font-mono text-sm'>
							{problem.examples[activeTestCaseId].outputText}
						</div>
					</div>
				</div>
			</Split>
			<EditorFooter handleSubmit={handleSubmit} />
		</div>
	);
};
export default Playground;
