# In worker.py (or a new file like phase_a.py)

from diff_normalizer import normalize_diff
from diff_analyzer import extract_symbols
from diff_signal import compute_risk_signals


def run_phase_a(diff: str, fetch_file_fn):
    """
    fetch_file_fn(path: str) -> str  # returns full file content
    """

    # -------- A.1: Normalize diff --------
    file_diffs = normalize_diff(diff)

    # -------- A.2: Extract symbols --------
    symbols_map = {}

    for fd in file_diffs:
        try:
            # Fetch latest file content from GitHub (head SHA)
            content = fetch_file_fn(fd.path)
            symbols = extract_symbols(fd.path, content)
        except Exception as e:
            # If file was deleted or fetch fails, store empty list
            symbols = []

        symbols_map[fd.path] = symbols

    # -------- A.3: Compute risk signals --------
    risk_summary = compute_risk_signals(file_diffs, symbols_map)

    return {
        "file_diffs": file_diffs,
        "symbols_map": symbols_map,
        "risk_summary": risk_summary,
    }
