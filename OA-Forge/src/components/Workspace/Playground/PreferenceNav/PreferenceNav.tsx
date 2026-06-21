import { useState, useEffect } from "react";
import { AiOutlineFullscreen, AiOutlineFullscreenExit, AiOutlineSetting } from "react-icons/ai";
import { ISettings } from "../Playground";
import SettingsModal from "@/components/Modals/SettingsModal";

type PreferenceNavProps = {
	settings: ISettings;
	setSettings: React.Dispatch<React.SetStateAction<ISettings>>;
};

const PreferenceNav: React.FC<PreferenceNavProps> = ({ setSettings, settings }) => {
	const [isFullScreen, setIsFullScreen] = useState(false);

	const handleFullScreen = () => {
		if (isFullScreen) document.exitFullscreen();
		else document.documentElement.requestFullscreen();
		setIsFullScreen(!isFullScreen);
	};

	useEffect(() => {
		function exitHandler() {
			setIsFullScreen(Boolean(document.fullscreenElement));
		}
		document.addEventListener("fullscreenchange", exitHandler);
		return () => document.removeEventListener("fullscreenchange", exitHandler);
	}, []);

	return (
		<div className='flex items-center justify-between bg-dark-layer-2 h-11 w-full border-b border-forge-border/60'>
			<div className='flex items-center ml-3'>
				<span className='font-mono text-xs px-3 py-1 rounded-md border border-forge-accent/40 bg-forge-accent/10 text-forge-accent'>
					C++17
				</span>
			</div>

			<div className='flex items-center m-2'>
				<button
					className='preferenceBtn group'
					onClick={() => setSettings({ ...settings, settingsModalIsOpen: true })}
				>
					<div className='h-4 w-4 text-dark-gray-6 font-bold text-lg'>
						<AiOutlineSetting />
					</div>
					<div className='preferenceBtn-tooltip'>Settings</div>
				</button>

				<button className='preferenceBtn group' onClick={handleFullScreen}>
					<div className='h-4 w-4 text-dark-gray-6 font-bold text-lg'>
						{!isFullScreen ? <AiOutlineFullscreen /> : <AiOutlineFullscreenExit />}
					</div>
					<div className='preferenceBtn-tooltip'>Full Screen</div>
				</button>
			</div>
			{settings.settingsModalIsOpen && <SettingsModal settings={settings} setSettings={setSettings} />}
		</div>
	);
};
export default PreferenceNav;
