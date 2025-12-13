import os

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
