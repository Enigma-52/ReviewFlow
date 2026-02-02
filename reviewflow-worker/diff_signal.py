from typing import List, Dict
from diff_normalizer import FileDiff


def compute_risk_signals(
    file_diffs: List[FileDiff], symbols_map: Dict[str, List[Dict]]
) -> Dict:
    """
    Basic heuristics to flag risky changes.
    """
    high_risk_files = []
    breaking_candidates = []
    tests_missing = False

    for fd in file_diffs:
        # Large change heuristic
        total_added = sum(len(h.added) for h in fd.hunks)
        total_removed = sum(len(h.removed) for h in fd.hunks)

        if total_added + total_removed > 100:
            high_risk_files.append(fd.path)

        # Signature change heuristic (simplified placeholder)
        if fd.path.endswith(".py"):
            for sym in symbols_map.get(fd.path, []):
                if total_removed > 0:
                    breaking_candidates.append(sym["name"])

        # Test coverage heuristic
        if not any("test" in f.path.lower() for f in file_diffs):
            tests_missing = True

    return {
        "high_risk_files": high_risk_files,
        "breaking_change_candidates": breaking_candidates,
        "tests_missing_for_changes": tests_missing,
    }
