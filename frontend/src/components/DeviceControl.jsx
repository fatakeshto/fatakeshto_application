import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, TextField, Button, Grid } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import axios from 'axios';
import wsService from '../services/websocket';
import { useParams } from 'react-router-dom';

const DeviceControl = () => {
  const { deviceId } = useParams();
  const [command, setCommand] = useState('');
  const [commandOutput, setCommandOutput] = useState('');
  const [clipboard, setClipboard] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [streamingStatus, setStreamingStatus] = useState({
    screen: false,
    audio: false
  });

  useEffect(() => {
    wsService.subscribe('command_result', handleCommandResult);
    wsService.subscribe('screen_data', handleScreenData);
    wsService.subscribe('audio_stream', handleAudioStream);

    return () => {
      wsService.unsubscribe('command_result', handleCommandResult);
      wsService.unsubscribe('screen_data', handleScreenData);
      wsService.unsubscribe('audio_stream', handleAudioStream);
      
      if (streamingStatus.screen) wsService.stopScreenShare(deviceId);
    };
  }, [deviceId]);

  const handleCommandSubmit = async () => {
    if (!command.trim()) return;

    setLoading(true);
    setError(null);

    try {
      wsService.sendCommand(deviceId, command);
      setCommand('');
    } catch (err) {
      setError('Failed to send command');
      console.error('Command error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCommandResult = (data) => {
    if (data.deviceId === deviceId) {
      setCommandOutput(prev => `${prev}\n${data.output}`);
    }
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Device Control
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Command Execution
            </Typography>
            <TextField
              fullWidth
              label="Enter Command"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              margin="normal"
            />
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                color="primary"
                startIcon={<PlayArrowIcon />}
                onClick={handleCommandSubmit}
              >
                Execute
              </Button>
              <Button
                variant="contained"
                color="error"
                startIcon={<StopIcon />}
              >
                Stop
              </Button>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Command Output
            </Typography>
            <Box
              sx={{
                bgcolor: 'black',
                color: 'lightgreen',
                p: 2,
                borderRadius: 1,
                fontFamily: 'monospace',
                minHeight: 200,
                maxHeight: 400,
                overflow: 'auto',
              }}
            >
              {output || 'No output to display'}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DeviceControl;