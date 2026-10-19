"use client";

import { useState } from "react";

const PRESETS = [
  {
    id: "sibalom",
    label: "Class A: Sibalom Baseline",
    badge: "Municipal Standard",
    values: { pH: "7.4", Temperature: "27.5", DO: "6.8", BOD: "3.2", TSS: "35", Fecal_Coliform: "80" }
  },
  {
    id: "pristine",
    label: "Class AA: Headwater",
    badge: "Pristine",
    values: { pH: "7.2", Temperature: "26.0", DO: "8.2", BOD: "1.0", TSS: "12", Fecal_Coliform: "8" }
  },
  {
    id: "recreational",
    label: "Class B: Recreational",
    badge: "Bathing / Swimming",
    values: { pH: "7.8", Temperature: "28.5", DO: "5.4", BOD: "4.8", TSS: "50", Fecal_Coliform: "160" }
  },
  {
    id: "runoff",
    label: "Class C: Agrarian Runoff",
    badge: "Irrigation / Fishery",
    values: { pH: "8.1", Temperature: "29.8", DO: "4.5", BOD: "8.2", TSS: "92", Fecal_Coliform: "410" }
  },
  {
    id: "high_risk",
    label: "Class D: Urban Contaminated",
    badge: "High Risk",
    values: { pH: "6.1", Temperature: "31.5", DO: "2.3", BOD: "16.5", TSS: "155", Fecal_Coliform: "2800" }
  },
  {
    id: "knn_test",
    label: "Field Only (KNN Impute)",
    badge: "Auto-Impute Lab",
    values: { pH: "7.3", Temperature: "28.0", DO: "6.5", BOD: "N/A", TSS: "N/A", Fecal_Coliform: "N/A" }
  }
];

const PARAM_CONFIG = [
  {
    key: "pH",
    symbol: "pH",
    name: "Potential of Hydrogen",
    unit: "pH",
    category: "field",
    hint: "DENR Standard: 6.5 – 9.0",
    standardDisplay: "6.5 – 9.0",
    check: (v) => {
      const n = parseFloat(v);
      if (isNaN(n) || String(v).trim().toUpperCase() === "N/A") return "impute";
      return (n >= 6.5 && n <= 9.0) ? "pass" : "fail";
    }
  },
  {
    key: "Temperature",
    symbol: "T°",
    name: "Water Temperature",
    unit: "°C",
    category: "field",
    hint: "DENR Standard: 25.0 – 31.0 °C",
    standardDisplay: "25.0 – 31.0 °C",
    check: (v) => {
      const n = parseFloat(v);
      if (isNaN(n) || String(v).trim().toUpperCase() === "N/A") return "impute";
      return (n >= 25.0 && n <= 31.0) ? "pass" : "fail";
    }
  },
  {
    key: "DO",
    symbol: "DO",
    name: "Dissolved Oxygen",
    unit: "mg/L",
    category: "field",
    hint: "DENR Standard: ≥ 5.0 mg/L",
    standardDisplay: "≥ 5.0 mg/L",
    check: (v) => {
      const n = parseFloat(v);
      if (isNaN(n) || String(v).trim().toUpperCase() === "N/A") return "impute";
      return n >= 5.0 ? "pass" : "fail";
    }
  },
  {
    key: "BOD",
    symbol: "BOD₅",
    name: "Biochemical Oxygen Demand",
    unit: "mg/L",
    category: "lab",
    hint: "DENR Standard: ≤ 7.0 mg/L",
    standardDisplay: "≤ 7.0 mg/L",
    check: (v) => {
      const n = parseFloat(v);
      if (isNaN(n) || String(v).trim().toUpperCase() === "N/A") return "impute";
      return n <= 7.0 ? "pass" : "fail";
    }
  },
  {
    key: "TSS",
    symbol: "TSS",
    name: "Total Suspended Solids",
    unit: "mg/L",
    category: "lab",
    hint: "DENR Standard: ≤ 80.0 mg/L",
    standardDisplay: "≤ 80.0 mg/L",
    check: (v) => {
      const n = parseFloat(v);
      if (isNaN(n) || String(v).trim().toUpperCase() === "N/A") return "impute";
      return n <= 80.0 ? "pass" : "fail";
    }
  },
  {
    key: "Fecal_Coliform",
    symbol: "FC",
    name: "Fecal Coliform",
    unit: "MPN/100mL",
    category: "lab",
    hint: "DENR Standard: ≤ 200 MPN",
    standardDisplay: "≤ 200 MPN/100mL",
    check: (v) => {
      const n = parseFloat(v);
      if (isNaN(n) || String(v).trim().toUpperCase() === "N/A") return "impute";
      return n <= 200 ? "pass" : "fail";
    }
  }
];

const CLASS_METADATA = {
  "Excellent": {
    className: "class-excellent",
    denrCode: "Class AA",
    title: "Excellent Suitability",
    description: "Meets pristine Class AA criteria. Public Water Supply Class I requiring only approved disinfection. Zero significant organic or microbial perturbation.",
    advisory: "Suitable for municipal consumption and ecological sanctuary preservation."
  },
  "Good": {
    className: "class-good",
    denrCode: "Class A",
    title: "Good Suitability",
    description: "Meets Class A criteria. Suitable for Public Water Supply Class II after conventional treatment (coagulation, sedimentation, filtration, disinfection).",
    advisory: "Complies with municipal water district intake guidelines for the Sibalom River basin."
  },
  "Fair": {
    className: "class-fair",
    denrCode: "Class B",
    title: "Fair Suitability",
    description: "Meets Class B criteria. Primary Contact Recreation (bathing, swimming, skin diving) and aquatic ecotourism.",
    advisory: "Safe for recreational immersion; requires full conventional treatment if extracted for drinking."
  },
  "Poor": {
    className: "class-poor",
    denrCode: "Class C",
    title: "Poor Suitability",
    description: "Meets Class C criteria. Fishery water for propagation of freshwater fish, secondary contact recreation (boating), and agricultural irrigation.",
    advisory: "Restricted from direct drinking use or swimming. Suitable for regulated irrigation."
  },
  "High Risk": {
    className: "class-high-risk",
    denrCode: "Class D",
    title: "High Risk / Degraded",
    description: "Severely deviates from DENR standards. Critical organic loading or excessive fecal coliform contamination.",
    advisory: "Requires immediate biological tracing, wastewater interception, and watershed remediation."
  }
};

export default function Home() {
  const [formData, setFormData] = useState({
    pH: "7.4",
    Temperature: "27.5",
    DO: "6.8",
    BOD: "3.2",
    TSS: "35",
    Fecal_Coliform: "80",
  });

  const [activePreset, setActivePreset] = useState("sibalom");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setActivePreset(null);
  };

  const applyPreset = (preset) => {
    setFormData(preset.values);
    setActivePreset(preset.id);
    setResult(null);
    setError(null);
  };

  const handleReset = () => {
    setFormData({
      pH: "N/A",
      Temperature: "N/A",
      DO: "N/A",
      BOD: "N/A",
      TSS: "N/A",
      Fecal_Coliform: "N/A",
    });
    setActivePreset(null);
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/predict";
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Prediction request failed.");
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to reach inference server.");
    } finally {
      setLoading(false);
    }
  };

  const currentClassInfo = result ? (CLASS_METADATA[result.prediction] || {
    className: "class-good",
    denrCode: "Class A",
    title: result.prediction,
    description: "Evaluated according to Weighted Arithmetic WQI standards.",
    advisory: "Refer to DENR DAO 2016-08 guidelines for specific parameter limits."
  }) : null;

  return (
    <>
      {/* Top Application Bar */}
      <header className="app-header">
        <div className="app-header-inner">
          <div className="brand-section">
            <div className="brand-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path>
                <path d="M9 13a3 3 0 0 0 6 0"></path>
              </svg>
            </div>
            <div className="brand-meta">
              <h1>HydroAnalytics WQI</h1>
              <p>Sibalom & Jalaur River Basin Water Quality Intelligence Platform</p>
            </div>
          </div>

          <div className="header-badges">
            <div className="system-badge">
              <span className="dot-live"></span>
              <span>DAO 2016-08 Standard</span>
            </div>
            <div className="system-badge">
              <span>KNN Imputer Active</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="workspace-container">
        <div className="dashboard-grid">
          
          {/* Left Panel: Inputs & Presets */}
          <section className="pro-card">
            <div className="card-header">
              <div className="card-title-group">
                <span className="card-title-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="4" y1="21" x2="4" y2="14"></line>
                    <line x1="4" y1="10" x2="4" y2="3"></line>
                    <line x1="12" y1="21" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12" y2="3"></line>
                    <line x1="20" y1="21" x2="20" y2="16"></line>
                    <line x1="20" y1="12" x2="20" y2="3"></line>
                    <line x1="1" y1="14" x2="7" y2="14"></line>
                    <line x1="9" y1="8" x2="15" y2="8"></line>
                    <line x1="17" y1="16" x2="23" y2="16"></line>
                  </svg>
                </span>
                <div>
                  <h2>Water Chemistry Telemetry</h2>
                  <p className="card-subtitle">Input in-situ and laboratory sample parameters</p>
                </div>
              </div>
            </div>

            <div className="card-body">
              {/* Presets Navigation */}
              <div className="presets-section">
                <div className="presets-label">Benchmark River Profiles (Quick Fill):</div>
                <div className="presets-wrapper">
                  {PRESETS.map((preset) => (
                    <button
                      key={preset.id}
                      type="button"
                      className={`preset-chip ${activePreset === preset.id ? "active" : ""}`}
                      onClick={() => applyPreset(preset)}
                    >
                      <span>{preset.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Input Form */}
              <form onSubmit={handleSubmit}>
                {/* Field In-Situ Parameters */}
                <div className="form-section-title">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="2" y1="12" x2="22" y2="12"></line>
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                  </svg>
                  Field In-Situ Sensor Telemetry
                </div>

                <div className="form-grid">
                  {PARAM_CONFIG.filter((p) => p.category === "field").map((param) => {
                    const status = param.check(formData[param.key]);
                    return (
                      <div className="param-field" key={param.key}>
                        <div className="field-top-row">
                          <div className="param-badge-name">
                            <span className="param-symbol">{param.symbol}</span>
                            <label className="param-label" htmlFor={param.key}>{param.name}</label>
                          </div>
                        </div>

                        <div className="field-input-box">
                          <input
                            id={param.key}
                            type="text"
                            inputMode="decimal"
                            className="param-input"
                            name={param.key}
                            value={formData[param.key]}
                            onChange={handleInputChange}
                            placeholder="e.g. 7.4 or N/A"
                          />
                          <span className="param-unit">{param.unit}</span>
                        </div>

                        <div className="field-meta-row">
                          <span className="field-standard-hint">{param.hint}</span>
                          <span className={`compliance-indicator ${status}`}>
                            {status === "pass" ? "Compliant" : status === "fail" ? "Out of Limit" : "KNN Auto"}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Laboratory Parameters */}
                <div className="form-section-title" style={{ marginTop: "1.5rem" }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M10 2v7.31"></path>
                    <path d="M14 9.3V2"></path>
                    <path d="M8.5 2h7"></path>
                    <path d="M14 9.3a6.5 6.5 0 1 1-4 0"></path>
                    <path d="M5.52 16h12.96"></path>
                  </svg>
                  Laboratory Biological & Organic Analysis
                </div>

                <div className="form-grid">
                  {PARAM_CONFIG.filter((p) => p.category === "lab").map((param) => {
                    const status = param.check(formData[param.key]);
                    return (
                      <div className="param-field" key={param.key}>
                        <div className="field-top-row">
                          <div className="param-badge-name">
                            <span className="param-symbol">{param.symbol}</span>
                            <label className="param-label" htmlFor={param.key}>{param.name}</label>
                          </div>
                        </div>

                        <div className="field-input-box">
                          <input
                            id={param.key}
                            type="text"
                            inputMode="decimal"
                            className="param-input"
                            name={param.key}
                            value={formData[param.key]}
                            onChange={handleInputChange}
                            placeholder="e.g. 80 or N/A"
                          />
                          <span className="param-unit">{param.unit}</span>
                        </div>

                        <div className="field-meta-row">
                          <span className="field-standard-hint">{param.hint}</span>
                          <span className={`compliance-indicator ${status}`}>
                            {status === "pass" ? "Compliant" : status === "fail" ? "Out of Limit" : "KNN Auto"}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Action Buttons */}
                <div className="action-row">
                  <button type="submit" className="primary-btn" disabled={loading}>
                    {loading ? (
                      <>
                        <span className="spin-ring" style={{ width: "16px", height: "16px", borderWidth: "2px", margin: 0 }}></span>
                        <span>Evaluating Chemistry...</span>
                      </>
                    ) : (
                      <>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                        </svg>
                        <span>Compute WQI Suitability</span>
                      </>
                    )}
                  </button>

                  <button type="button" className="secondary-btn" onClick={handleReset} title="Clear to N/A to test imputation">
                    Reset
                  </button>
                </div>
              </form>

              {error && (
                <div className="error-banner">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                  </svg>
                  <span>{error}</span>
                </div>
              )}
            </div>
          </section>

          {/* Right Panel: Output & Environmental Assessment */}
          <section className="pro-card">
            <div className="card-header">
              <div className="card-title-group">
                <span className="card-title-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                  </svg>
                </span>
                <div>
                  <h2>Water Quality Classification</h2>
                  <p className="card-subtitle">DENR DAO 2016-08 Suitability & Diagnostics</p>
                </div>
              </div>
            </div>

            <div className="card-body">
              {/* Ready / Empty State */}
              {!result && !loading && (
                <div className="empty-state-wrapper">
                  <div className="empty-icon-shield">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                    </svg>
                  </div>
                  <h3>Awaiting Water Sample Input</h3>
                  <p>
                    Select a river profile template or adjust sensor values on the left to calculate the Weighted Arithmetic WQI.
                  </p>

                  <div className="empty-table-summary">
                    <div className="empty-table-header">DENR DAO 2016-08 Benchmark Thresholds</div>
                    <div className="empty-table-row">
                      <span>Dissolved Oxygen (DO)</span>
                      <span>Min 5.0 mg/L</span>
                    </div>
                    <div className="empty-table-row">
                      <span>Biochemical Oxygen Demand (BOD₅)</span>
                      <span>Max 7.0 mg/L</span>
                    </div>
                    <div className="empty-table-row">
                      <span>Total Suspended Solids (TSS)</span>
                      <span>Max 80.0 mg/L</span>
                    </div>
                    <div className="empty-table-row">
                      <span>Fecal Coliform Count</span>
                      <span>Max 200 MPN/100mL</span>
                    </div>
                    <div className="empty-table-row">
                      <span>pH Level</span>
                      <span>6.5 – 9.0</span>
                    </div>
                    <div className="empty-table-row">
                      <span>Water Temperature</span>
                      <span>25.0 – 31.0 °C</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Loading State */}
              {loading && (
                <div className="loading-wrapper">
                  <div className="spin-ring"></div>
                  <div className="loading-title">Processing Chemical Pipeline</div>
                  <div className="loading-desc">
                    Running KNN imputation, feature engineering, and WAWQI classification...
                  </div>
                </div>
              )}

              {/* Results State */}
              {result && currentClassInfo && (
                <div className="results-container">
                  {/* Hero Classification Card */}
                  <div className={`hero-class-card ${currentClassInfo.className}`}>
                    <div className="hero-header-row">
                      <div>
                        <div className="class-tag">Suitability Class</div>
                        <div className="class-main-title">{result.prediction}</div>
                      </div>
                      <div className="denr-class-badge">{currentClassInfo.denrCode}</div>
                    </div>
                    <p className="class-usage-description">{currentClassInfo.description}</p>
                    <div style={{ fontSize: "0.8rem", color: "rgba(255, 255, 255, 0.8)", borderTop: "1px solid rgba(255, 255, 255, 0.1)", paddingTop: "0.5rem" }}>
                      <strong>Operational Advisory:</strong> {currentClassInfo.advisory}
                    </div>
                  </div>

                  {/* Engineered Biomarkers */}
                  {result.engineered_features && (
                    <div className="metrics-twin-grid">
                      <div className="metric-mini-card">
                        <div className="metric-mini-label">DO / Temperature Ratio</div>
                        <div className="metric-mini-value">{result.engineered_features.DO_Temp_Ratio}</div>
                        <div className="metric-mini-subtext">Thermal oxygen saturation factor</div>
                      </div>
                      <div className="metric-mini-card">
                        <div className="metric-mini-label">pH Deviation from Neutral</div>
                        <div className="metric-mini-value">{result.engineered_features.pH_Deviation}</div>
                        <div className="metric-mini-subtext">Acid-base equilibrium offset (|pH - 7|)</div>
                      </div>
                    </div>
                  )}

                  {/* Compliance Diagnostic Breakdown */}
                  <div className="audit-table-card">
                    <div className="audit-table-title">
                      <span>Sample Compliance Diagnostic Audit</span>
                      <span style={{ fontSize: "0.72rem", color: "var(--text-tertiary)" }}>DENR DAO 2016-08</span>
                    </div>
                    <table className="audit-table">
                      <thead>
                        <tr>
                          <th>Parameter</th>
                          <th>Tested Value</th>
                          <th>Standard</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {PARAM_CONFIG.map((p) => {
                          const val = formData[p.key];
                          const status = p.check(val);
                          return (
                            <tr key={p.key}>
                              <td>{p.name} ({p.symbol})</td>
                              <td className="cell-val">{val} {p.unit}</td>
                              <td className="cell-standard">{p.standardDisplay}</td>
                              <td>
                                <span className={`compliance-indicator ${status}`}>
                                  {status === "pass" ? "Compliant" : status === "fail" ? "Exceeded" : "KNN Imputed"}
                                </span>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>

                  {/* Classification Scale Reference */}
                  <div className="standards-legend">
                    <div className="legend-header-title">Classification Matrix Reference</div>
                    <div className="legend-grid-list">
                      <div className="legend-row">
                        <div className="legend-row-left">
                          <span className="legend-dot dot-excellent"></span>
                          <span className="legend-name">Excellent (Class AA)</span>
                        </div>
                        <span className="legend-desc">Pristine Public Water Supply I</span>
                      </div>
                      <div className="legend-row">
                        <div className="legend-row-left">
                          <span className="legend-dot dot-good"></span>
                          <span className="legend-name">Good (Class A)</span>
                        </div>
                        <span className="legend-desc">Public Water Supply II (Disinfected)</span>
                      </div>
                      <div className="legend-row">
                        <div className="legend-row-left">
                          <span className="legend-dot dot-fair"></span>
                          <span className="legend-name">Fair (Class B)</span>
                        </div>
                        <span className="legend-desc">Primary Contact Recreation (Bathing)</span>
                      </div>
                      <div className="legend-row">
                        <div className="legend-row-left">
                          <span className="legend-dot dot-poor"></span>
                          <span className="legend-name">Poor (Class C)</span>
                        </div>
                        <span className="legend-desc">Fishery & Agricultural Irrigation</span>
                      </div>
                      <div className="legend-row">
                        <div className="legend-row-left">
                          <span className="legend-dot dot-risk"></span>
                          <span className="legend-name">High Risk (Class D)</span>
                        </div>
                        <span className="legend-desc">Severe Degradation / Navigation Only</span>
                      </div>
                    </div>
                  </div>

                </div>
              )}
            </div>
          </section>

        </div>
      </main>
    </>
  );
}
