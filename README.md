# gai-ag (Gemini Autonomous Agent)

`gai-ag` is a professional, fast, and intelligent command-line tool that brings the Google Gemini API to your terminal. It features an advanced "Agent" mode that can both answer questions directly and perform automatic modifications on your project.

- **Autonomous Agent Mode**: Automatically fixes errors, runs tests, and generates solutions.
- **Project Brain**: Creates a `.gai/` folder in each project to store history, state, and errors.
- **Smart Scanning**: Caches project structure and prioritizes critical files to save tokens.
- **Polyglot Support**: Automatically detects Flutter, Node.js, and Python projects.

## ✨ Features

- 🤖 **Agent Mode**: Analyzes files in your project, plans requested changes (code writing, file creation, deletion, moving), and applies them with your approval.
- 💬 **Interactive Chat**: Communicate fluently with Gemini through a multi-modal chat interface.
- 📁 **Context Injection (@)**: Add files as context to your chat using `@file.py` or `@src/`.
- 🎨 **Premium UI**: Stylish and readable output powered by the `rich` library.
- 🌍 **Multi-language Support**: English and Turkish language options.
- 🔒 **Secure Operations**: File system operations are restricted to the project directory.

## 🚀 Installation

### From PyPI (Easiest)
```bash
pip install gai-ag
```

### For Development
1. Clone the repository:
   ```bash
   git clone https://github.com/bugraakdemir/gai-cli.git
   cd gai-cli
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

## 🛠️ Usage

> **Note**: Both `gai` and `gai-ag` commands work in the terminal!

### One-time Question
```bash
gai "What are list comprehensions in Python?"
# or
gai-ag "What are list comprehensions in Python?"
```

### Interactive Mode (Chat & Agent)
Start the interactive mode by simply typing `gai` or `gai-ag`:
```bash
gai
# or
gai-ag
```
