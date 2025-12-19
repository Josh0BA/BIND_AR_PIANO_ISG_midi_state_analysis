from typing import Dict, Set, Tuple

# ---------------------------------------------------------------------------
# 1. State-Definitionen (fixes Mapping deiner 9 Zustände)
# ---------------------------------------------------------------------------

STATE_DEFS: Dict[int, Set[int]] = {
    1: {65, 67, 72, 74, 77, 79},  # state1: F4, G4, C5, D5, F5, G5
    2: {60, 62, 64, 72, 77, 79},  # state2: C4, D4, E4, C5, F5, G5
    3: {60, 62, 64, 67, 72, 76},  # state3: C4, D4, E4, G4, C5, E5
    4: {60, 62, 64, 76, 77, 79},  # state4: C4, D4, E4, E5, F5, G5
    5: {62, 64, 65, 76, 77, 79},  # state5: D4, E4, F4, E5, F5, G5
    6: {64, 65, 72, 76, 77, 79},  # state6: E4, F4, C5, E5, F5, G5
    7: {60, 62, 72, 74, 76, 77},  # state7: C4, D4, C5, D5, E5, F5
    8: {64, 65, 72, 74, 77, 79},  # state8: E4, F4, C5, D5, F5, G5
    9: {62, 64, 65, 67, 72, 74},  # state9: D4, E4, F4, G4, C5, D5
}

COMBO_TO_STATE: Dict[frozenset, int] = {
    frozenset(notes): state for state, notes in STATE_DEFS.items()
}

# ---- Übergangsabfolgen für Test und Blöcke ----------------------
# Reihenfolge der Übergänge aus "Übergang Abfolge" Dokument
TEST_TRANSITION_SEQUENCE = [
    91, 13, 32, 24, 46, 65, 57, 79, 98, 81, 12, 23, 34, 45, 56, 67, 78, 89,
    91, 13, 32, 24, 46, 65, 57, 79, 98, 81, 12, 23, 34, 45, 56, 67, 78, 89,
    91, 13, 32, 24, 46, 65, 57, 79, 98, 81, 12, 23, 34, 45, 56, 67, 78, 89, 91
]

BLOCK_TRANSITION_SEQUENCE = [
    67, 78, 89, 91, 12, 23, 34, 45, 56, 67, 79, 91, 12, 23, 34, 45, 56, 65,
    56, 67, 78, 89, 91, 12, 24, 45, 56, 67, 78, 89, 91, 13, 34, 45, 56, 67, 78, 89, 98,
    89, 91, 12, 23, 34, 45, 57, 78, 89, 91, 12, 23, 34, 46, 67, 78, 89, 91, 12, 23, 32,
    23, 34, 45, 56, 67, 78, 81, 12, 23, 34, 45, 56, 67
]

# Häufigkeiten-Mapping für jeden Übergang
TRANSITION_FREQUENCIES: Dict[int, str] = {
    12: "h", 13: "s", 23: "h", 24: "s", 32: "s", 34: "h", 45: "h", 46: "s", 
    56: "h", 57: "s", 65: "s", 67: "h", 78: "h", 79: "s", 81: "s", 89: "h", 
    91: "h", 98: "s"
}


def map_transition_index_to_states(transition_key: int) -> Tuple[int, int]:
    """
    Mappt eine Übergangsnummer auf das Paar von States.
    
    Die Übergangsnummer wird wie folgt interpretiert:
    - 12 -> (1, 2)  # Von State 1 zu State 2
    - 23 -> (2, 3)  # Von State 2 zu State 3
    - 91 -> (9, 1)  # Von State 9 zu State 1
    
    Args:
        transition_key: Numerischer Key (z.B. 12, 23, 91)
    
    Returns:
        Tuple (from_state, to_state)
    
    Beispiel:
        >>> map_transition_index_to_states(12)
        (1, 2)
        >>> map_transition_index_to_states(91)
        (9, 1)
    """
    key_str = str(transition_key)
    
    if len(key_str) == 2:
        # Zweistellig: erste Ziffer = from_state, zweite = to_state
        from_state = int(key_str[0])
        to_state = int(key_str[1])
    elif len(key_str) == 3:
        # Dreistellig: erste Ziffer = from_state, Rest = to_state
        from_state = int(key_str[0])
        to_state = int(key_str[1:])
    else:
        raise ValueError(f"Ungültiger Übergangscode: {transition_key}")
    
    return (from_state, to_state)


def get_transition_sequence(block_type: str) -> list:
    """
    Gibt die Übergangssequenz für einen bestimmten Block-Typ zurück.
    
    Args:
        block_type: "Test" für Pre-/Post-Test oder "Block" für Trainingsblöcke
    
    Returns:
        Liste der Übergangscodes in der richtigen Reihenfolge
    
    Beispiel:
        >>> seq = get_transition_sequence("Test")
        >>> seq[0]  # Erster Übergang im Test
        91
        >>> seq = get_transition_sequence("Block")
        >>> seq[0]  # Erster Übergang im Block
        67
    """
    block_lower = block_type.lower()
    
    if "test" in block_lower or "pre" in block_lower or "post" in block_lower:
        return TEST_TRANSITION_SEQUENCE
    elif "block" in block_lower or "b" == block_lower[0]:
        return BLOCK_TRANSITION_SEQUENCE
    else:
        # Default: Test-Sequenz
        return TEST_TRANSITION_SEQUENCE


def get_expected_transition_at_index(index: int, block_type: str) -> Tuple[int, str]:
    """
    Gibt den erwarteten Übergang und seine Häufigkeit für einen Index zurück.
    
    Args:
        index: Position in der Sequenz (0-basiert)
        block_type: "Test" oder "Block"
    
    Returns:
        Tuple (transition_key, frequency)
        z.B. (91, "h") für hohe Frequenz oder (13, "s") für seltene Frequenz
    
    Beispiel:
        >>> get_expected_transition_at_index(0, "Test")
        (91, 'h')
        >>> get_expected_transition_at_index(1, "Test")
        (13, 's')
    """
    sequence = get_transition_sequence(block_type)
    
    if index >= len(sequence):
        raise IndexError(f"Index {index} außerhalb der Sequenz (max: {len(sequence)-1})")
    
    transition_key = sequence[index]
    frequency = TRANSITION_FREQUENCIES.get(transition_key, "UNKNOWN")
    
    return (transition_key, frequency)
