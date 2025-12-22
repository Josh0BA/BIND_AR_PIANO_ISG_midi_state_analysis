from typing import List, Tuple, Dict
import pandas as pd

def choose_freq_pattern(block: str, n_events: int) -> str:
    b = block.lower()
    if "pre" in b or "post" in b or "test" in b:
        return "Test"
    if b.startswith("b") and len(b) <= 3:
        return "Block_Training"
    return "Test" if n_events <= 55 else "Block_Training"

def compute_transition_id(state_from: int, state_to: int) -> int:
    """
    Berechnet die Übergangsnummer aus zwei States.
    
    Beispiele:
        State 1 → State 2 = 12
        State 9 → State 1 = 91
        State 2 → State 3 = 23
    
    Args:
        state_from: Start-State (1-9)
        state_to: Ziel-State (1-9)
    
    Returns:
        int: Übergangscode als zweistellige Zahl
    """
    return int(f"{state_from}{state_to}")

def compute_transitions(events: pd.DataFrame) -> pd.DataFrame:
    """
    Berechnet alle Übergänge zwischen aufeinanderfolgenden States.
    
    Hinweis: idx_from und idx_to geben die Position des States in der MIDI-Datei an.
    Nach der Filterung in analyzer.py können Lücken in der idx_from-Sequenz auftreten,
    wenn ungültige Übergänge aussortiert werden.
    """
    if events.empty:
        return pd.DataFrame()
    transitions = []
    for i in range(len(events) - 1):
        t1, s1 = events.iloc[i]["time_s"], events.iloc[i]["state"]
        t2, s2 = events.iloc[i + 1]["time_s"], events.iloc[i + 1]["state"]
        transition_id = compute_transition_id(s1, s2)
        transitions.append({
            "idx_from": i,  # Position des Start-States in der MIDI-Datei
            "state_from": s1,
            "onset_from_s": t1,
            "idx_to": i + 1,  # Position des Ziel-States in der MIDI-Datei
            "state_to": s2,
            "onset_to_s": t2,
            "transition_time_s": t2 - t1,
            "transition_id": transition_id,
        })
    return pd.DataFrame(transitions)
