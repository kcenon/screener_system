# Contributing Guide

Thank you for your interest in contributing to the Stock Screening Platform!

This guide will help you get started with contributing to the project.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please read and follow our [Code of Conduct](https://github.com/kcenon/screener_system/blob/main/CODE_OF_CONDUCT.md).

## Ways to Contribute

### Reporting Bugs
Found a bug? Please [create an issue](https://github.com/kcenon/screener_system/issues/new?template=bug_report.md) with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (browser, OS, etc.)

### Suggesting Features
Have an idea? [Submit a feature request](https://github.com/kcenon/screener_system/issues/new?template=feature_request.md) with:
- Clear description of the feature
- Use case and benefits
- Potential implementation approach
- Mockups or examples if applicable

### Improving Documentation
Documentation improvements are always welcome:
- Fix typos or unclear explanations
- Add examples or tutorials
- Translate documentation
- Improve API references

### Contributing Code
Ready to code? Follow these steps:

## Development Setup

### Prerequisites
- Git
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Getting Started

1. **Fork the repository**
   ```bash
   # Fork via GitHub UI, then clone your fork
   git clone https://github.com/YOUR_USERNAME/screener_system.git
   cd screener_system
   ```

2. **Set up the development environment**
   ```bash
   # Start all services
   docker-compose up -d

   # Install frontend dependencies
   cd frontend
   npm install

   # Install backend dependencies
   cd ../backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Run tests**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

## Development Workflow

### Creating a Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

### Making Changes

1. Write clean, readable code
2. Follow coding standards (see below)
3. Add tests for new features
4. Update documentation as needed
5. Commit with clear messages

### Coding Standards

#### Python (Backend)
- Follow [PEP 8](https://pep8.org/)
- Use type hints
- Write docstrings (Google style)
- Maximum line length: 88 (Black formatter)
- Use `async/await` for async operations

```python
async def get_stock(stock_code: str) -> Stock:
    """
    Retrieve stock information by code.

    Args:
        stock_code: The stock ticker code (e.g., "005930").

    Returns:
        Stock object with current data.

    Raises:
        StockNotFoundError: If stock code doesn't exist.
    """
    # Implementation
```

#### TypeScript (Frontend)
- Follow [TypeScript guidelines](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)
- Use functional components with hooks
- Prefer named exports
- Use TSDoc comments for exported functions

```typescript
/**
 * Formats stock price with appropriate precision.
 * @param price - The stock price to format
 * @param currency - Currency symbol (default: '₩')
 * @returns Formatted price string
 */
export function formatPrice(price: number, currency = '₩'): string {
  // Implementation
}
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(screening): add custom indicator support

fix(portfolio): correct ROI calculation for split stocks

docs(api): add WebSocket event examples

test(backend): add integration tests for alert service
```

### Running Tests

```bash
# Backend tests with coverage
cd backend
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

### Creating a Pull Request

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR via GitHub UI**
   - Fill out the PR template
   - Link related issues
   - Add screenshots if UI changes
   - Request review from maintainers

3. **Address review feedback**
   - Make requested changes
   - Push updates to the same branch
   - Respond to comments

4. **Merge**
   - PR will be merged once approved
   - Branch will be deleted automatically

## Code Review Process

All contributions go through code review:
1. Automated checks (CI/CD)
2. Code quality review
3. Functionality testing
4. Documentation review

## Getting Help

- **Questions?** [Ask in Discussions](https://github.com/kcenon/screener_system/discussions)
- **Stuck?** Comment on your PR or issue
- **Chat?** Join our [Discord community](#)

## Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing! 🎉

## Next Steps

- [Architecture Overview](/docs/architecture/overview)
- [API Reference](/docs/api/intro)
- [Development Guide](/docs/contributing/development)
- [Testing Guide](/docs/contributing/testing)
