import os, mido
import pandas as pd
from .folder_utils import parse_subject_and_block
from .state_detection import detect_states_in_midi
from .transitions import compute_transitions, choose_freq_pattern
from .config import BLOCK_FREQ_BY_INDEX

def analyze_root_folder(root_folder: str, output_csv: str):
    all_dfs = []
    for dirpath, _, files in os.walk(root_folder):
        midi_files = [f for f in files if f.lower().endswith((".mid", ".midi"))]
        if not midi_files:
            continue
        for filename in sorted(midi_files):
            full = os.path.join(dirpath, filename)
            subject, block = parse_subject_and_block(dirpath, filename)
            events = detect_states_in_midi(mido.MidiFile(full))
            transitions = compute_transitions(events)
            if transitions.empty:
                continue
            pattern = choose_freq_pattern(block, len(events))
            freqs = list(BLOCK_FREQ_BY_INDEX.get(pattern, {}).values())
            transitions["subject"] = subject
            transitions["block"] = block
            transitions["state_from_freq"] = [freqs[i] if i < len(freqs) else "UNKNOWN" for i in range(len(transitions))]
            all_dfs.append(transitions)
    if not all_dfs:
        print("Keine Daten gefunden.")
        return
    df = pd.concat(all_dfs, ignore_index=True)
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
