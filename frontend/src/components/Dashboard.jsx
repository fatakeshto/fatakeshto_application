import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';
import wsService from '../services/websocket';

const Dashboard = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Authentication token not found');
      return;
    }

    // Connect to WebSocket
    wsService.connect(token);

    // Setup WebSocket event listeners
    const setupWebSocketListeners = () => {
      wsService.subscribe('device_status', handleDeviceStatusUpdate);
      wsService.subscribe('device_metrics', handleDeviceMetricsUpdate);
    };

    // Fetch initial devices data
    const fetchDevices = async () => {
      try {
        const response = await axios.get('https://fatakeshto-application.onrender.com/api/devices', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setDevices(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching devices:', error);
        setError('Failed to fetch devices');
        setLoading(false);
      }
    };

    setupWebSocketListeners();
    fetchDevices();

    // Cleanup function
    return () => {
      wsService.unsubscribe('device_status', handleDeviceStatusUpdate);
      wsService.unsubscribe('device_metrics', handleDeviceMetricsUpdate);
      wsService.disconnect();
    };
  }, []);

  const handleDeviceStatusUpdate = (data) => {
    setDevices(prevDevices => {
      return prevDevices.map(device => {
        if (device.id === data.deviceId) {
          return { ...device, status: data.status, lastActive: data.timestamp };
        }
        return device;
      });
    });
  };

  const handleDeviceMetricsUpdate = (data) => {
    setDevices(prevDevices => {
      return prevDevices.map(device => {
        if (device.id === data.deviceId) {
          return { 
            ...device, 
            cpu: data.cpu,
            ram: data.ram,
            network: data.network,
            battery: data.battery
          };
        }
        return device;
      });
    });
  };

  if (loading) return <div className="loading">Loading devices...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="dashboard">
      <h1>Device Dashboard</h1>
      
      {/* Device List */}
      <section className="device-list">
        <h2>Connected Devices</h2>
        {devices.length === 0 ? (
          <p>No devices connected</p>
        ) : (
          <ul>
            {devices.map(device => (
              <li key={device.id} className={`device-item ${device.status}`}>
                <h3>{device.name}</h3>
                <div className="device-details">
                  <p><strong>Status:</strong> {device.status}</p>
                  <p><strong>IP:</strong> {device.ip}</p>
                  <p><strong>Last Active:</strong> {new Date(device.lastActive).toLocaleString()}</p>
                  <p><strong>Battery:</strong> {device.battery}%</p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* GPS Tracking Map */}
      <section className="gps-tracking">
        <h2>GPS Tracking</h2>
        <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
          <GoogleMap
            mapContainerStyle={{ width: '100%', height: '400px' }}
            center={{ lat: 0, lng: 0 }}
            zoom={2}
          >
            {devices.map(device => (
              device.lat && device.lng && (
                <Marker
                  key={device.id}
                  position={{ lat: device.lat, lng: device.lng }}
                  title={device.name}
                />
              )
            ))}
          </GoogleMap>
        </LoadScript>
      </section>

      {/* Resource Monitoring */}
      <section className="resource-monitoring">
        <h2>Resource Monitoring</h2>
        <div className="resource-grid">
          {devices.map(device => (
            <div key={device.id} className="resource-card">
              <h3>{device.name}</h3>
              <div className="metrics">
                <div className="metric">
                  <span>CPU</span>
                  <div className="progress-bar">
                    <div 
                      className="progress" 
                      style={{ width: `${device.cpu || 0}%` }}
                    ></div>
                  </div>
                  <span>{device.cpu || 0}%</span>
                </div>
                <div className="metric">
                  <span>RAM</span>
                  <div className="progress-bar">
                    <div 
                      className="progress" 
                      style={{ width: `${(device.ram / device.totalRam) * 100 || 0}%` }}
                    ></div>
                  </div>
                  <span>{device.ram || 0}MB / {device.totalRam || 0}MB</span>
                </div>
                <div className="metric">
                  <span>Network</span>
                  <span>{device.network || 0} KB/s</span>
                </div>
              </div>
              {device.apps && (
                <div className="apps">
                  <h4>Installed Apps</h4>
                  <p>{device.apps.join(', ')}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  )
};

export default Dashboard;