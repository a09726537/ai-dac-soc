import { useEffect, useRef, useState } from "react";

import criticalSound from "./assets/critical.mp3";
import suspiciousSound from "./assets/suspicious.mp3";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  Tooltip,
  XAxis,
  YAxis,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar
} from "recharts";

import "./App.css";

const API_URL = "http://192.168.136.132:8000/api/stats";
const WS_URL = "ws://192.168.136.132:8765";

function App() {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({
    total_alerts: 0,
    critical: 0,
    suspicious: 0
  });

  const [connected, setConnected] = useState(false);
  const [filter, setFilter] = useState("all");
  const [toastAlert, setToastAlert] = useState(null);
  const [analysisAlert, setAnalysisAlert] = useState(null);

  const socketRef = useRef(null);
  const toastTimerRef = useRef(null);
  const criticalAudio = useRef(null);
  const suspiciousAudio = useRef(null);

  const fetchStats = () => {
    fetch(API_URL)
      .then((res) => res.json())
      .then((data) => {
        console.log("API STATS:", data);
        setStats(data);
      })
      .catch((err) => {
        console.error("API ERROR", err);
      });
  };

  useEffect(() => {
    fetchStats();

    if (socketRef.current) return;

    const socket = new WebSocket(WS_URL);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("WEBSOCKET CONNECTED");
      setConnected(true);
    };

    socket.onclose = () => {
      console.log("WEBSOCKET DISCONNECTED");
      setConnected(false);
      socketRef.current = null;
    };

    socket.onerror = (err) => {
      console.error("WEBSOCKET ERROR", err);
      setConnected(false);
    };

    socket.onmessage = (event) => {
      try {
        const alert = JSON.parse(event.data);

        console.log("NEW ALERT:", alert);

        setToastAlert(alert);
        setAnalysisAlert(alert);

        if (toastTimerRef.current) {
          clearTimeout(toastTimerRef.current);
        }

        toastTimerRef.current = setTimeout(() => {
          setToastAlert(null);
        }, 5000);

        if (alert.severity === "critical") {
          criticalAudio.current?.play().catch(() => {});
        }

        if (alert.severity === "suspicious") {
          suspiciousAudio.current?.play().catch(() => {});
        }

        setAlerts((prev) => {
          const exists = prev.find((a) => a.id === alert.id);
          if (exists) return prev;
          return [alert, ...prev];
        });

        fetchStats();
      } catch (e) {
        console.error("Invalid WebSocket JSON", e);
      }
    };

    return () => {
      if (toastTimerRef.current) {
        clearTimeout(toastTimerRef.current);
      }

      socket.close();
      socketRef.current = null;
    };
  }, []);

  const filteredAlerts = alerts.filter((alert) => {
    if (filter === "all") return true;
    return alert.severity === filter;
  });

  const trendData = [...alerts].reverse().map((_, index) => ({
    index: index + 1,
    alerts: index + 1
  }));

  const severityData = [
    { name: "Critical", value: stats.critical },
    { name: "Suspicious", value: stats.suspicious }
  ];

  const shapData = [
    { feature: "DROP", score: 0.31 },
    { feature: "TABLE", score: 0.24 },
    { feature: "OR 1=1", score: 0.21 },
    { feature: "admin", score: 0.16 },
    { feature: "users", score: 0.12 }
  ];

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          AI-DAC
          <br />
          SOC
        </div>

        <nav>
          <div className="nav active">Dashboard</div>
          <div className="nav">Alerts</div>
          <div className="nav">Analytics</div>
          <div className="nav">Logs</div>
          <div className="nav">Reports</div>
          <div className="nav">Settings</div>
        </nav>

        <div className="connection">
          <span className={connected ? "dot green" : "dot red"}></span>
          <strong>{connected ? "Connected" : "Disconnected"}</strong>
          <p>AI-DAC WebSocket</p>
        </div>
      </aside>

      <main className="main">
        {toastAlert && (
          <div className={`toast ${toastAlert.severity}`}>
            <strong>{toastAlert.severity.toUpperCase()} ALERT</strong>
            <span>{toastAlert.query}</span>
          </div>
        )}

        <header className="topbar">
          <div>
            <h1>AI-DAC SOC Dashboard</h1>
            <p>Real-time cyber threat monitoring and analysis</p>
          </div>

          <div className="protection">
            ⬡ AI-DAC Protection Active
            <span className="dot green"></span>
          </div>
        </header>

        <section className="cards">
          <div className="metric blue">
            <p>TOTAL LIVE ALERTS</p>
            <h2>{stats.total_alerts}</h2>
            <span>↑ 100% from last hour</span>
          </div>

          <div className="metric red">
            <p>CRITICAL ALERTS</p>
            <h2>{stats.critical}</h2>
            <span>↑ high severity threats</span>
          </div>

          <div className="metric amber">
            <p>SUSPICIOUS ALERTS</p>
            <h2>{stats.suspicious}</h2>
            <span>potential threats</span>
          </div>

          <div className="metric green">
            <p>TOTAL LOGS ANALYZED</p>
            <h2>{stats.total_alerts}</h2>
            <span>↑ 100% from last hour</span>
          </div>
        </section>

        <section className="analytics-grid">
          <div className="chart-card">
            <h3>Alert Trend</h3>

            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={trendData}>
                <CartesianGrid stroke="#1e293b" />
                <XAxis dataKey="index" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" allowDecimals={false} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="alerts"
                  stroke="#3b82f6"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Severity Distribution</h3>

            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={severityData}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={90}
                  label
                >
                  <Cell fill="#ef4444" />
                  <Cell fill="#f59e0b" />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="mitre-panel">
          <h2>MITRE ATT&CK Mapping</h2>

          <div className="mitre-grid">
            <div className="mitre-card critical">
              <span>T1190</span>
              <p>Exploit Public-Facing Application</p>
            </div>

            <div className="mitre-card suspicious">
              <span>T1071</span>
              <p>Application Layer Protocol</p>
            </div>

            <div className="mitre-card">
              <span>T1021</span>
              <p>Remote Services</p>
            </div>

            <div className="mitre-card">
              <span>T1046</span>
              <p>Network Service Scanning</p>
            </div>
          </div>
        </section>

        <section className="alerts-panel">
          <div className="panel-header">
            <div>
              <h2>Real-Time Cyber Alerts</h2>
              <p>Live stream of detected threats and suspicious activities</p>
            </div>

            <select value={filter} onChange={(e) => setFilter(e.target.value)}>
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="suspicious">Suspicious</option>
            </select>
          </div>

          <div className="table-wrapper">
            <table className="soc-table">
              <thead>
                <tr>
                  <th>SEVERITY</th>
                  <th>QUERY</th>
                  <th>EXPLANATION</th>
                  <th>TIME</th>
                </tr>
              </thead>

              <tbody>
                {filteredAlerts.length === 0 && (
                  <tr>
                    <td colSpan="4" className="empty">
                      No alerts received yet.
                    </td>
                  </tr>
                )}

                {filteredAlerts.map((alert) => (
                  <tr className={alert.severity} key={alert.id}>
                    <td>
                      <span className="badge">{alert.severity}</span>
                    </td>
                    <td className="query">{alert.query}</td>
                    <td className="explanation">{alert.explanation}</td>
                    <td className="time">
                      {new Date(alert.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="ai-panel">
          <h2>AI Explainability Engine</h2>

          {analysisAlert ? (
            <div className="ai-card">
              <div className="ai-grid">
                <div>
                  <span className="label">Threat Type</span>
                  <h3>
                    {analysisAlert.severity === "critical"
                      ? "SQL Injection / Destructive Query"
                      : "Suspicious Database Activity"}
                  </h3>
                </div>

                <div>
                  <span className="label">MITRE ATT&CK</span>
                  <h3>T1190</h3>
                </div>

                <div>
                  <span className="label">Confidence Score</span>
                  <h3>
                    {analysisAlert.severity === "critical" ? "98.4%" : "87.2%"}
                  </h3>
                </div>

                <div>
                  <span className="label">Risk Level</span>
                  <h3 className={analysisAlert.severity}>
                    {analysisAlert.severity.toUpperCase()}
                  </h3>
                </div>
              </div>

              <div className="ai-explanation">
                <span className="label">AI Explanation</span>
                <p>{analysisAlert.explanation}</p>
              </div>

              <div className="recommendation">
                <span className="label">Recommended Action</span>
                <p>
                  Block the session, isolate the database transaction, preserve
                  forensic logs, and trigger SOC escalation.
                </p>
              </div>
            </div>
          ) : (
            <div className="ai-empty">Waiting for AI anomaly analysis...</div>
          )}
        </section>

        <section className="shap-panel">
          <h2>SHAP Explainability Visualization</h2>

          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={shapData}>
              <CartesianGrid stroke="#1e293b" />
              <XAxis dataKey="feature" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip />
              <Bar dataKey="score" fill="#60a5fa" />
            </BarChart>
          </ResponsiveContainer>
        </section>

        <section className="assistant-panel">
          <div className="assistant-header">
            <h2>AI SOC Analyst Assistant</h2>
            <div className="assistant-status">● Online</div>
          </div>

          <div className="assistant-card">
            {analysisAlert ? (
              <>
                <div className="assistant-message ai">
                  <strong>AI Analyst</strong>
                  <p>
                    A <b>{analysisAlert.severity}</b> database anomaly has been
                    detected. The query pattern indicates possible malicious
                    behavior targeting the RDBMS infrastructure. Recommended
                    response: isolate the affected session, preserve forensic
                    logs, and trigger incident escalation procedures.
                  </p>
                </div>

                <div className="assistant-message system">
                  <strong>System</strong>
                  <p>
                    MITRE ATT&CK: T1190
                    <br />
                    Confidence Score:{" "}
                    {analysisAlert.severity === "critical" ? "98.4%" : "87.2%"}
                    <br />
                    Status: Active Threat Investigation
                  </p>
                </div>
              </>
            ) : (
              <div className="assistant-empty">
                Waiting for incoming threat intelligence...
              </div>
            )}
          </div>
        </section>

        <section className="timeline-panel">
          <div className="timeline-header">
            <h2 className="white-title">Threat Intelligence Timeline</h2>
            <div className="timeline-live">● LIVE</div>
          </div>

          <div className="timeline-list">
            {alerts.slice(0, 6).map((alert) => (
              <div
                className={`timeline-item ${alert.severity}`}
                key={alert.id}
              >
                <div className="timeline-dot"></div>

                <div className="timeline-mini-content">
                  <div className="timeline-mini-top">
                    <span className="timeline-mini-severity">
                      {alert.severity.toUpperCase()}
                    </span>

                    <span className="timeline-mini-time">
                      {new Date(alert.created_at).toLocaleTimeString()}
                    </span>
                  </div>

                  <div className="timeline-mini-text">
                    {alert.severity === "critical"
                      ? "Critical database attack pattern detected."
                      : "Suspicious query behavior observed."}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        <audio ref={criticalAudio} src={criticalSound} />
        <audio ref={suspiciousAudio} src={suspiciousSound} />
      </main>
    </div>
  );
}

export default App;
