# Changelog
All notable changes to this project will be documented in this file.

## [0.0.3] - 2026-01-08
### Added
- `--master` CLI flag to enable master node mode (schedules tasks)
- `--consumers N` CLI flag to configure number of consumer worker threads (0 disables consumers)
- `--environment {local,production}` CLI flag to set environment mode
- `--admin-username` and `--admin-password` CLI flags to set admin credentials
- `--verbose` CLI flag to enable verbose logging with HTTP access logs
- Support for nodes to operate as both master and consumer simultaneously
- Automatic auto-reload when environment is set to "local"

### Changed
- Replaced `--workers` and `--reload` CLI flags with new `--master` and `--consumers` flags
- Replaced `SCHEDULER_NODE_TYPE` configuration with `IS_MASTER_MODE` boolean flag
- Default `SCHEDULER_WORKERS` changed from 4 to 0 (consumers disabled by default)
- Default `ENVIRONMENT` changed from "local" to "production"
- Removed "staging" from environment options (now only "local" and "production")
- Default host binding: 127.0.0.1 for non-master nodes, 0.0.0.0 for master nodes in production
- FastAPI server now always runs with a single worker (consumer workers are separate)
- Admin credentials validation now only required when master mode is enabled
- Task list API endpoint now returns raw task data instead of Task model instances
- Node status API now returns node_type as "master", "consumer", "both", or "none"
- Redis connection now uses `decode_responses=False` for better compatibility
- Improved logging messages and error handling throughout scheduler components

### Fixed
- Fixed Redis decode_responses configuration for better compatibility
- Fixed task parsing error messages formatting

## [0.0.2] - 2026-01-07
### Added
- Default values for admin credentials (`ADMIN_USERNAME` and `ADMIN_PASSWORD`) to simplify local setup
- Default admin username: `admin@example.com`
- Default admin password: `changethis`

### Changed
- Renamed `FIRST_SUPERUSER` environment variable to `ADMIN_USERNAME`
- Renamed `FIRST_SUPERUSER_PASSWORD` environment variable to `ADMIN_PASSWORD`
- Admin credentials now have default values (previously required to be set)
- Validation warnings now use logging instead of Python warnings module
- Updated `.env.sample` and `.env.test` files to use new variable names

## [0.0.1] - 2026-01-07
### Added
- OctoBot Node alpha version
