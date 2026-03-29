# Update Docstring

Update or add docstrings to match code changes.

## Usage
/update-docstring <filepath or glob pattern>

**Supported formats:**
- Single file: `/update-docstring src/browser.py`
- Glob pattern: `/update-docstring src/*.py`
- Recursive: `/update-docstring src/**/*.py`

## Instructions
When this command is invoked:

1. **Analyze file**: Read and identify all classes and methods/functions

2. **Check docstrings**: For each class and method:
   - No docstring → create new
   - Docstring doesn't match code → update
   - Docstring is accurate → keep

3. **Check items**:
   - Class docstring: description, Args, Example
   - Method docstring: description, Args, Returns, Example
   - Parameter names and types match code
   - Return type matches code
   - Default values are documented correctly

4. **Use Google Style Docstring format**:
```python
def method(self, arg1: str, arg2: int = 10) -> bool:
    """Brief description

    Detailed description if needed.

    Args:
        arg1: First argument description
        arg2: Second argument description. Default 10

    Returns:
        Description of return value

    Raises:
        ValueError: When raised (if applicable)

    Example:
        >>> result = obj.method("test")
        >>> print(result)
    """
```

5. **Report changes**: After completion, report:
   - Newly added docstrings
   - Updated docstrings
   - Unchanged items count

## Example
```
/update-docstring src/*.py
```

This will:
1. Process all .py files in src/
2. Update/add docstrings in Korean
3. Report changes

## Notes
- All docstrings should be written in Korean
- Code logic is not changed (docstrings only)
- Examples should be actually runnable
- Skip `__init__.py` and test files if desired