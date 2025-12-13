from typing import List, Tuple, Dict
from .config import BLOCK_FREQ_BY_INDEX

def choose_freq_pattern(block: str, n_events: int) -> str:
    b = block.lower()
    if "pre" in b or "post" in b or "test" in b:
        return "Test"
    if b.startswith("b") and len(b) <= 3:
        return "Block_Training"
    return "Test" if n_events <= 55 else "Block_Training"

def compute_transitions(events: List[Tuple[float, int]]) -> List[Dict]:
    return [
        {
            "idx_from": i,
            "state_from": s1,
            "onset_from_s": t1,
            "idx_to": i + 1,
            "state_to": s2,
            "onset_to_s": t2,
            "transition_time_s": t2 - t1,
        }
        for i, ((t1, s1), (t2, s2)) in enumerate(zip(events, events[1:]))
    ]
