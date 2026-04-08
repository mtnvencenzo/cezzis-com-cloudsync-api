
# Cezzis.com CloudSync API

A message-forwarding microservice that receives cocktail update events from RabbitMQ via a Dapr input binding and publishes them to Kafka via Dapr pub/sub.

## Overview

**Status:** Work In Progress (WIP) — This project is in its early stages and actively under development.

The CloudSync API acts as a bridge in the Cezzis.com event-driven architecture, synchronizing cocktail data changes across services. It listens for incoming messages on a RabbitMQ queue through a Dapr input binding and forwards them to a Kafka topic through Dapr pub/sub.

### Key Features
- FastAPI-based API with OpenAPI 3.0 specification
- Dapr input binding (RabbitMQ) to pub/sub (Kafka) message forwarding
- Dapr API token and App API token authorization
- OpenTelemetry instrumentation for observability
- Modular clean architecture (Application / Domain / Infrastructure layers)
- Scalar API documentation at `/scalar/v1`
- Health check and readiness endpoints
- Structured error handling with RFC 7807 Problem Details

### Architecture
```
src/cezzis_com_cloudsync_api/
├── apis/              # API endpoints (health check, integrations, docs)
├── application/       # Application layer
│   ├── behaviors/     # Cross-cutting concerns (auth, error handling, OpenTelemetry)
│   └── concerns/      # Feature-specific logic (health, integrations)
├── domain/            # Domain models, config, and service interfaces
│   ├── config/        # Application settings (App, Dapr, OAuth, OTEL)
│   └── services/      # Service interfaces (IMessageBus)
└── infrastructure/    # Dapr client, message bus implementation
```

## API Endpoints

### Integration
- **POST** `/{binding-name}` — Dapr input binding endpoint that receives cocktail update events and forwards them to Kafka

### Health
- **GET** `/api/v1/health/liveness` — Liveness probe
- **GET** `/api/v1/health/readiness` — Readiness probe (checks Dapr sidecar connectivity)

## Getting Started

### Prerequisites
- Python 3.12 or higher
- Poetry 2.x for dependency management
- Dapr CLI (for local development with sidecar)

### Installation

Install dependencies using Poetry:

```bash
poetry install
```

### Configuration

The API uses environment variables for configuration. Copy `.env` to `.env.loc` and populate values. Key settings include:
- Dapr connection (host, ports, API tokens)
- OAuth 2.0 settings (domain, client ID, audience)
- OpenTelemetry configuration
- Application options (service name, allowed origins, topic/binding names)

### Running the API

#### Using VS Code Debugger (Recommended)
Launch the API in debug mode using the **"Debug: CloudSync API"** configuration (F5):
- Runs on port `8017`
- Auto-reload enabled
- Sets `ENV=loc` environment variable

#### Using the Dapr Sidecar
Use the VS Code task **"dapr-run-docker"** or **"dapr-run-k8s"** to start the API with a Dapr sidecar.

#### Using Command Line
```bash
cd src/cezzis_com_cloudsync_api
ENV=loc uvicorn main:app --reload --port 8017
```

The API will be available at `http://localhost:8017`.

### API Documentation

Once running, access the interactive API documentation:
- **Scalar UI**: `http://localhost:8017/scalar/v1`
- **OpenAPI JSON**: `http://localhost:8017/scalar/v1/openapi.json`

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

- **FastAPI** — Web framework
- **Dapr** — Distributed runtime (input binding, pub/sub)
- **Pydantic** — Data validation and settings management
- **OAuth 2.0** — Authentication and authorization (via `cezzis-oauth`)
- **OpenTelemetry** — Distributed tracing and observability
- **Scalar** — API documentation UI
- **Mediatr** — CQRS pattern implementation
- **Injector** — Dependency injection
- **pytest** — Testing framework

## Project Structure

- `src/cezzis_com_cloudsync_api/` — Main application code
  - `main.py` — Application entry point
  - `app_module.py` — Dependency injection configuration
  - `apis/` — REST API endpoints
  - `application/behaviors/` — Middleware and cross-cutting concerns
  - `application/concerns/` — Business logic and use cases
  - `domain/config/` — Configuration models
  - `infrastructure/` — Dapr client and message bus
- `test/` — Test suite
  - `unit/` — Unit tests
  - `integration/` — Integration tests
- `.iac/` — Infrastructure as Code (K8s manifests, Dapr components)

## License

### Deploy

#### CloudSync
``` shell
# app
kubectl apply -f https://raw.githubusercontent.com/mtnvencenzo/cezzis-com-coudsync-api/refs/heads/main/.iac/argocd/cezzis-com-cloudsync-api-cloudsync.yaml

# image updater
kubectl apply -f https://raw.githubusercontent.com/mtnvencenzo/cezzis-com-coudsync-api/refs/heads/main/.iac/argocd/image-updater-cloudsync.yaml
```

### Remove 
``` shell
kubectl delete -f https://raw.githubusercontent.com/mtnvencenzo/cezzis-com-cloudsync-api/refs/heads/main/.iac/argocd/cezzis-com-cloudsync-api-cloudsync.yaml

kubectl delete -f https://raw.githubusercontent.com/mtnvencenzo/cezzis-com-cloudsync-api/refs/heads/main/.iac/argocd/image-updater-cloudsync.yaml
```

#### Loc
``` shell
# app
kubectl apply -f https://raw.githubusercontent.com/mtnvencenzo/cezzis-com-cloudsync-api/refs/heads/main/.iac/argocd/cezzis-com-cloudsync-api-loc.yaml

# image updater
kubectl apply -f https://raw.githubusercontent.com/mtnvencenzo/cezzis-com-cloudsync-api/refs/heads/main/.iac/argocd/image-updater-loc.yaml
```

### Remove 
``` shell
kubectl delete -f https://raw.githubusercontent.com/mtnvencenzo/cezzis-com-cloudsync-api/refs/heads/main/.iac/argocd/cezzis-com-cloudsync-api-loc.yaml

kubectl delete -f https://raw.githubusercontent.com/mtnvencenzo/cezzis-com-cloudsync-api/refs/heads/main/.iac/argocd/image-updater-loc.yaml
```

This project is licensed under the MIT License.