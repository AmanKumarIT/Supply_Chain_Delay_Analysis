import { useState, useEffect, useRef, useCallback } from "react";
import { simulate, monitorRoute } from "../services/api";

export default function Dashboard({ setRerouted, setAlerts, setRouteGeometry, setRerouteGeometry, children }) {
  const [source, setSource] = useState("Delhi");
  const [target, setTarget] = useState("Chennai");
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [monitorStatus, setMonitorStatus] = useState(null);
  const [sweepActive, setSweepActive] = useState(false);
  const [logs, setLogs] = useState([]);
  const monitorRef = useRef(null);

  const addLog = useCallback((tag, msg, type = "msg") => {
    const time = new Date().toLocaleTimeString();
    setLogs(prev => [...prev.slice(-20), { time, tag, msg, type }]);
  }, []);

  // Clear monitor on source/target change
  useEffect(() => {
    if (monitorRef.current) {
      clearInterval(monitorRef.current);
      monitorRef.current = null;
    }
    setSweepActive(false);
    setMonitorStatus(null);
  }, [source, target]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (monitorRef.current) clearInterval(monitorRef.current);
    };
  }, []);

  const handleSimulate = async () => {
    setLoading(true);
    addLog("CMD", "INITIALIZING_SWEEP...");
    try {
      const res = await simulate({ source, target });
      const data = res.data;
      setPrediction(data);

      // Pass road geometry to map
      if (data.route_geometry) {
        setRouteGeometry(data.route_geometry.coords || []);
      }
      if (data.reroute_geometry) {
        setRerouteGeometry(data.reroute_geometry.coords || []);
      } else {
        setRerouteGeometry([]);
      }

      // Weather data
      if (data.weather_data) {
        setWeatherData(data.weather_data);
        addLog("WEATHER", `Severity: ${data.weather_data.severity} | ${data.weather_data.waypoint_count} waypoints scanned`);
        data.weather_data.alerts?.forEach(a => addLog("ALERT", a, "alert"));
      }

      // Decision
      if (data.decision.action === "reroute") {
        setRerouted(data.decision.recommended_path);
        setAlerts(prev => [...prev, data.decision.reason]);
        addLog("REROUTE", data.decision.reason, "alert");
      } else {
        setRerouted([]);
        addLog("SYS", "Route conditions NOMINAL. Standby.");
      }

      // Start continuous monitoring
      setSweepActive(true);
      addLog("MONITOR", "Continuous monitoring ACTIVE. Polling every 30s.");

      // Clear any existing interval
      if (monitorRef.current) clearInterval(monitorRef.current);

      monitorRef.current = setInterval(async () => {
        try {
          const monRes = await monitorRoute(source, target);
          const mon = monRes.data;
          setMonitorStatus(mon);

          if (mon.status === "ALERT") {
            addLog("ALERT", mon.reason, "alert");
            setAlerts(prev => [...prev, mon.reason]);
            mon.weather_alerts?.forEach(a => addLog("WEATHER", a, "alert"));
          } else {
            addLog("MONITOR", `Risk: ${mon.risk_score?.toFixed(2)} | Status: NOMINAL`);
          }

          // Update weather details from monitor
          if (mon.weather_details) {
            setWeatherData(prev => ({
              ...prev,
              severity: mon.weather_severity,
              details: mon.weather_details,
            }));
          }
        } catch (err) {
          addLog("ERR", "Monitor poll failed", "alert");
        }
      }, 30000);

    } catch (error) {
      console.error("Simulation failed", error);
      addLog("ERR", "SWEEP_FAILED: " + (error.message || "Unknown error"), "alert");
    } finally {
      setLoading(false);
    }
  };

  const stopMonitor = () => {
    if (monitorRef.current) {
      clearInterval(monitorRef.current);
      monitorRef.current = null;
    }
    setSweepActive(false);
    setMonitorStatus(null);
    addLog("SYS", "Monitoring STOPPED by operator.");
  };

  return (
    <>
      <header className="top-nav">
        <div className="nav-brand">
          <span className="material-symbols-outlined" style={{ color: "var(--primary-neon)" }}>terminal</span>
          <h1>CORE_INTEL_V.04</h1>
        </div>
        <div className="nav-status">
          {sweepActive && (
            <div className="flex-row gap-2" style={{ alignItems: 'center' }}>
              <div className="live-dot"></div>
              <span className="live-text">MONITORING</span>
            </div>
          )}
          <div className="nav-coord">STATUS: {sweepActive ? "TRACKING" : "IDLE"}</div>
          <span className="material-symbols-outlined">sensors</span>
        </div>
      </header>

      <main className="main-content">
        <div className="dashboard-grid">
          
          {/* Controls & Metrics Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            
            {/* Simulation Controls */}
            <section className="hud-card hud-card-accent-bottom">
              <div className="hud-corner hud-corner-tl"></div>
              <div className="hud-corner hud-corner-tr"></div>
              
              <div className="hud-header">
                <span className="hud-title">Routing Protocol</span>
              </div>
              
              <div className="cyber-form-group">
                <label className="cyber-label">Source Node</label>
                <select 
                  className="cyber-select" 
                  value={source} 
                  onChange={(e) => setSource(e.target.value)}
                >
                  <option value="Delhi">Delhi</option>
                  <option value="Mumbai">Mumbai</option>
                  <option value="Chennai">Chennai</option>
                  <option value="Kolkata">Kolkata</option>
                  <option value="Bangalore">Bangalore</option>
                  <option value="Hyderabad">Hyderabad</option>
                </select>
              </div>

              <div className="cyber-form-group">
                <label className="cyber-label">Target Node</label>
                <select 
                  className="cyber-select" 
                  value={target} 
                  onChange={(e) => setTarget(e.target.value)}
                >
                  <option value="Delhi">Delhi</option>
                  <option value="Mumbai">Mumbai</option>
                  <option value="Chennai">Chennai</option>
                  <option value="Kolkata">Kolkata</option>
                  <option value="Bangalore">Bangalore</option>
                  <option value="Hyderabad">Hyderabad</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
                <button 
                  className="cyber-button" 
                  onClick={handleSimulate} 
                  disabled={loading}
                  style={{ flex: 1 }}
                >
                  <span className="material-symbols-outlined">bolt</span>
                  {loading ? "EXECUTING..." : "INITIALIZE SWEEP"}
                </button>
                {sweepActive && (
                  <button 
                    className="cyber-button" 
                    onClick={stopMonitor}
                    style={{ flex: 0, padding: '16px', background: 'rgba(254,0,254,0.3)' }}
                  >
                    <span className="material-symbols-outlined">stop_circle</span>
                  </button>
                )}
              </div>
            </section>

            {/* Weather Intel HUD */}
            <section className="hud-card" style={{ borderLeft: '2px solid rgba(251, 255, 107, 0.4)' }}>
              <div className="hud-header">
                <span className="hud-title">Weather Intel</span>
                <span className="material-symbols-outlined color-tertiary">thunderstorm</span>
              </div>
              
              {weatherData ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div className="flex-row justify-between" style={{ alignItems: 'flex-end' }}>
                    <div className="metric-value glow-text-tertiary color-tertiary">
                      {(weatherData.severity * 100).toFixed(0)}
                      <span className="metric-unit">%</span>
                    </div>
                    <span className="metric-label">Composite Severity</span>
                  </div>
                  
                  {/* Weather waypoint grid */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', gap: '8px' }}>
                    {weatherData.details?.map((wp, i) => (
                      <div key={i} className="weather-chip">
                        <span className="weather-chip-condition">{wp.condition}</span>
                        <span className="weather-chip-temp">{wp.temp_c}°C</span>
                        <span className="weather-chip-detail">💨 {wp.wind_speed}m/s</span>
                        {wp.rain_1h > 0 && <span className="weather-chip-detail">🌧 {wp.rain_1h}mm</span>}
                      </div>
                    ))}
                  </div>

                  {weatherData.alerts?.length > 0 && (
                    <div className="terminal-section">
                      {weatherData.alerts.map((a, i) => (
                        <div key={i} className="terminal-log">
                          <span className="terminal-time">[⚠]</span>
                          <span className="terminal-alert">{a}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="terminal-section">
                  <div className="terminal-log">
                    <span className="terminal-time">[IDLE]</span>
                    <span className="terminal-msg">NO_WEATHER_DATA — Run sweep to scan route</span>
                  </div>
                </div>
              )}
            </section>

            {/* Results HUD */}
            <section className="hud-card hud-card-accent-left">
              <div className="hud-header">
                <span className="hud-title">Telemetry Readout</span>
                <span className="material-symbols-outlined color-secondary">ecg_heart</span>
              </div>
              
              {prediction ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <div className="flex-row justify-between" style={{ alignItems: 'flex-end' }}>
                    <div className="metric-value glow-text-secondary color-secondary">
                      {prediction.prediction.predicted_delay_hours}
                      <span className="metric-unit">HRS</span>
                    </div>
                    <span className="metric-label color-secondary">Est. Latency</span>
                  </div>
                  
                  {/* Route metadata */}
                  <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                    <div className="stat-chip">
                      <span className="stat-label">DISTANCE</span>
                      <span className="stat-value">{prediction.route_geometry?.distance_km || '—'} km</span>
                    </div>
                    <div className="stat-chip">
                      <span className="stat-label">METHOD</span>
                      <span className="stat-value">{prediction.route_geometry?.method || '—'}</span>
                    </div>
                    <div className="stat-chip">
                      <span className="stat-label">RISK</span>
                      <span className="stat-value">{Math.round(prediction.prediction.risk_score * 100)}%</span>
                    </div>
                  </div>
                  
                  {/* Pulse Wave Visualizer */}
                  <div className="pulse-wave" style={{ position: 'relative' }}>
                    <div className="live-indicator">
                      <div className="live-dot"></div>
                      <span className="live-text">SYNC</span>
                    </div>
                    <div className="pulse-bar" style={{ height: '30%' }}></div>
                    <div className="pulse-bar" style={{ height: '45%' }}></div>
                    <div className="pulse-bar active" style={{ height: '70%' }}></div>
                    <div className="pulse-bar active" style={{ height: '90%' }}></div>
                    <div className="pulse-bar active" style={{ height: '65%' }}></div>
                    <div className="pulse-bar" style={{ height: '40%' }}></div>
                    <div className="pulse-bar" style={{ height: '25%' }}></div>
                  </div>

                  <div className="terminal-section">
                    <div className="terminal-log">
                      <span className="terminal-time">[SYS]</span>
                      <span className="terminal-msg">Risk Score: {Math.round(prediction.prediction.risk_score * 100)}</span>
                    </div>
                    <div className="terminal-log">
                      <span className="terminal-time">[INTEL]</span>
                      <span className="terminal-alert">{prediction.decision.reason}</span>
                    </div>
                    <div className="terminal-log">
                      <span className="terminal-time">[CMD]</span>
                      <span className="terminal-alert">ACTION: {prediction.decision.action.toUpperCase()}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="terminal-section">
                  <div className="terminal-log">
                    <span className="terminal-time">[IDLE]</span>
                    <span className="terminal-msg">AWAITING_INITIALIZATION_COMMAND</span>
                  </div>
                </div>
              )}
            </section>
          </div>

          {/* Holographic Map Container */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <section className="map-container-wrapper">
              <div className="hud-corner hud-corner-tl"></div>
              <div className="hud-corner hud-corner-tr"></div>
              <div className="hud-corner hud-corner-bl"></div>
              <div className="hud-corner hud-corner-br"></div>
              
              <div className="geo-sync-badge">GEO_SYNC_ACTIVE</div>
              
              {/* Radar Sweep Effect */}
              <div className="radar-sweep"></div>
              
              {/* Leaflet Map Injection */}
              {children}
            </section>

            {/* Terminal Logs */}
            <section className="terminal-section" style={{ flex: 1, maxHeight: '250px', overflowY: 'auto' }}>
              {logs.length === 0 ? (
                <>
                  <div className="terminal-log">
                    <span className="terminal-time">[{new Date().toLocaleTimeString()}]</span>
                    <span className="terminal-msg">SYSTEM_CHECK: ALL_MODULES_NOMINAL</span>
                  </div>
                  <div className="terminal-log">
                    <span className="terminal-time">[{new Date().toLocaleTimeString()}]</span>
                    <span className="terminal-msg">WEATHER_API: STANDBY</span>
                  </div>
                </>
              ) : (
                logs.map((log, i) => (
                  <div key={i} className="terminal-log">
                    <span className="terminal-time">[{log.time}]</span>
                    <span className="terminal-time">[{log.tag}]</span>
                    <span className={log.type === "alert" ? "terminal-alert" : "terminal-msg"}>{log.msg}</span>
                  </div>
                ))
              )}
              
              <div className="terminal-footer">
                <span>Core Nodes: 6/6</span>
                <span>{sweepActive ? "MONITOR: ACTIVE" : "MONITOR: IDLE"}</span>
              </div>
            </section>
          </div>

        </div>
      </main>
    </>
  );
}
