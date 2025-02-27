# Fatakeshto Application Backend

This is a FastAPI-based backend system designed to manage remote devices efficiently. It includes features such as user authentication, device control, real-time communication, and background task scheduling. The project leverages a Neon PostgreSQL database for secure and scalable data storage, built with a focus on performance, security, and extensibility.

## Features

### 1. User Authentication & Management

- **JWT-based Authentication**: Secure token-based login system.
- **Role-Based Access Control (RBAC)**: Define roles (e.g., admin, standard, read-only).
- **User Registration & Login**: Endpoints for creating and accessing accounts.
- **Password Hashing**: Secure storage using bcrypt.
- **Account Management**: Update profiles, reset passwords, and recover accounts.
- **Multi-Factor Authentication (MFA)**: Optional OTP-based security layer.
- **Session Management**: Tokens expire after 30 minutes of inactivity.

### 2. Remote Device Control API

- **Shell Command Execution**: Send commands to devices and retrieve output in real time.
- **Process Management**: Start, stop, and monitor device processes.
- **File Operations**: Upload, download, delete, and rename files on devices.
- **Clipboard Access**: Read and write to device clipboards.
- **Power Control**: Reboot or shut down devices remotely.

### 3. Real-Time Communication

- **WebSocket Streaming**: Live updates for device status, GPS, screen captures, and keylogging.
- **Live Screen Monitoring**: Stream device screenshots in real time.
- **Push Notifications**: Alerts for device connectivity changes or suspicious activities.
- **Audio Streaming**: Placeholder for real-time audio capabilities.

### 4. Data Storage & Logging

- **NeonDB Integration**: Persistent storage for users, devices, and logs.
- **Device Logs**: Record command history and timestamps.
- **Log Rotation**: Manage storage with automated log rotation.
- **Audit Logs**: Track administrative actions for accountability.

### 5. Admin Panel API

- **Device Management**: Add, remove, or update device records.
- **User Management**: Full CRUD operations for user accounts.
- **Reports**: Generate and export activity logs in PDF or CSV formats.

### 6. Background Services & Task Scheduling

- **Periodic Data Collection**: Automatically gather device data at set intervals.
- **Auto-Reconnect**: Re-establish connections with offline devices.
- **Command Queue**: Queue commands for devices that are temporarily offline.
- **Maintenance Tasks**: Schedule log cleanup and health checks.

### 7. Additional Features

- **Rate Limiting**: Protect the API from abuse by limiting requests per IP.
- **Error Logging**: Detailed logs for troubleshooting.
- **Data Encryption**: Encrypt sensitive data both at rest and in transit.

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.8+
- Git: To clone the repository.
- Virtual Environment Tool: Such as venv or conda.
- Neon Database URL: Obtain this from your Neon account for database access.

## Project Structure

The project follows a modular architecture for better maintainability and scalability:

```
backend/
├── database.py         # Database connection and configuration
├── models.py           # SQLAlchemy ORM models
├── schemas.py          # Pydantic models for request/response validation
├── utils.py            # Utility functions and helper methods
├── main.py            # Application entry point and FastAPI app configuration
├── routers/           # API route handlers
│   ├── auth.py        # Authentication endpoints
│   ├── devices.py     # Device management endpoints
│   └── admin.py       # Administrative endpoints
├── services/
│   └── tasks.py       # Background tasks and scheduled jobs
├── Dockerfile         # Container configuration for the backend
└── docker-compose.yml # Multi-container Docker configuration
```

### Key Components

- **database.py**: Manages database connections and configurations using SQLAlchemy with Neon PostgreSQL.
- **models.py**: Defines database models using SQLAlchemy ORM for users, devices, and other entities.
- **schemas.py**: Contains Pydantic models for request/response validation and data serialization.
- **utils.py**: Houses utility functions, helpers, and common functionality used across the application.
- **main.py**: The application entry point that configures FastAPI, middleware, and routes.

#### Routers
- **auth.py**: Implements authentication endpoints including login, registration, and token management.
- **devices.py**: Handles device-related operations such as control, monitoring, and file operations.
- **admin.py**: Provides administrative endpoints for user and device management.

#### Services
- **tasks.py**: Implements background tasks and scheduled jobs for data collection and maintenance.

#### Docker Configuration
- **Dockerfile**: Contains instructions for building the backend container image.
- **docker-compose.yml**: Defines the multi-container setup including the backend and database services.