import re
from typing import List, Dict, Literal

ChangeType = Literal["added", "modified", "deleted", "renamed"]


class FileHunk:
    def __init__(self, start_line: int, added: List[str], removed: List[str]):
        self.start_line = start_line
        self.added = added
        self.removed = removed


class FileDiff:
    def __init__(self, path: str, change_type: ChangeType, hunks: List[FileHunk]):
        self.path = path
        self.change_type = change_type
        self.hunks = hunks


def normalize_diff(unified_diff: str) -> List[FileDiff]:
    """
    Convert raw GitHub unified diff into a structured representation.
    """
    files: List[FileDiff] = []
    current_file = None
    hunks: List[FileHunk] = []

    for line in unified_diff.splitlines():
        # New file header
        if line.startswith("diff --git"):
            if current_file:
                files.append(FileDiff(current_file, change_type, hunks))
                hunks = []
            continue

        if line.startswith("+++ b/"):
            current_file = line[6:]
            change_type = "modified"
            continue

        if line.startswith("@@"):
            # Extract starting line number
            m = re.search(r"\+(\d+)", line)
            start_line = int(m.group(1)) if m else 0
            hunks.append(FileHunk(start_line, [], []))
            continue

        if hunks:
            if line.startswith("+") and not line.startswith("+++"):
                hunks[-1].added.append(line[1:])
            elif line.startswith("-") and not line.startswith("---"):
                hunks[-1].removed.append(line[1:])

    if current_file:
        files.append(FileDiff(current_file, change_type, hunks))

    return files
