# Changelog

All notable changes to this project will be documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-04-01
### Added
- System tray icon with minimize-to-tray support
- Automatic EXE build and GitHub Release via CI/CD (PyInstaller + GitHub Actions)
- `requirements.txt`, `pyproject.toml`, `build.spec` for reproducible builds
- Ruff linting enforced in CI
- Automated tests with pytest
- MIT License

### Changed
- Icon generation improved (PIL ImageDraw fallback when no `icon.ico` present)
- Idle monitoring enhanced with keep-awake mode (`SetThreadExecutionState`)

### Fixed
- Ruff linting errors (indentation, unused variables, bare excepts)
- `test_get_idle_seconds`: removed invalid `ctypes.byref` side_effect

## [1.0.0] - 2026-01-29
### Added
- Core idle monitoring (`IdleMonitor`) with configurable threshold
- Shutdown, restart, hibernate, and sleep actions
- CustomTkinter UI with dark mode support
- German/English localization
- Configurable settings persistence (`settings.json`)
- Warning dialog before executing power action
