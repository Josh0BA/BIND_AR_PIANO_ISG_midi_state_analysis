import argparse, os
from .folder_utils import find_midi_data_folder
from .analyzer import analyze_root_folder

def main():
    parser = argparse.ArgumentParser(description="Analyse von Klavier-MIDI-State-Übergängen.")
    parser.add_argument("start_path", nargs="?", default=".")
    parser.add_argument("-o", "--output", help="Output-CSV-Datei")
    args = parser.parse_args()
    midi_root = find_midi_data_folder(args.start_path)
    if not midi_root:
        fallback = r"C:\Users\joshb\Desktop\CODE\BIND_AR_PIANO_ISG_midi_state_analysis\Daten (MIDI)"
        if os.path.isdir(fallback):
            midi_root = fallback
            print(f"✓ Verwende Fallback-Ordner: {midi_root}")
        else:
            print("✗ 'Daten (MIDI)' nicht gefunden und Fallback-Pfad existiert nicht.")
            return
    output = args.output or os.path.join(os.path.dirname(midi_root), "MIDI_ANALYSIS_STATES.csv")
    analyze_root_folder(midi_root, output)
    print("✓ Analyse abgeschlossen:", output)
