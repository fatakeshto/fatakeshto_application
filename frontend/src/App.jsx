import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box, CssBaseline, Drawer, AppBar, Toolbar, List, Typography, Divider, IconButton, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Computer as DeviceIcon,
  Visibility as MonitoringIcon,
  People as UserIcon,
  ExitToApp as LogoutIcon
} from '@mui/icons-material';
import Dashboard from './components/Dashboard';
import DeviceControl from './components/DeviceControl';
import LiveMonitoring from './components/LiveMonitoring';
import Login from './components/Login';
import UserManagement from './components/UserManagement';

const drawerWidth = 240;

const PrivateRoute = ({ children }) => {
  const isAuthenticated = localStorage.getItem('token');
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const Layout = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const role = localStorage.getItem('role');

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    window.location.href = '/login';
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Live Monitoring', icon: <MonitoringIcon />, path: '/live-monitoring' },
    ...(role === 'admin' ? [{ text: 'User Management', icon: <UserIcon />, path: '/user-management' }] : [])
  ];

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Fatakeshto
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem button key={item.text} component="a" href={item.path}>
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem button onClick={handleLogout}>
          <ListItemIcon><LogoutIcon /></ListItemIcon>
          <ListItemText primary="Logout" />
        </ListItem>
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            Fatakeshto Application
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: ['48px', '56px', '64px']
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

const App = () => {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token && window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
    setIsLoading(false);
  }, []);

  if (isLoading) {
    return null;
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/device/:id"
          element={
            <PrivateRoute>
              <Layout>
                <DeviceControl />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/live-monitoring"
          element={
            <PrivateRoute>
              <Layout>
                <LiveMonitoring />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/user-management"
          element={
            <PrivateRoute>
              <Layout>
                <UserManagement />
              </Layout>
            </PrivateRoute>
          }
        />
      </Routes>
    </Router>
  );
};

export default App;
