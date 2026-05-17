import { useEffect, useRef, useState } from "react";
import "./App.css";

function App() {
  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    if (socketRef.current) return;

    const socket = new WebSocket("ws://localhost:8765");

    socketRef.current = socket;

    socket.onopen = () => {
      console.log("[WS] Connected");
      setConnected(true);
    };

    socket.onclose = () => {
      console.log("[WS] Disconnected");
      setConnected(false);
      socketRef.current = null;
    };

    socket.onerror = (err) => {
      console.error("[WS ERROR]", err);
      setConnected(false);
    };

    socket.onmessage = (event) => {
      console.log("[WS MESSAGE]", event.data);

      const alert = JSON.parse(event.data);

      setAlerts((prev) => {
        const exists = prev.find((a) => a.id === alert.id);
        if (exists) return prev;
        return [alert, ...prev];
      });
    };

    return () => {
      socket.close();
      socketRef.current = null;
    };
  }, []);

  const critical = alerts.filter(
    (a) => a.severity === "critical"
  ).length;

  const suspicious = alerts.filter(
    (a) => a.severity === "suspicious"
  ).length;

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
            <h2>{alerts.length}</h2>
            <span>↑ 100% from last hour</span>
          </div>

          <div className="metric red">
            <p>CRITICAL ALERTS</p>
            <h2>{critical}</h2>
            <span>↑ high severity threats</span>
          </div>

          <div className="metric amber">
            <p>SUSPICIOUS ALERTS</p>
            <h2>{suspicious}</h2>
            <span>potential threats</span>
          </div>

          <div className="metric green">
            <p>TOTAL LOGS ANALYZED</p>
            <h2>5</h2>
            <span>↑ 100% from last hour</span>
          </div>
        </section>

        <section className="alerts-panel">
          <div className="panel-header">
            <div>
              <h2>Real-Time Cyber Alerts</h2>

              <p>Live stream of detected threats and suspicious activities</p>
            </div>

            <button>All Severities</button>
          </div>

          <div className="table">
            <div className="table-head">
              <span>SEVERITY</span>
              <span>QUERY</span>
              <span>EXPLANATION</span>
              <span>TIME</span>
            </div>

            {alerts.length === 0 && (
              <div className="empty">No alerts received yet.</div>
            )}

            <div className="alerts-scroll">
              {alerts.map((alert) => (
                <div
                  className={`table-row ${alert.severity}`}
                  key={alert.id}
                >
                  <span className="badge">{alert.severity}</span>

                  <span className="query">{alert.query}</span>

                  <span className="explanation">{alert.explanation}</span>

                  <span className="time">
                    {new Date(alert.created_at).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
