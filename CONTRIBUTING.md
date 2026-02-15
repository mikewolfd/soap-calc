# Contributing to Soap Calc

Thank you for your interest in contributing to Soap Calc!

## Getting Started

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/soap-calc.git
    cd soap-calc
    ```

2.  **Set up development environment**:
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -e .
    pip install pytest
    ```

3.  **Run Tests**:
    Ensure all tests pass before submitting changes.
    ```bash
    pytest
    ```

## Submitting Changes

1.  Create a new branch for your feature or bugfix.
2.  Write tests for your changes.
3.  Ensure existing tests pass.
4.  Submit a Pull Request with a clear description of your changes.

## Code Style

-   Follow PEP 8 guidelines.
-   Use descriptive variable and function names.
-   Adddocstrings to functions and classes.

## Adding Oils

If you are adding a new oil to the database (`data/oils.json`), please ensure you provide accurate SAP values and fatty acid profiles from a reputable source. References (links) in the PR description are appreciated.
