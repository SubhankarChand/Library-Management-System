# Library Management System

## Overview

A comprehensive web-based library management system built with Flask that allows users to browse, borrow, and manage books. The system supports multiple user roles (admin, publisher, user) with role-based access control. Users can browse available books, publishers can add and manage their publications, and administrators can manage users and oversee the entire system.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Flask-based Architecture**: Uses Flask as the main web framework with a modular structure separating concerns across multiple files (app.py for configuration, routes.py for endpoints, models.py for data models, auth.py for authentication).
- **Template Engine**: Jinja2 templating with Bootstrap 5 for responsive UI design and Font Awesome for icons.

### Authentication & Authorization
- **Session-based Authentication**: Uses Flask sessions to manage user login state with secure session keys.
- **Role-based Access Control**: Three-tier permission system (user, publisher, admin) with decorators for protecting routes based on user roles.
- **Password Security**: Uses Werkzeug's password hashing utilities for secure password storage and verification.

### Database Layer
- **SQLAlchemy ORM**: Uses Flask-SQLAlchemy with declarative base for database modeling and operations.
- **Flexible Database Support**: Configurable database URL supporting SQLite for development and can be easily switched to PostgreSQL or other databases for production.
- **Database Models**: Three main entities - User, Book, and BorrowedBook with proper relationships and foreign key constraints.

### Application Structure
- **MVC Pattern**: Clear separation between models (data), views (templates), and controllers (routes).
- **Modular Design**: Authentication logic separated into its own module, making the codebase maintainable and testable.
- **Static Assets**: Organized CSS and JavaScript files for enhanced user experience and client-side functionality.

### User Interface
- **Responsive Design**: Bootstrap-based responsive interface that works across different device sizes.
- **Role-specific Dashboards**: Different dashboard views and navigation options based on user roles.
- **Interactive Features**: JavaScript-enhanced forms with validation, tooltips, and dynamic content updates.

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework for responsive design and UI components
- **Font Awesome 6.0.0**: Icon library for consistent iconography throughout the application

### Python Packages
- **Flask**: Core web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Werkzeug**: Password hashing and security utilities

### Database
- **SQLite**: Default development database (easily configurable to other databases like PostgreSQL)
- **Database Connection Pooling**: Configured with connection recycling and pre-ping for reliability

### Deployment Support
- **ProxyFix Middleware**: Configured to handle reverse proxy deployments correctly
- **Environment Configuration**: Uses environment variables for sensitive configuration like database URLs and session secrets