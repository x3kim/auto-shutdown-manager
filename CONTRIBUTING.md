# Contributing to Auto Shutdown Manager

Thank you for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/x3kim/auto-shutdown-manager.git
cd auto-shutdown-manager
pip install -r requirements.txt
```

## Making Changes

1. Fork the repository and create a branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes.
3. Ensure all checks pass locally:
   ```bash
   ruff check .
   pytest tests/ --verbose
   ```
4. Commit with a clear message and open a Pull Request.

## Code Style

- Formatting: [Ruff](https://docs.astral.sh/ruff/)
- Run `ruff check .` before committing — CI will enforce this.

## Reporting Bugs

Use the [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) template when opening an issue.

## Suggesting Features

Use the [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) template.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
