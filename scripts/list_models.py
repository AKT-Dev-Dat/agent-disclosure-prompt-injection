"""List the Claude model IDs that the API key in .env can use.

Usage (from the project folder):
    C:\\venvs\\adpi\\Scripts\\python.exe scripts\\list_models.py

Safety: the key is read from .env and is NEVER printed. Only model names are shown.
"""
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        sys.exit("No key found: .env has nothing after 'ANTHROPIC_API_KEY='.")

    try:
        page = anthropic.Anthropic().models.list(limit=1000)
    except anthropic.AuthenticationError:
        sys.exit("Anthropic rejected the key (authentication error).")

    ids = sorted(m.id for m in page.data)
    print(f"Key works. {len(ids)} models available:")
    for model_id in ids:
        print(" ", model_id)


if __name__ == "__main__":
    main()
