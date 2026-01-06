# OctoBot Node

<p align="middle">
<img src="public/assets/images/octobot_node_256.png" height="256" alt="OctoBot Node logo">
</p>

<p align="center">
<em>Run any OctoBot, anywhere, with ease</em>
</p>

This project is related to [OctoBot](https://github.com/Drakkar-Software/OctoBot).

## Usage

### CLI

OctoBot-Node provides a command-line interface (CLI) for starting the server and managing the application.

#### Basic Usage

Start the server with default settings:
```bash
python start.py
```

Or if installed via pip:
```bash
octobot_node
```

#### CLI Options

- `-v, --version`: Show OctoBot-Node current version
- `--host HOST`: Host to bind the server to (default: 0.0.0.0)
- `--port PORT`: Port to bind the server to (default: 8000)
- `--workers WORKERS`: Number of worker processes (default: 1)
- `--reload`: Enable auto-reload for development (only works with single worker)

#### Examples

Start the server on a custom host and port:
```bash
python start.py --host 127.0.0.1 --port 9000
```

Start with multiple workers for production:
```bash
python start.py --workers 4
```

Start in development mode with auto-reload:
```bash
python start.py --reload
```

Show version:
```bash
python start.py --version
```

### With Redis

For using Redis as the scheduler backend:
```bash
docker run -p 6379:6379 --name redis -d redis redis-server --save 60 1 --loglevel warning
```

## Developers
### Prerequisites

Before proceeding, ensure you have [**Python 3.10+**](https://www.python.org) and [**Node.js 20+**](https://nodejs.org) installed on your system.

Once you have installed Python and Node.js, run the following commands:
```bash
npm install
pip install -r requirements.txt
cp .env.sample .env
```

### Web UI

The Web UI can be used in two modes: **static** and **dynamic (development)**. The Web UI is built using [React](https://github.com/facebook/react), [Vite](https://github.com/vitejs/vite), [TanStack](https://github.com/TanStack) and [shadcn-ui](https://github.com/shadcn-ui/ui).

#### Static Web UI

If you do not need to modify the Web UI code, it is recommended to use the static mode for better performance. 
To build the static assets, run:
```bash
npm run build
```
After building, start the FastAPI server. The static Web UI will be available at [http://localhost:8000/app](http://localhost:8000/app).

#### Dynamic (Development) Web UI

If you plan to actively develop or modify the Web UI, use the dynamic development mode. This provides hot-reload and the latest changes instantly.
To run the Web UI in development mode, use:
```bash
npm run ui:dev
```
This will start the development server, typically available at [http://localhost:3000](http://localhost:3000). You can access the UI separately while developing.
For API integration during development, make sure your FastAPI backend server is running simultaneously. The development server will proxy API requests to the backend as configured.

### OpenAPI

Whenever you update or add routes in `octobot_node/app/api`, you need to regenerate the [OpenAPI specification](https://github.com/OAI/OpenAPI-Specification) and the UI OpenAPI client. This can be done easily with the provided script:
```bash
bash ./generate-client.sh
```

### API Server

The API server is built using [FastAPI](https://github.com/fastapi) and provides the backend REST endpoints and websocket interface for OctoBot Node.

#### Running the FastAPI Server

You can start the API server using the CLI (recommended):

```bash
python start.py --workers 1
```

Or directly with uvicorn:

```bash
uvicorn octobot_node.app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

- By default, the server runs on [http://localhost:8000](http://localhost:8000).
- You can configure environment variables via `.env`, including host, port, and scheduler/backend settings.
- For development: Use `--reload` flag or fewer workers (e.g. `--workers 1`), so that code changes are picked up more easily.
- For production: Increase the number of workers using `--workers` option.

##### Environment Variables

Some key `.env` variables:
- `SCHEDULER_BACKEND` (redis, sqlite, etc.)
- `SCHEDULER_REDIS_URL` (if using Redis)
- `SCHEDULER_SQLITE_FILE` (if using SQLite)
- `SCHEDULER_NODE_TYPE` ("master" or "worker")
- `SCHEDULER_WORKERS` (number of consumer workers)

See `.env.sample` for all options, and adjust as needed.

#### Scheduler

The task scheduler is automatically started together with the FastAPI server through import of the `octobot_node/app/scheduler` module. The scheduler uses [Huey](https://github.com/coleifer/huey) for task queue management.

- **No manual launch needed** — scheduler and consumers are managed by the FastAPI app on startup.
- Configuration for the scheduler backend (Redis or SQLite) is picked up from environment variables.
- When `SCHEDULER_NODE_TYPE=worker`, background consumers process tasks automatically. When set to `master`, consumer threads are skipped by design.
