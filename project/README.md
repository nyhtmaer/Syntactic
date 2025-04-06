# Python Syntax Sugaring Tool

A web-based tool that analyzes Python code and suggests more concise, "sugared" versions by applying syntactic sugar transformations.

## Architecture Overview

```
User Input (Python Code)
       ↓
 [Frontend (JS/CSS)]
       ↓
 [Flask Backend]
       ↓
[AST Parser → CrewAI Agent Orchestration]
       ↓
Parser Agent → Sugaring Agent → Validation Agent
       ↓
[Sugared Code + Explanation]
       ↓
Frontend Display
```

## Technologies Used

- **Frontend**: HTML/CSS/JavaScript with CodeMirror editor
- **Backend**: Python + Flask
- **LLM API**: Claude 3.7 Sonnet (via Anthropic API)
- **AST Parsing**: Python's built-in `ast` module
- **Agent Framework**: CrewAI
- **Hosting**: Local server

## Features

- Accept Python code input via web interface
- Parse and analyze using AST
- Detect verbose constructs that can be rewritten with syntactic sugar
- Replace verbose code with equivalent sugared form
- Preserve and make code comments concise in the transformed code
- Provide natural-language explanations (via Claude)
- Show side-by-side diff of changes
- Validate correctness of transformed code

## Supported Transformations

- For loop with append → List comprehension
- For loop with set.add → Set comprehension
- For loop with dict assignment → Dict comprehension
- Manual counter with index access → enumerate()
- Index-based parallel loops → zip()
- Tuple index assignments → Tuple unpacking
- If/Else assignment → Ternary operator
- Assign then use in if → Walrus operator
- Try/finally with close() → with statement
- One-off def used inline → lambda
- And more...

## Setup and Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Add your Anthropic API key to the `sugaring_agent.py` file
4. Run the application:
   ```
   python app.py
   ```
5. Open your browser to `http://localhost:5000`

## Project Structure

```
project/
├── app.py                  # Flask entrypoint
├── agents/
│   ├── parser_agent.py
│   ├── sugaring_agent.py
│   ├── validation_agent.py
├── rules/
│   └── sugaring_rules.py   # Contains rulebook
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
```

## Future Improvements

- Add more sugar rules
- Allow users to choose which rules to apply
- Improve AST parsing accuracy
- Add user accounts to save code snippets
- Add ability to share transformations
- Auto-generate test inputs to validate code
- Enhance comment preservation for inline comments 