import re
from typing import List, Dict


def extract_symbols(file_path: str, file_content: str) -> List[Dict]:
    """
    Lightweight, pure-Python fallback symbol extractor.
    Good enough for Phase A right now.
    """

    symbols = []

    # --- Python function detection ---
    if file_path.endswith(".py"):
        for match in re.finditer(
            r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)", file_content, re.MULTILINE
        ):
            symbols.append(
                {
                    "name": match.group(1),
                    "type": "function",
                    "start_line": file_content[: match.start()].count("\n") + 1,
                }
            )

        for match in re.finditer(
            r"^class\s+([a-zA-Z_][a-zA-Z0-9_]*)", file_content, re.MULTILINE
        ):
            symbols.append(
                {
                    "name": match.group(1),
                    "type": "class",
                    "start_line": file_content[: match.start()].count("\n") + 1,
                }
            )

    # --- Basic TypeScript / JS support (optional) ---
    if file_path.endswith(".ts") or file_path.endswith(".js"):
        for match in re.finditer(r"function\s+([a-zA-Z_][a-zA-Z0-9_]*)", file_content):
            symbols.append(
                {
                    "name": match.group(1),
                    "type": "function",
                    "start_line": file_content[: match.start()].count("\n") + 1,
                }
            )

    return symbols
