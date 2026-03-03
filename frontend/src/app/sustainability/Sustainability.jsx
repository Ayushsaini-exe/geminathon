import { useState } from 'react';
import { Leaf, Award, Download, TrendingUp, AlertTriangle } from 'lucide-react';
import { generateSustainabilityReport } from '../../api';
import './Sustainability.css';

export default function Sustainability() {
    const [isGenerating, setIsGenerating] = useState(false);

    const generateReport = async () => {
        setIsGenerating(true);
        try {
            const blob = await generateSustainabilityReport();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'AgroFix_Sustainability_Report.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            alert("Failed to generate report: Ensure backend is running.");
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="esg-container">
            <div className="esg-header">
                <div>
                    <h2>Sustainability Profile</h2>
                    <p>Your Environmental, Social, and Governance (ESG) standing.</p>
                </div>
                <button className="btn-primary" onClick={generateReport} disabled={isGenerating}>
                    {isGenerating ? <span className="spinner small-spinner"></span> : <Download size={18} />}
                    {isGenerating ? ' Generating...' : ' Generate PDF Report'}
                </button>
            </div>

            <div className="score-hero glass-panel">
                <div className="score-circle">
                    <svg viewBox="0 0 36 36" className="circular-chart">
                        <path className="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                        <path className="circle" strokeDasharray="85, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                        <text x="18" y="20.35" className="percentage">85</text>
                    </svg>
                </div>
                <div className="score-details">
                    <h3>Excellent Rating</h3>
                    <p>Your farm is in the top 15% of sustainable practices in your region. This profile is ready for Green Loan applications.</p>
                    <div className="trend-badge positive">
                        <TrendingUp size={16} /> +4 Points since last quarter
                    </div>
                </div>
            </div>

            <div className="pillars-grid">
                <div className="pillar-card glass-panel">
                    <div className="pillar-header">
                        <Leaf className="pillar-icon env" size={24} />
                        <h4>Environmental</h4>
                        <span className="score">90/100</span>
                    </div>
                    <ul className="impact-list">
                        <li><Award size={16} className="text-success" /> Reduced chemical pesticide use by 30%</li>
                        <li><Award size={16} className="text-success" /> Integrated organic compost (SHC Rec)</li>
                        <li><AlertTriangle size={16} className="text-warning" /> Water usage in Sector 4 remains high</li>
                    </ul>
                </div>

                <div className="pillar-card glass-panel">
                    <div className="pillar-header">
                        <div className="pillar-icon soc">👥</div>
                        <h4>Social</h4>
                        <span className="score">82/100</span>
                    </div>
                    <ul className="impact-list">
                        <li><Award size={16} className="text-success" /> Zero safety incidents reported</li>
                        <li><Award size={16} className="text-success" /> Authenticated 100% of agrochemicals</li>
                    </ul>
                </div>

                <div className="pillar-card glass-panel">
                    <div className="pillar-header">
                        <div className="pillar-icon gov">🏛️</div>
                        <h4>Governance</h4>
                        <span className="score">80/100</span>
                    </div>
                    <ul className="impact-list">
                        <li><Award size={16} className="text-success" /> Up-to-date Soil Health logs</li>
                        <li><Award size={16} className="text-success" /> Digital Twin monitoring active</li>
                    </ul>
                </div>
            </div>
        </div>
    );
}
