"use client";

import { useState } from "react";

export default function Home() {
  const [formData, setFormData] = useState({
    pH: "7.0",
    Temperature: "25.0",
    DO: "5.0",
    BOD: "2.0",
    TSS: "10.0",
    Fecal_Coliform: "100.0",
  });
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/predict';
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to fetch prediction");
      }

      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  // Helper to format the class name for CSS
  const getStatusClass = (prediction) => {
    if (!prediction) return "";
    const clean = prediction.toLowerCase().replace(/_/g, '-').replace(/\s+/g, '-');
    return `class-${clean}`;
  };

  const getBgClass = (prediction) => {
    if (!prediction) return "";
    const clean = prediction.toLowerCase().replace(/_/g, '-').replace(/\s+/g, '-');
    return `bg-${clean}`;
  };

  return (
    <div className="container">
      <header className="header">
        <h1>WQI Prediction Dashboard</h1>
        <p>Powered by XGBoost & Vercel Serverless Functions</p>
      </header>

      <main className="dashboard">
        <section className="glass-panel">
          <h2>Input Parameters</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              
              <div className="input-group">
                <label>pH Level</label>
                <div className="input-wrapper">
                  <input type="number" step="0.01" name="pH" value={formData.pH} onChange={handleInputChange} required />
                  <span className="input-unit">pH</span>
                </div>
              </div>

              <div className="input-group">
                <label>Temperature</label>
                <div className="input-wrapper">
                  <input type="number" step="0.1" name="Temperature" value={formData.Temperature} onChange={handleInputChange} required />
                  <span className="input-unit">°C</span>
                </div>
              </div>

              <div className="input-group">
                <label>Dissolved Oxygen (DO)</label>
                <div className="input-wrapper">
                  <input type="number" step="0.01" name="DO" value={formData.DO} onChange={handleInputChange} required />
                  <span className="input-unit">mg/L</span>
                </div>
              </div>

              <div className="input-group">
                <label>Biochemical Oxygen Demand (BOD)</label>
                <div className="input-wrapper">
                  <input type="number" step="0.01" name="BOD" value={formData.BOD} onChange={handleInputChange} required />
                  <span className="input-unit">mg/L</span>
                </div>
              </div>

              <div className="input-group">
                <label>Total Suspended Solids (TSS)</label>
                <div className="input-wrapper">
                  <input type="number" step="0.01" name="TSS" value={formData.TSS} onChange={handleInputChange} required />
                  <span className="input-unit">mg/L</span>
                </div>
              </div>

              <div className="input-group">
                <label>Fecal Coliform</label>
                <div className="input-wrapper">
                  <input type="number" step="0.1" name="Fecal_Coliform" value={formData.Fecal_Coliform} onChange={handleInputChange} required />
                  <span className="input-unit">MPN/100mL</span>
                </div>
              </div>

            </div>
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? "Analyzing Chemistry..." : "Calculate WQI Suitability Class"}
            </button>
          </form>
          
          {error && (
            <div style={{ marginTop: '1rem', color: '#ef4444', textAlign: 'center' }}>
              Error: {error}
            </div>
          )}
        </section>

        <section className="glass-panel">
          <h2>Prediction Output</h2>
          
          {!result && !loading && (
            <div className="result-placeholder">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" style={{marginBottom: '1rem', opacity: 0.5}}>
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
              <p>Enter the water sample parameters<br/>and run the analysis.</p>
            </div>
          )}

          {loading && (
            <div className="result-placeholder">
              <div className="loader" style={{marginBottom: '1rem', border: '3px solid rgba(255,255,255,0.1)', borderTop: '3px solid var(--accent)', borderRadius: '50%', width: '40px', height: '40px', animation: 'spin 1s linear infinite'}}></div>
              <p>Running Neural Network Inference...</p>
              <style jsx>{`
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
              `}</style>
            </div>
          )}

          {result && (
            <div className="result-card">
              <div className={`status-indicator ${getBgClass(result.prediction)}`}>
                <span className="metric-label" style={{textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '2px'}}>Suitability Class</span>
                <span className={`status-text ${getStatusClass(result.prediction)}`}>
                  {result.prediction.replace('_', ' ')}
                </span>
              </div>

              <div className="metrics-list">
                <div className="metric-item">
                  <span className="metric-label">Engineered DO/Temp Ratio</span>
                  <span className="metric-value">{result.engineered_features?.DO_Temp_Ratio}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Engineered pH Deviation</span>
                  <span className="metric-value">| {result.engineered_features?.pH_Deviation} |</span>
                </div>
                {result.probabilities && result.probabilities[result.prediction] && (
                  <div className="metric-item">
                    <span className="metric-label">Confidence Score</span>
                    <span className="metric-value">{result.probabilities[result.prediction]}%</span>
                  </div>
                )}
              </div>
              
              <div className="class-legend">
                <h4>Water Quality Scale</h4>
                <div className="legend-items">
                  <span className="legend-badge bg-excellent">Excellent</span>
                  <span className="legend-badge bg-good">Good</span>
                  <span className="legend-badge bg-fair">Fair</span>
                  <span className="legend-badge bg-poor">Poor</span>
                  <span className="legend-badge bg-high-risk">High Risk</span>
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
