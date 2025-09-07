// frontend/src/App.js
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

function App() {
  const [logs, setLogs] = useState([]);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [monitorStatus, setMonitorStatus] = useState(null);
  const [activeMonitors, setActiveMonitors] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  // ✅ WebSocket connection with reconnection logic
  const connectWebSocket = () => {
    try {
      wsRef.current = new WebSocket("ws://localhost:8000/ws/monitor-updates");
      
      wsRef.current.onopen = () => {
        console.log('✅ WebSocket connected');
        setConnectionStatus('Connected');
        setError(null);
        reconnectAttemptsRef.current = 0;
        
        addLog('connection', '✅ Connected to monitoring system');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("📡 WebSocket message:", data);
          
          // Don't add pong messages to logs
          if (data.event !== 'pong') {
            addLog(data.event, data.message, data.timestamp);
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('🔌 WebSocket closed:', event.code, event.reason);
        setConnectionStatus('Disconnected');
        
        // Attempt to reconnect
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const timeout = Math.pow(2, reconnectAttemptsRef.current) * 1000;
          reconnectAttemptsRef.current++;
          
          setConnectionStatus(`Reconnecting (${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);
          addLog('reconnecting', `🔄 Reconnecting in ${timeout/1000}s (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(connectWebSocket, timeout);
        } else {
          setConnectionStatus('Connection Failed');
          addLog('error', '❌ Max reconnection attempts reached');
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setConnectionStatus('Error');
      };

    } catch (err) {
      console.error('❌ WebSocket connection failed:', err);
      setConnectionStatus('Error');
    }
  };

  // ✅ Helper function to add logs
  const addLog = (event, message, timestamp = null) => {
    const logEntry = {
      id: Date.now() + Math.random(),
      timestamp: timestamp || new Date().toISOString(),
      event: event,
      message: message
    };
    
    setLogs(prev => [logEntry, ...prev.slice(0, 99)]); // Keep only last 100 logs
  };

  // Connect WebSocket on mount
  useEffect(() => {
    connectWebSocket();
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Load data on mount and periodically
  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // Every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [monitorsRes, statusRes] = await Promise.all([
        axios.get("http://localhost:8000/monitors/"),
        axios.get("http://localhost:8000/monitors/status")
      ]);
      
      setActiveMonitors(monitorsRes.data);
      setMonitorStatus(statusRes.data);
      
      // Update monitoring state based on active monitor
      const hasActiveMonitor = statusRes.data.active_monitor?.id;
      setIsMonitoring(!!hasActiveMonitor);
      
    } catch (err) {
      console.error("Failed to load data:", err);
      addLog('error', '❌ Failed to load monitor data');
    }
  };

  const startMonitoring = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post("http://localhost:8000/monitors/", {
        flow: "mozambique-to-portugal",
        applicant_id: `user_${Date.now()}`, // ✅ Generate unique applicant_id
        config: { check_interval: 60 }
      });
      
      console.log('✅ Monitor started:', response.data);
      addLog('monitor_started', `✅ Monitor ${response.data.id} started successfully`);
      await loadData();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Failed to start monitoring";
      setError(errorMsg);
      addLog('error', `❌ ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const stopMonitoring = async () => {
    if (!monitorStatus?.active_monitor?.id) return;
    
    setLoading(true);
    setError(null);
    
    try {
      await axios.post(`http://localhost:8000/monitors/${monitorStatus.active_monitor.id}/stop`);
      addLog('monitor_stopped', '⏹️ Monitoring stopped successfully');
      await loadData();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Failed to stop monitoring";
      setError(errorMsg);
      addLog('error', `❌ ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const startBooking = async () => {
    if (!monitorStatus?.active_monitor?.run_id) {
      setError('No active monitor found');
      addLog('error', '❌ No active monitor found for booking');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post("http://localhost:8000/bookings/", {
        applicant_id: monitorStatus.active_monitor.applicant_id, // ✅ Use correct applicant_id
        run_id: monitorStatus.active_monitor.run_id, // ✅ Use correct run_id
        form_data: { name: 'Test User' }
      });
      
      console.log('✅ Booking started:', response.data);
      addLog('booking_triggered', '🚀 Booking triggered — browser opening...');
    } catch (err) {
      const errorMsg = err.response?.data?.detail || "Failed to start booking";
      setError(errorMsg);
      addLog('error', `❌ ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1>🎯 VFS Appointment Dashboard</h1>
        <p>Real-time monitoring & booking control</p>
        <div style={styles.connectionStatus}>
          WebSocket: <span style={{
            color: connectionStatus === 'Connected' ? '#4CAF50' : 
                   connectionStatus.includes('Reconnecting') ? '#ffd93d' : '#ff6b6b'
          }}>{connectionStatus}</span>
        </div>
      </header>

      {/* Error Display */}
      {error && (
        <div style={styles.errorBox}>
          ❌ {error}
          <button onClick={() => setError(null)} style={styles.closeButton}>×</button>
        </div>
      )}

      {/* Status Cards */}
      <div style={styles.statusGrid}>
        <div style={styles.card}>
          <h3>🔍 Monitor Status</h3>
          <div style={styles.statusItem}>
            <strong>Status:</strong> 
            <span style={{
              color: monitorStatus?.active_monitor?.id ? '#4CAF50' : '#ff6b6b',
              marginLeft: '8px'
            }}>
              {monitorStatus?.active_monitor?.id ? 'Active' : 'Inactive'}
            </span>
          </div>
          {monitorStatus?.active_monitor && (
            <>
              <div style={styles.statusItem}>
                <strong>ID:</strong> {monitorStatus.active_monitor.id}
              </div>
              <div style={styles.statusItem}>
                <strong>Applicant:</strong> {monitorStatus.active_monitor.applicant_id}
              </div>
            </>
          )}
        </div>

        <div style={styles.card}>
          <h3>📊 Statistics</h3>
          <div style={styles.statusItem}>
            <strong>Total Monitors:</strong> {activeMonitors.length}
          </div>
          <div style={styles.statusItem}>
            <strong>Active:</strong> {activeMonitors.filter(m => m.status === 'active').length}
          </div>
          <div style={styles.statusItem}>
            <strong>Log Messages:</strong> {logs.length}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div style={styles.card}>
        <h2>🟢 Controls</h2>
        <div style={styles.buttonGroup}>
          <button 
            onClick={startMonitoring} 
            style={{
              ...styles.button,
              backgroundColor: isMonitoring ? '#666' : '#4CAF50',
              cursor: (loading || isMonitoring) ? 'not-allowed' : 'pointer'
            }}
            disabled={loading || isMonitoring}
          >
            {loading ? '⏳ Starting...' : isMonitoring ? '✅ Monitoring Active' : '▶️ Start Monitoring'}
          </button>
          
          <button 
            onClick={stopMonitoring} 
            style={{
              ...styles.button, 
              backgroundColor: '#f44336',
              cursor: (loading || !isMonitoring) ? 'not-allowed' : 'pointer'
            }}
            disabled={loading || !isMonitoring}
          >
            {loading ? '⏳ Stopping...' : '⏹️ Stop Monitoring'}
          </button>
          
          <button 
            onClick={startBooking} 
            style={{
              ...styles.button,
              backgroundColor: '#2196F3',
              cursor: (loading || !isMonitoring) ? 'not-allowed' : 'pointer'
            }}
            disabled={loading || !isMonitoring}
          >
            {loading ? '⏳ Starting...' : '🎯 Start Booking'}
          </button>
          
          <button onClick={clearLogs} style={{...styles.button, backgroundColor: '#666'}}>
            🗑️ Clear Logs
          </button>
        </div>
      </div>

      {/* Real-time Logs */}
      <div style={styles.card}>
        <h2>📋 Real-Time Logs ({logs.length})</h2>
        <div style={styles.logs}>
          {logs.length === 0 ? (
            <div style={styles.noLogs}>
              🔍 Waiting for log messages...
              <br />
              <small>Start monitoring to see real-time updates</small>
            </div>
          ) : (
            logs.map((log) => (
              <div key={log.id} style={styles.logLine}>
                <span style={styles.timestamp}>
                  [{formatTimestamp(log.timestamp)}]
                </span>
                <span style={getEventStyle(log.event)}>
                  {log.message}
                </span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Active Monitors */}
      <div style={styles.card}>
        <h2>📊 Recent Monitors ({activeMonitors.length})</h2>
        {activeMonitors.length === 0 ? (
          <p style={{color: '#888'}}>No monitors found</p>
        ) : (
          <div style={styles.monitorList}>
            {activeMonitors.slice(0, 5).map(monitor => (
              <div key={monitor.id} style={styles.monitorItem}>
                <span><strong>ID:</strong> {monitor.id}</span>
                <span><strong>Flow:</strong> {monitor.flow}</span>
                <span style={{
                  color: monitor.status === 'active' ? '#4CAF50' : '#ff6b6b'
                }}>
                  <strong>Status:</strong> {monitor.status}
                </span>
                <span><strong>Created:</strong> {new Date(monitor.created_at).toLocaleString()}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Helper function for event-specific styling
const getEventStyle = (event) => {
  const baseStyle = { marginLeft: '8px' };
  switch (event) {
    case 'error':
      return { ...baseStyle, color: '#ff6b6b' };
    case 'monitor_started':
    case 'booking_triggered':
    case 'slots_found':
      return { ...baseStyle, color: '#51cf66' };
    case 'connection':
    case 'connected':
      return { ...baseStyle, color: '#64ffda' };
    case 'disconnection':
    case 'captcha_detected':
      return { ...baseStyle, color: '#ffd93d' };
    case 'slot_check':
    case 'no_slots':
      return { ...baseStyle, color: '#888' };
    default:
      return { ...baseStyle, color: '#cccccc' };
  }
};

// ✅ Updated Styles
const styles = {
  container: {
    fontFamily: 'monospace',
    padding: '20px',
    backgroundColor: '#1e1e1e',
    color: 'white',
    minHeight: '100vh'
  },
  header: {
    textAlign: 'center',
    marginBottom: '30px',
    color: '#64ffda'
  },
  connectionStatus: {
    fontSize: '14px',
    marginTop: '10px'
  },
  errorBox: {
    backgroundColor: '#ff6b6b',
    color: 'white',
    padding: '12px',
    borderRadius: '6px',
    marginBottom: '20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  closeButton: {
    background: 'none',
    border: 'none',
    color: 'white',
    fontSize: '18px',
    cursor: 'pointer'
  },
  statusGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '20px',
    marginBottom: '20px'
  },
  card: {
    backgroundColor: '#2d2d2d',
    borderRadius: '10px',
    padding: '20px',
    marginBottom: '20px',
    border: '1px solid #444'
  },
  statusItem: {
    margin: '8px 0',
    fontSize: '14px'
  },
  buttonGroup: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '10px'
  },
  button: {
    padding: '12px 24px',
    fontSize: '16px',
    backgroundColor: '#4CAF50',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'background-color 0.3s'
  },
  logs: {
    maxHeight: '500px',
    overflowY: 'auto',
    border: '1px solid #444',
    borderRadius: '6px',
    padding: '10px',
    backgroundColor: '#1e1e1e',
    fontFamily: 'monospace',
    fontSize: '14px',
    lineHeight: '1.6'
  },
  noLogs: {
    textAlign: 'center',
    color: '#888',
    padding: '40px 20px'
  },
  logLine: {
    display: 'flex',
    alignItems: 'flex-start',
    borderBottom: '1px solid #333',
    padding: '4px 0',
    wordBreak: 'break-word'
  },
  timestamp: {
    color: '#888',
    fontSize: '12px',
    minWidth: '80px',
    flexShrink: 0
  },
  monitorList: {
    maxHeight: '300px',
    overflowY: 'auto'
  },
  monitorItem: {
    display: 'grid',
    gridTemplateColumns: '1fr 2fr 1fr 2fr',
    gap: '10px',
    alignItems: 'center',
    padding: '8px 12px',
    margin: '4px 0',
    backgroundColor: '#1e1e1e',
    borderRadius: '4px',
    fontSize: '14px',
    border: '1px solid #444'
  }
};

export default App;