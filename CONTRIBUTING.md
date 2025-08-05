# Contributing to Vertiport Autonomy

Thank you for your interest in contributing to the Vertiport Autonomy project! We welcome contributions from the community to help improve this Deep Reinforcement Learning platform for autonomous vertiport coordination.

## 🚀 Getting Started

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/N-cryptd/vertiport-autonomy.git
   cd vertiport-autonomy
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Activate on Linux/Mac
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

### Project Structure

```
vertiport-autonomy/
├── src/vertiport_autonomy/    # Main package
│   ├── core/                  # Core simulation components
│   ├── config/                # Configuration management
│   ├── agents/                # Agent implementations
│   ├── training/              # Training utilities
│   └── evaluation/            # Evaluation framework
├── scripts/                   # Executable scripts
├── scenarios/                 # Configuration files
├── tests/                     # Test suite
└── docs/                      # Documentation
```

## 🔧 Development Guidelines

### Code Style

We follow PEP 8 and use automated tools to maintain consistent code style:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run these tools before committing:

```bash
# Format code
black src/ scripts/ tests/
isort src/ scripts/ tests/

# Check linting
flake8 src/ scripts/ tests/

# Type checking
mypy src/vertiport_autonomy/
```

### Code Quality Standards

1. **Type Hints**: Add type hints to all public functions and class methods
2. **Docstrings**: Write clear docstrings for all public functions and classes
3. **Testing**: Write tests for new functionality
4. **Documentation**: Update documentation for significant changes

### Example Code Style

```python
"""Module docstring describing the purpose."""

from typing import Dict, List, Optional
import numpy as np

from vertiport_autonomy.core.simulator import VertiportSim


class ExampleAgent:
    """Example agent class with proper documentation.
    
    Args:
        name: Human-readable name for the agent
        config: Configuration dictionary
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None) -> None:
        """Initialize the agent."""
        self.name = name
        self.config = config or {}
    
    def act(self, observation: np.ndarray) -> np.ndarray:
        """Select actions based on observation.
        
        Args:
            observation: Current environment observation
            
        Returns:
            Array of actions for each drone
        """
        # Implementation here
        pass
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/vertiport_autonomy --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run tests excluding slow ones
pytest -m "not slow"
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern

Example test:

```python
import pytest
import numpy as np
from vertiport_autonomy.agents.heuristic import SimpleHeuristicAgent


def test_simple_heuristic_agent_initialization():
    """Test that SimpleHeuristicAgent initializes correctly."""
    # Arrange
    agent_name = "test_agent"
    
    # Act
    agent = SimpleHeuristicAgent(agent_name)
    
    # Assert
    assert agent.name == agent_name


def test_simple_heuristic_agent_action_shape():
    """Test that agent returns correct action shape."""
    # Arrange
    agent = SimpleHeuristicAgent("test")
    observation = {
        "drones_state": np.random.random((5, 10))  # 5 drones
    }
    
    # Act
    actions = agent.act(observation)
    
    # Assert
    assert actions.shape == (5,)
    assert actions.dtype == np.int32
```

## 📝 Documentation

### Updating Documentation

- Update docstrings for any modified functions/classes
- Update the README.md if adding new features
- Add examples for new functionality
- Update the CHANGELOG.md

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation (future feature)
# sphinx-build -b html docs/ docs/_build/
```

## 🔄 Pull Request Process

### Before Submitting

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test your changes**
   ```bash
   pytest
   black --check src/ scripts/ tests/
   isort --check-only src/ scripts/ tests/
   flake8 src/ scripts/ tests/
   mypy src/vertiport_autonomy/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new agent implementation"
   ```

### Commit Message Format

Use conventional commits format:

- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `style:` code style changes
- `refactor:` code refactoring
- `test:` adding tests
- `chore:` maintenance tasks

### Submitting the Pull Request

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request on GitHub**
   - Use a descriptive title
   - Explain what changes you made
   - Reference any related issues
   - Include screenshots if relevant

3. **Respond to feedback**
   - Address review comments promptly
   - Make requested changes
   - Keep the conversation friendly and professional

### Pull Request Requirements

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Changes are covered by tests
- [ ] No conflicts with main branch
- [ ] PR description is clear and complete

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Environment information**
   - Python version
   - Operating system
   - Package versions (`pip list`)

2. **Steps to reproduce**
   - Minimal code example
   - Expected behavior
   - Actual behavior

3. **Additional context**
   - Error messages
   - Log files
   - Screenshots if relevant

### Feature Requests

When requesting features:

1. **Use case description**
   - What problem does this solve?
   - How would you use this feature?

2. **Proposed solution**
   - How should it work?
   - API design considerations

3. **Alternatives considered**
   - Other approaches you've thought about

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and considerate
- Use inclusive language
- Focus on constructive feedback
- Help others learn and grow

### Getting Help

- **GitHub Discussions**: For questions and general discussion
- **Issues**: For bug reports and feature requests
- **Documentation**: Check existing docs first

### Recognition

Contributors will be recognized in:

- GitHub contributors list
- CHANGELOG.md for significant contributions
- Release notes for major features

## 📊 Project Roadmap

### Current Priorities

1. **Core Stability**
   - Bug fixes and performance improvements
   - Better test coverage
   - Documentation improvements

2. **Feature Enhancements**
   - Additional agent implementations
   - More evaluation metrics
   - Improved visualization tools

3. **Community Building**
   - Better onboarding experience
   - More examples and tutorials
   - Integration with other tools

### Future Goals

- Multi-agent coordination algorithms
- Real-time simulation capabilities
- Integration with industry standards
- Performance optimization

## 🙏 Questions?

Don't hesitate to reach out if you have questions:

- Open a GitHub Discussion
- Create an issue with the "question" label
- Check existing documentation and issues first

Thank you for contributing to Vertiport Autonomy! 🚁