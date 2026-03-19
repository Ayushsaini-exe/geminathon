import { useState, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/client';

export default function DiseaseScanner() {
  const { user } = useAuth();
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState('');
  const [crop, setCrop] = useState('Tomato');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileRef = useRef(null);

  const handleFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setResult(null);
    setError('');
    const reader = new FileReader();
    reader.onload = () => {
      setPreview(reader.result);
      setImage(reader.result.split(',')[1]); // base64
    };
    reader.readAsDataURL(file);
  };

  const analyze = async () => {
    if (!image) return;
    setLoading(true);
    setError('');
    try {
      const data = await api.post('/api/vision/detect', {
        farmer_id: user?.farmer_id,
        image_base64: image,
        crop_type: crop,
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="page-header">
        <div>
          <div className="page-title">Disease Scanner 🔬</div>
          <div className="page-subtitle">Upload a leaf photo for AI-powered disease detection</div>
        </div>
      </div>
      <div className="page-content">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, alignItems: 'start' }}>
          <div>
            <div className="card" style={{ marginBottom: 16 }}>
              <div className="form-group" style={{ marginBottom: 16 }}>
                <label style={{ color: 'var(--earth-900)', fontWeight: 600 }}>Crop Type</label>
                <select className="form-select" value={crop} onChange={e => setCrop(e.target.value)}
                  style={{ background: 'var(--gray-50)', color: 'var(--earth-900)', border: '1px solid var(--gray-300)' }}>
                  {['Tomato','Potato','Corn','Apple','Grape','Cherry','Peach','Pepper','Strawberry'].map(c =>
                    <option key={c} value={c}>{c}</option>
                  )}
                </select>
              </div>

              <div
                className={`upload-zone ${preview ? 'active' : ''}`}
                onClick={() => fileRef.current.click()}
              >
                <input ref={fileRef} type="file" accept="image/*" hidden onChange={handleFile} />
                {preview ? (
                  <div className="upload-preview">
                    <img src={preview} alt="Selected leaf" />
                  </div>
                ) : (
                  <>
                    <div className="upload-icon">📷</div>
                    <div className="upload-text">Click to upload a leaf image</div>
                  </>
                )}
              </div>

              <button
                className="btn btn-green"
                style={{ width: '100%', marginTop: 16, justifyContent: 'center' }}
                onClick={analyze}
                disabled={!image || loading}
              >
                {loading ? <><span className="spinner" /> Analyzing...</> : '🔬 Analyze Image'}
              </button>
            </div>
          </div>

          <div>
            {error && <div className="error-message" style={{ background: 'var(--red-100)', color: 'var(--red-500)', border: '1px solid var(--red-500)' }}>{error}</div>}
            {result && (
              <div className="fade-in">
                <div className="result-section">
                  <div className="result-header">🦠 Diagnosis Result</div>
                  <div className="result-body">
                    <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
                      <span className={`badge ${result.risk_level === 'high' ? 'red' : result.risk_level === 'medium' ? 'orange' : 'green'}`}>
                        Risk: {result.risk_level}
                      </span>
                      <span className="badge blue">Confidence: {(result.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <h3 style={{ marginBottom: 8 }}>{result.disease}</h3>
                  </div>
                </div>
                <div className="result-section">
                  <div className="result-header">💊 Treatment Plan</div>
                  <div className="result-body" style={{ whiteSpace: 'pre-wrap' }}>
                    {result.treatment_plan}
                  </div>
                </div>
              </div>
            )}
            {!result && !error && (
              <div className="empty-state">
                <div className="empty-icon">🌿</div>
                <div className="empty-text">Upload a leaf image to get started</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
