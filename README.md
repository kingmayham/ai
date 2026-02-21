# Smart AI Coding Assistant

A lightweight Python coding assistant that helps you:

- Understand coding tasks from plain language.
- Scan a repository for relevant files.
- Generate a practical implementation plan.
- Suggest safe shell commands for execution.
- Produce actionable "next response" text suitable for chat-based coding workflows.
- Generate **real code edits** (patch preview or direct apply).

## Quick start

```bash
python cli.py --task "add function parse_config to parser"
```

Apply generated edits:

```bash
python cli.py --task "add function parse_config to parser" --apply
```

Use explicit target files:

```bash
python cli.py --task "add function format_price" --files app.py utils/money.py
```

## What coding support it provides

Current coding capability is intentionally conservative:

- Detects intent from your prompt.
- Chooses relevant files based on task tokens.
- For tasks requesting an added Python function, it can generate a function stub in a relevant `.py` file.
- Can apply edits with `--apply` or show a patch preview in the response draft.

## Run tests

```bash
python -m unittest discover -s tests -p 'test_*.py'
```


## GUI

Run a local web GUI:

```bash
python gui_server.py
```

Then open `http://localhost:8000`.
