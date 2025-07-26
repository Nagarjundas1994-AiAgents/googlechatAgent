# Contributing to Google Chat Agent

Thank you for considering contributing to the Google Chat Agent project! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

Bugs are tracked as GitHub issues. Create an issue and provide the following information:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the bug
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed and what you expected to see
- Include screenshots if possible
- Include details about your environment (OS, browser, etc.)

### Suggesting Enhancements

Enhancement suggestions are also tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- A detailed description of the proposed functionality
- Any possible implementation details
- Why this enhancement would be useful to most users

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure they pass
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure your environment variables
6. Run the application: `uvicorn app.main:app --reload`

### Testing

Before submitting a pull request, make sure all tests pass:

```bash
python -m pytest tests/
```

Add tests for new features to ensure they work as expected.

## Style Guidelines

### Code Style

This project follows PEP 8 style guidelines for Python code. Use tools like `flake8` and `black` to ensure your code adheres to these standards.

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license.

## Questions?

If you have any questions, feel free to create an issue with the tag `question`.

Thank you for contributing to Google Chat Agent!