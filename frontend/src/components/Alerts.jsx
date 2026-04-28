import { useState, useEffect } from "react";

export default function Alerts({ alerts }) {
  const [visible, setVisible] = useState([]);

  useEffect(() => {
    if (alerts.length > visible.length) {
      const newAlerts = alerts.slice(visible.length).map((msg, i) => ({
        id: Date.now() + i,
        msg,
        fading: false,
      }));
      setVisible(prev => [...prev, ...newAlerts]);

      // Auto-dismiss each new alert after 10 seconds
      newAlerts.forEach(alert => {
        setTimeout(() => {
          setVisible(prev => prev.map(a => a.id === alert.id ? { ...a, fading: true } : a));
          setTimeout(() => {
            setVisible(prev => prev.filter(a => a.id !== alert.id));
          }, 500);
        }, 10000);
      });
    }
  }, [alerts]);

  if (visible.length === 0) return null;

  return (
    <div className="alerts-container">
      {visible.map((alert) => (
        <div
          key={alert.id}
          className={`alert-card ${alert.fading ? 'alert-fade' : ''}`}
        >
          <div className="alert-header">
            <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>warning</span>
            <span className="alert-title">DISRUPTION ALERT</span>
          </div>
          <p className="alert-msg">{alert.msg}</p>
          <button
            className="alert-dismiss"
            onClick={() => setVisible(prev => prev.filter(a => a.id !== alert.id))}
          >
            DISMISS
          </button>
        </div>
      ))}
    </div>
  );
}
