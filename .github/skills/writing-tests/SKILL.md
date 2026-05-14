---
name: writing-tests
description: This skill is used for writing tests to aid developers in ensuring code works properly. Use when a user mentions "writing tests", "adding code coverage", "testing new feature", asks to "write unit tests", or says "write a unit test for" something specific.
---

# Writing Tests

## Instructions

### Step 1: Activate virtual environment
Look for a `.venv` directory in the current workspace folder (e.g. `pyansys-geometry/.venv`). If one exists, activate it.
If no `.venv` exists in the current directory, check the parent directory for a `.venv`. If one exists there, activate it instead.
If no virtual environment is found in either location, follow the instructions under `.github/copilot-instructions.md` for "Install (developer)" to create and install one.
Ex: Call `./.venv/Scripts/Activate.ps1` (Windows) or `source ./.venv/bin/activate` (Linux/macOS) from the directory containing the virtual environment.

### Step 2: Write the test(s)
Read any code that the user references.
If the user does not specify a specific file to write the tests in, go in the tests folder, and find the most relevant test file.
If no other test file is relevant, consider creating a new file.
Tests that require a modeler session need to be added to the "integration" folder.
Leverage the pytest fixtures available for handling modeler sessions.
Write test code to test code in a detailed way. For example, if the code alters a face, test the before and after area of the face.
Document briefly what the test is doing through a docstring.
If the code to be tested has paths that raise errors, test those scenarios.

### Step 3: Run the test and verify results
Change directory into the pyansys-geometry directory.
Run the test by calling "pytest --use-existing-service=yes -k TEST_NAME", replacing TEST_NAME with the new test.
Assume the calling developer has a server running.
If the test fails, figure out why and iterate the source code or test code to fix it.
If the test fails and needs server-side changes, raise that to the user.

### Reducing line count
- **Inline sketch creation** using method chaining: `Sketch()` methods like `.box()`, `.circle()`, `.slot()` etc. all return `self`, so pass them directly: `design.extrude_sketch("Box", Sketch().box(Point2D([0, 0]), 1, 1), 1)` instead of assigning to an intermediate variable.
- **Eliminate single-use variables** when the value is only referenced once. If a value is used more than once, store it in a variable to avoid repeated property access.
- **Inline `len()` checks** rather than assigning the list to a variable just to call `len()` on it.

### Linting and line length
- The project enforces a **100-character maximum line length**. Every line must stay within this limit.
- When a line would exceed 100 characters, break it using Python's implicit line continuation inside parentheses:
  ```python
  # Too long:
  assert sum(mappable for _, mappable in results) == 6, "All 6 flat box faces should be mappable"
  # Fixed — drop the message or wrap:
  assert sum(mappable for _, mappable in results) == 6
  ```
- Drop inline assertion messages when they push the line over the limit; the asserted expression is usually self-documenting.
- After writing tests, run `pre-commit run --files <test_file>` or check line lengths manually to catch any violations before running pytest.

### Assertion quality
- **Never use `> 0` as a test condition.** Always assert exact expected values (e.g. `== 6`, `== 1`, `== 0`). If the exact value is not obvious from the geometry or logic, run the test once to observe the actual return value, then hard-code that exact value as the assertion.
- Prefer specific assertions over vague ones: `assert count == 6` is better than `assert count > 0`; `assert len(results) == 3` is better than `assert len(results) > 0`.
