---
name: writing-tests
description: This skill is used for writing tests to aid developers in ensuring code works properly. Use when a user mentions "writing tests", "adding code coverage", "testing new feature", asks to "write unit tests", or says "write a unit test for" something specific.
---

# Writing Tests

## Instructions

### Step 1: Activate virtual environment
Activate the virtual environment available to the workspace.
Ex: Call "./.venv/Scripts/activate" in the directory containing the virtual environment

### Step 2: Write the test(s)
Read any code that the user references.
If the user does not specify a specific file to write the tests in, go in the tests folder, and find the most relevant test file.
Write test code to test code in a detailed way. For example, if the code alters a face, test the before and after area of the face.
If the code to be tested has paths that raise errors, test those scenarios.

### Step 3: Run the test and verify results
Change directory into the pyansys-geometry directory.
Run the test by calling "pytest --use-existing-service=yes -k TEST_NAME", replacing TEST_NAME with the new test.
Assume the calling developer has a server running.
If the test fails, figure out why and iterate the source code or test code to fix it.
If the test fails and needs server-side changes, raise that to the user.