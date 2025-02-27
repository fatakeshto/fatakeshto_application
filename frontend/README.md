# Fatakeshto Application Frontend

A modern React-based frontend for the Fatakeshto Application, featuring real-time monitoring capabilities, device management, and user authentication.

## Features

- **Real-Time Monitoring**: Live screen sharing and device metrics tracking using WebSocket
- **Device Management**: Comprehensive file management system for connected devices
- **User Authentication**: Secure login system with role-based access control
- **Responsive Design**: Material-UI components for a modern, mobile-friendly interface

## Tech Stack

- React 19.0.0
- Material-UI 6.4.6
- React Router DOM 7.2.0
- Axios for HTTP requests
- Socket.io for real-time communication
- Vite as the build tool

## Getting Started

### Prerequisites

- Node.js (Latest LTS version recommended)
- npm or yarn package manager

### Installation

1. Clone the repository
2. Navigate to the frontend directory
3. Install dependencies:
   ```bash
   npm install
   ```

### Development

Run the development server:
```bash
npm run dev
```

Build for production:
```bash
npm run build
```

Lint the code:
```bash
npm run lint
```

## Project Structure

```
src/
├── components/        # React components
│   ├── Dashboard.jsx  # Main dashboard view
│   ├── FileManager.jsx # File management interface
│   ├── LiveMonitoring.jsx # Real-time monitoring
│   ├── Login.jsx     # Authentication component
│   └── UserManagement.jsx # User administration
├── services/         # API and WebSocket services
├── assets/          # Static assets
└── App.jsx          # Main application component
```

## Key Components

### LiveMonitoring
Implements real-time screen sharing and device metrics tracking using WebSocket connections.

### FileManager
Provides a user interface for managing files and folders on connected devices.

### Login
Handles user authentication with JWT token management and role-based access.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License.
