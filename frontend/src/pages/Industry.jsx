import { useTheme } from "../context/ThemeContext";
export default function Industry(){
    const {theme} = useTheme();
    return(
        <div className="text-white text-center">
            <div className="section-min-height">
                <h1>Industries</h1>
            </div>
            <div id="sections" className="text-2xl">
                <div id="healthcare" className="section-min-height">
                    <h2>Healthcare</h2>
                </div>

                <div id="fintech" className="section-min-height">
                    <h2>Finance & Fintech</h2>
                </div>

                <div id="ecommerce" className="section-min-height">
                    <h2>E-commerce</h2>
                </div>

                <div id="smb" className="section-min-height">
                    <h2>SMBs</h2>
                </div>

                <div id="agriculture" className="section-min-height">
                    <h2>Agriculture</h2>
                </div>

                <div id="technology" className="section-min-height">
                    <h2>Technology</h2>
                    </div>

                <div id="nonprofit" className="section-min-height">
                    <h2>Non Profit</h2>
                    </div>

                <div id="government" className="section-min-height">
                    <h2>Government</h2>
                </div>

            </div>
        </div>
    );
}