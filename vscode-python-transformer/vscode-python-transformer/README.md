# Python Code Transformer Extension for VS Code

This VS Code extension transforms Python code between concise and verbose forms. It connects to a Python backend service that performs AST-based code transformations.

## Features

- **Sugarize Code**: Transform Python code into more concise forms using language features like list comprehensions, ternary operators, etc.
- **Desugarize Code**: Expand and add comments to Python code to make it more explicit and easier to understand.

## Requirements

- Visual Studio Code 1.60.0 or higher
- Node.js and npm installed
- Python 3.6+ (for the backend service)

## Installation

### 1. Installing the Extension

Clone this repository and install dependencies:

```bash
git clone https://github.com/yourusername/vscode-python-transformer.git
cd vscode-python-transformer
npm install
npm run compile
```

Then open VS Code in the extension directory and press F5 to launch a new VS Code window with the extension loaded.

### 2. Setting up the Python Backend Service

The extension requires a Python backend service to handle the code transformations:

1. Navigate to the Python project directory:
   ```bash
   cd /path/to/python/project
   ```

2. Install the required dependencies:
   ```bash
   pip install flask astunparse pydantic requests
   ```

3. Run the service:
   ```bash
   python app.py
   ```

The service should be running at http://localhost:5000.

## Usage

1. Open a Python file in VS Code
2. Select code (or the entire file will be used if nothing is selected)
3. Right-click and select either:
   - "Python: Sugarize Code (Make Concise)" - to transform code into a more concise form
   - "Python: Desugarize Code (Expand & Add Comments)" - to expand code and add explanatory comments

Alternatively, you can use the Command Palette (Ctrl+Shift+P or Cmd+Shift+P) and search for "Python: Sugarize Code" or "Python: Desugarize Code".

## Development

### Extension Structure

- `src/extension.ts`: The main extension code
- `package.json`: Extension manifest
- `tsconfig.json`: TypeScript configuration

### Building the Extension

```bash
npm run compile
```

### Packaging the Extension

```bash
npm install -g vsce
vsce package
```

This will create a `.vsix` file that can be installed in VS Code.

## License

MIT 