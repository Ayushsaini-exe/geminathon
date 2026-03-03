import { useState, useRef } from 'react';
import { Camera, UploadCloud, AlertCircle, CheckCircle, RefreshCcw } from 'lucide-react';
import { uploadScannerImage } from '../../api';
import './Scanner.css';

export default function GenericScanner({ title, description, endpoint, isPesticide }) {
    const [imageStr, setImageStr] = useState(null);
    const [fileObj, setFileObj] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setImageStr(URL.createObjectURL(file));
            setFileObj(file);
            setResult(null);
            setError(null);
        }
    };

    const simulateAnalysis = async () => {
        if (!fileObj) return;
        setLoading(true);
        setError(null);

        try {
            const data = await uploadScannerImage(fileObj, isPesticide);

            // Map generic FastAPI response to UI state
            if (isPesticide) {
                setResult({
                    status: data.is_genuine ? 'verified' : 'unverified',
                    message: data.message || (data.is_genuine ? 'Pesticide is verified.' : 'Could not verify pesticide.'),
                    details: [
                        `Manufacturer: ${data.manufacturer || 'Unknown'}`,
                        `Active Ingredient: ${data.active_ingredient || 'Unknown'}`
                    ]
                });
            } else {
                setResult({
                    disease: data.disease_name || data.classification || 'Unknown Disease',
                    confidence: data.confidence ? `${(data.confidence * 100).toFixed(1)}%` : 'N/A',
                    treatment: data.treatment_plan || data.recommendation || 'No treatment plan available.'
                });
            }
        } catch (err) {
            setError(err.message);
            // Fallback to mock for testing if no backend is running
            if (isPesticide) {
                setResult({
                    status: 'verified',
                    message: 'MOCK: This pesticide batch (B-9021) is verified against the CIBRC database.',
                    details: ['Manufacturer: AgroChem India', 'Active Ingredient: Chlorpyrifos 20% EC']
                });
            } else {
                setResult({
                    disease: 'MOCK: Tomato Early Blight',
                    confidence: '94%',
                    treatment: 'Apply Mancozeb 75% WP.'
                });
            }
        } finally {
            setLoading(false);
        }
    };

    const resetScanner = () => {
        setImageStr(null);
        setFileObj(null);
        setResult(null);
        setError(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    return (
        <div className="scanner-page">
            <div className="scanner-header">
                <h2>{title}</h2>
                <p>{description}</p>
            </div>

            <div className="scanner-content">
                <div className="camera-view glass-panel">
                    {!imageStr ? (
                        <div className="upload-prompt">
                            <Camera size={48} className="prompt-icon" />
                            <h3>Capture or Upload Image</h3>
                            <p>Take a clear photo for the AI to analyze.</p>

                            <div className="upload-actions">
                                <button className="btn-primary" onClick={() => fileInputRef.current?.click()}>
                                    <UploadCloud size={20} /> Choose File
                                </button>
                                <input
                                    type="file"
                                    accept="image/*"
                                    ref={fileInputRef}
                                    onChange={handleFileChange}
                                    hidden
                                />
                            </div>
                        </div>
                    ) : (
                        <div className="image-preview">
                            <img src={imageStr} alt="Captured" />
                            {!loading && !result && (
                                <div className="preview-overlay">
                                    <button className="btn-primary analyze-btn" onClick={simulateAnalysis}>
                                        {isPesticide ? 'Verify Authenticity' : 'Analyze Disease'}
                                    </button>
                                    <button className="btn-secondary" onClick={resetScanner}>Retake</button>
                                </div>
                            )}
                            {loading && (
                                <div className="scanning-overlay">
                                    <div className="scanner-line"></div>
                                    <p>Processing via Gemini AI...</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {result && (
                    <div className="results-panel glass-panel">
                        <div className="results-header">
                            {isPesticide ? (
                                <><CheckCircle color="var(--color-success)" size={28} /> <h3>Verification Result</h3></>
                            ) : (
                                <><AlertCircle color="var(--color-warning)" size={28} /> <h3>Diagnosis Complete</h3></>
                            )}
                        </div>

                        <div className="results-body">
                            {isPesticide ? (
                                <>
                                    <div className="result-status success">{result.status.toUpperCase()}</div>
                                    <p className="result-msg">{result.message}</p>
                                    <ul className="details-list">
                                        {result.details.map((d, i) => <li key={i}>{d}</li>)}
                                    </ul>
                                </>
                            ) : (
                                <>
                                    <div className="disease-name">{result.disease}</div>
                                    <div className="confidence-badge">Confidence: {result.confidence}</div>
                                    <div className="treatment-plan">
                                        <h4>Recommended Treatment:</h4>
                                        <p>{result.treatment}</p>
                                    </div>
                                </>
                            )}
                        </div>

                        <button className="btn-outline reset-btn" onClick={resetScanner}>
                            <RefreshCcw size={16} /> Scan Another
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
