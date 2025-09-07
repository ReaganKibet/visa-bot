// frontend/src/components/MonitorStatus.jsx
import { useEffect, useState } from 'react';

function MonitorStatus() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/monitor-updates");
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLogs(prev => [data, ...prev.slice(0, 99)]);
    };

    return () => ws.close();
  }, []);

  return (
    <div>
      <h3>Monitoring Activity</h3>
      {logs.map((log, i) => (
        <div key={i} className={`log-item ${log.status}`}>
          {new Date(log.timestamp).toLocaleTimeString()} — {log.event}
        </div>
      ))}
    </div>
  );
}