import os
import re

def find_midi_data_folder(start_path="."):
    current = os.path.abspath(start_path)
    while True:
        candidate = os.path.join(current, "Daten (MIDI)")
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    for root, dirs, _ in os.walk(start_path):
        if "Daten (MIDI)" in dirs:
            return os.path.join(root, "Daten (MIDI)")
    return None

def parse_subject_and_block(dirpath, filename):
    subject = os.path.basename(dirpath)
    name, _ = os.path.splitext(filename)
    if name.startswith("MIDI_") and "_" in name[5:]:
        return subject, name.split("_", 1)[1]
    return subject, name

def normalize_block_name(block: str) -> str:
    """
    Normalisiert Block-Namen zu standardisierten Formen: B1-B8, Pretest, Posttest.
    
    Konvertiert alles mit B1-B8 im Namen → B1-B8
    Konvertiert alles mit Pretest im Namen → Pretest
    Konvertiert alles mit Posttest im Namen → Posttest
    
    Beispiele:
    - "Block_1", "B1" → "B1"
    - "Pretest", "Pre" → "Pretest"
    - "Posttest", "Post" → "Posttest"
    
    Args:
        block: Original-Block-Name
    
    Returns:
        str: Normalisierter Block-Name (B1-B8, Pretest, oder Posttest)
    """
    block_lower = block.lower().strip()
    
    # Erkenne alle Varianten von B1-B8
    # Block_1, Block_2, ..., B1, B2
    block_match = re.search(r"b([1-8])|block[_\s]*([1-8])", block_lower)
    if block_match:
        block_num = block_match.group(1) or block_match.group(2)
        return f"B{block_num}"
    
    # Erkenne alle Varianten von Pretest
    # Pretest, Pre
    if re.search(r"pretest|^pre", block_lower):
        return "Pretest"
    
    # Erkenne alle Varianten von Posttest
    # Posttest, Post
    if re.search(r"posttest|^post", block_lower):
        return "Posttest"
    
    # Fallback: versuche nach einzelner Ziffer zu suchen
    digit_match = re.search(r"[1-8]", block_lower)
    if digit_match:
        digit = digit_match.group(0)
        return f"B{digit}"
    
    # Letzter Fallback: Original zurückgeben
    return block
