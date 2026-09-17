import time
from typing import List, Dict, Any, Optional
from collections import Counter

class HistoryManager:
    """
    Manages action stack for undo/revert functionality (Ctrl+Z / Backspace)
    and collects session statistics.
    """
    def __init__(self):
        self._stack: List[Dict[str, Any]] = []

    def record_action(self, source_path: str, target_path: Optional[str], 
                      action_type: str, image_index: int, 
                      target_subfolder: str = ""):
        """Pushes an action onto the history stack."""
        record = {
            "source_path": source_path,
            "target_path": target_path,
            "action_type": action_type, # 'move', 'copy', or 'skip'
            "image_index": image_index,
            "target_subfolder": target_subfolder,
            "timestamp": time.time()
        }
        self._stack.append(record)

    def can_undo(self) -> bool:
        """Returns True if there is at least one action to undo."""
        return len(self._stack) > 0

    def pop_last_action(self) -> Optional[Dict[str, Any]]:
        """Pops and returns the most recent action record."""
        if self._stack:
            return self._stack.pop()
        return None

    def peek_last_action(self) -> Optional[Dict[str, Any]]:
        """Views the most recent action record without removing it."""
        if self._stack:
            return self._stack[-1]
        return None

    def get_history_count(self) -> int:
        return len(self._stack)

    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Calculates summary statistics: total actions, counts per subfolder,
        and count of skipped items.
        """
        counts = Counter()
        skipped = 0
        total = len(self._stack)

        for record in self._stack:
            if record["action_type"] == "skip":
                skipped += 1
            else:
                folder = record.get("target_subfolder") or "Other"
                counts[folder] += 1

        return {
            "total_processed": total,
            "skipped": skipped,
            "by_subfolder": dict(counts)
        }

    def clear(self):
        self._stack.clear()
