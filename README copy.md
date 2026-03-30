
# Cezzis.com Accounts API

This repository provides the backend API for user account management, profile operations, and authentication as part of the Cezzis.com platform.

## Overview

**Status:** Work In Progress (WIP) — This project is in its early stages and actively under development.

The Accounts API manages user profiles, authentication, preferences, and account-related operations for the Cezzis.com ecosystem. This API is being migrated from the existing cocktails API to provide a dedicated microservice for account management.

### Key Features
- FastAPI-based RESTful API with OpenAPI 3.0 specification
- OAuth 2.0 authentication with PKCE flow
- Comprehensive user profile management
- API key authorization support (APIM Host Key)
- OpenTelemetry instrumentation for observability
- Modular clean architecture (Application/Domain/Infrastructure layers)
- Scalar API documentation at `/scalar/v1`
- Health check endpoints
- Structured error handling with RFC 7807 Problem Details

### Architecture
```
src/cezzis_com_cloudsync_api/
├── apis/              # API endpoints (health check, documentation)
├── application/       # Application layer
│   ├── behaviors/     # Cross-cutting concerns (auth, error handling, OpenTelemetry)
│   └── concerns/      # Feature-specific logic
├── domain/            # Domain models and configuration
│   └── config/        # Application settings (OAuth, OTEL, app options)
└── infrastructure/    # External integrations and repositories
```

## API Endpoints

### Account Profile Management
The following endpoints will be migrated to this API:

#### Profile Operations
- **POST** `/api/v1/accounts/owned/profile` - Login/create account profile
- **GET** `/api/v1/accounts/owned/profile` - Get authenticated user's profile
- **PUT** `/api/v1/accounts/owned/profile` - Update profile information

#### Account Settings
- **PUT** `/api/v1/accounts/owned/profile/email` - Change email address
- **PUT** `/api/v1/accounts/owned/profile/username` - Change username
- **PUT** `/api/v1/accounts/owned/profile/password` - Initiate password change flow
- **PUT** `/api/v1/accounts/owned/profile/accessibility` - Update accessibility settings
- **PUT** `/api/v1/accounts/owned/profile/notifications` - Update notification preferences
- **POST** `/api/v1/accounts/owned/profile/image` - Upload profile image

#### Cocktail-Related Profile Features
- **PUT** `/api/v1/accounts/owned/profile/cocktails/favorites` - Manage favorite cocktails
- **POST** `/api/v1/accounts/owned/profile/cocktails/ratings` - Rate a cocktail
- **GET** `/api/v1/accounts/owned/profile/cocktails/ratings` - Get user's cocktail ratings
- **POST** `/api/v1/accounts/owned/profile/cocktails/recommendations` - Submit cocktail recommendation

### Authentication
All endpoints require:
- **X-Key** header: APIM subscription key
- **OAuth 2.0** Bearer token with appropriate scopes

#### OAuth Scopes
- **`read:owned-account`** - Required for reading user's own account data
- **`write:owned-account`** - Required for modifying user's own account data

Most write operations require both scopes, while read-only operations only require the `read:owned-account` scope.

## Getting Started

### Prerequisites
- Python 3.12 or higher
- Poetry for dependency management

### Installation

Install dependencies using Poetry:

```bash
poetry install
```

### Configuration

The API uses environment variables for configuration. Key settings include:
- OAuth 2.0 settings (domain, client ID, audience)
- OpenTelemetry configuration
- Application options (service name, version, host)

### Running the API

#### Using VS Code Debugger (Recommended)
Launch the API in debug mode using the **"Debug: Accounts API"** configuration (F5):
- Runs on port `8015`
- Auto-reload enabled
- Automatically opens Scalar documentation when ready
- Sets `ENV=loc` environment variable

#### Using Command Line
From the project root, start the development server:

```bash
cd src/cezzis_com_cloudsync_api
ENV=loc uvicorn main:app --reload --port 8015
```

Or using Poetry from the project root:

```bash
poetry run uvicorn src.cezzis_com_cloudsync_api.main:app --reload --port 8015
```

The API will be available at `http://localhost:8015`.

### API Documentation

Once running, access the interactive API documentation:
- **Scalar UI**: `http://localhost:8015/scalar/v1`
- **OpenAPI JSON**: `http://localhost:8015/scalar/v1/openapi.json`

You can also use the VS Code task **"OpenApiRoot"** to open the Scalar documentation in your browser.

### Testing

Run the test suite:

```bash
poetry run pytest
```

### Testing

Run the test suite:

```bash
poetry run pytest
```

Run tests with coverage:

```bash
poetry run pytest --cov=src/cezzis_com_cloudsync_api --cov-report=html
```

## Technology Stack

- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and settings management
- **OAuth 2.0** - Authentication and authorization (via `cezzis-oauth` libraries)
- **OpenTelemetry** - Distributed tracing and observability
- **Scalar** - API documentation UI
- **Mediatr** - CQRS pattern implementation
- **Injector** - Dependency injection
- **pytest** - Testing framework

## Project Structure

- `src/cezzis_com_cloudsync_api/` - Main application code
  - `main.py` - Application entry point
  - `app_module.py` - Dependency injection configuration
  - `apis/` - REST API endpoints
  - `application/behaviors/` - Middleware and cross-cutting concerns
  - `application/concerns/` - Business logic and use cases
  - `domain/config/` - Configuration models
  - `infrastructure/repositories/` - Data access layer
- `test/` - Test suite
  - `unit/` - Unit tests
  - `integration/` - Integration tests
- `terraform/` - Infrastructure as Code

## Contributing

Contributions are welcome! Please open issues or pull requests to help improve the API and its capabilities.

## License

This project is licensed under the MIT License.