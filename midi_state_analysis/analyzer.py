import os, mido
import pandas as pd
from .folder_utils import parse_subject_and_block, normalize_block_name
from .state_detection import detect_states_in_midi
from .transitions import compute_transitions, choose_freq_pattern, compute_transition_id
from .config import get_transition_sequence, TRANSITION_FREQUENCIES

def analyze_root_folder(root_folder: str, output_csv: str):
    all_dfs = []
    for dirpath, _, files in os.walk(root_folder):
        midi_files = [f for f in files if f.lower().endswith((".mid", ".midi"))]
        if not midi_files:
            continue
        for filename in sorted(midi_files):
            full = os.path.join(dirpath, filename)
            try:
                subject, block = parse_subject_and_block(dirpath, filename)
                block = normalize_block_name(block)  # Normalisiere Block-Namen
                events = detect_states_in_midi(mido.MidiFile(full))
                transitions = compute_transitions(events)
                if transitions.empty:
                    continue
                
                # Bestimme Block-Typ und erwartete Übergangssequenz
                pattern = choose_freq_pattern(block, len(events))
                block_type = 'Test' if pattern == 'Test' else 'Block'
                sequence = get_transition_sequence(block_type)
                valid_transitions = set(sequence)
                
                # Filtere nur Übergänge, die in der erwarteten Sequenz vorkommen
                transitions_filtered = transitions[transitions['transition_id'].isin(valid_transitions)].copy()
                
                if transitions_filtered.empty:
                    continue
                
                # Weise Häufigkeiten basierend auf Übergangscode zu
                transitions_filtered["state_from_freq"] = transitions_filtered["transition_id"].apply(
                    lambda tid: TRANSITION_FREQUENCIES.get(tid, "UNKNOWN")
                )
                
                # Füge subject und block hinzu
                transitions_filtered["subject"] = subject
                transitions_filtered["block"] = block
                
                all_dfs.append(transitions_filtered)
            except Exception as e:
                print(f"⚠ Fehler beim Verarbeiten von {filename}: {e}")
                continue
    
    if not all_dfs:
        print("Keine Daten gefunden.")
        return
    
    df = pd.concat(all_dfs, ignore_index=True)
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
