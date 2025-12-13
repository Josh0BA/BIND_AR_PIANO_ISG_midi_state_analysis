import os, csv, mido
from .folder_utils import parse_subject_and_block
from .state_detection import detect_states_in_midi
from .transitions import compute_transitions, choose_freq_pattern
from .config import BLOCK_FREQ_BY_INDEX

def analyze_root_folder(root_folder: str, output_csv: str):
    all_rows = []
    for dirpath, _, files in os.walk(root_folder):
        midi_files = [f for f in files if f.lower().endswith((".mid", ".midi"))]
        if not midi_files:
            continue
        for filename in sorted(midi_files):
            full = os.path.join(dirpath, filename)
            subject, block = parse_subject_and_block(dirpath, filename)
            events = detect_states_in_midi(mido.MidiFile(full))
            transitions = compute_transitions(events)
            pattern = choose_freq_pattern(block, len(events))
            freqs = list(BLOCK_FREQ_BY_INDEX.get(pattern, {}).values())
            for i, tr in enumerate(transitions):
                row = tr.copy()
                row.update({
                    "subject": subject,
                    "block": block,
                    "state_from_freq": freqs[i] if i < len(freqs) else "UNKNOWN",
                })
                all_rows.append(row)
    if not all_rows:
        print("Keine Daten gefunden.")
        return
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)
