import React, { useEffect, useState } from 'react';
import { Snackbar, Alert, Button } from '@mui/material';

const Notifications = ({ logs }) => {
  const [permission, setPermission] = useState(Notification.permission);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });

  useEffect(() => {
    // Request notification permission if not already granted
    if (permission === 'default') {
      requestNotificationPermission();
    }

    // Handle latest log
    const latestLog = logs[logs.length - 1];
    if (latestLog) {
      handleNewLog(latestLog);
    }
  }, [logs, permission]);

  const requestNotificationPermission = async () => {
    try {
      const result = await Notification.requestPermission();
      setPermission(result);
      if (result === 'granted') {
        setSnackbar({
          open: true,
          message: 'Notifications enabled successfully',
          severity: 'success'
        });
      } else {
        setSnackbar({
          open: true,
          message: 'Notifications permission denied',
          severity: 'warning'
        });
      }
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      setSnackbar({
        open: true,
        message: 'Failed to enable notifications',
        severity: 'error'
      });
    }
  };

  const handleNewLog = (log) => {
    // Determine notification severity based on log type
    const getSeverity = (type) => {
      switch (type) {
        case 'error':
          return 'high';
        case 'warning':
          return 'medium';
        default:
          return 'low';
      }
    };

    // Show browser notification if permitted
    if (permission === 'granted') {
      const severity = getSeverity(log.type);
      const notification = new Notification('Device Alert', {
        body: `${log.type}: ${log.data}`,
        icon: '/favicon.ico', // Add your app icon path
        tag: `device-alert-${Date.now()}`,
        badge: '/notification-badge.png', // Add your badge icon path
        timestamp: log.timestamp,
        requireInteraction: severity === 'high', // Keep notification for high severity alerts
        silent: severity === 'low' // Silent notification for low severity
      });

      // Handle notification click
      notification.onclick = () => {
        window.focus();
        notification.close();
      };

      // Auto close low severity notifications
      if (severity === 'low') {
        setTimeout(() => notification.close(), 5000);
      }
    }

    // Show in-app notification
    setSnackbar({
      open: true,
      message: `${log.type}: ${log.data}`,
      severity: log.type === 'error' ? 'error' : log.type === 'warning' ? 'warning' : 'info'
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  return (
    <>
      {permission === 'default' && (
        <Button
          variant="contained"
          color="primary"
          onClick={requestNotificationPermission}
          sx={{ position: 'fixed', bottom: 16, right: 16, zIndex: 1000 }}
        >
          Enable Notifications
        </Button>
      )}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default Notifications;