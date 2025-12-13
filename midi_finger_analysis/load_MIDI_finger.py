import os
import pretty_midi
import pandas as pd
import numpy as np

# Change this to your actual folder path
root_folder = r'C:\Users\tobia\OneDrive - Universitaet Bern\25FS_BSc_AubertTobias_ARPiano\12_Rohdaten'
data = []

# Walk through all subfolders
for dirpath, dirnames, filenames in os.walk(root_folder):
    for filename in filenames:
        if filename.lower().endswith(('.mid', '.midi')) and 'finger' in filename.lower():
            file_path = os.path.join(dirpath, filename)

            try:
                # Extract participant ID, appointment, song, and attempt from filename
                participant_id = filename.split('_')[0]
                appointment = filename.split('_')[1]
                song = filename.split('_')[2]
                attempt = filename.split('_')[3].split('.')[0]  # Remove file extension

                # Extract note keystrokes

                # Load MIDI file
                midi = pretty_midi.PrettyMIDI(file_path)

                # Remove notes that start after 30 seconds
                for instrument in midi.instruments:
                    instrument.notes = [note for note in instrument.notes if note.start <= 30.0]

                # Your expected pattern (adjust to match what they were supposed to play)
                expected_sequence = ['F4', 'C4', 'E4', 'D4', 'F4']
                sequence_len = len(expected_sequence)

                # Extract played notes (non-drum, sorted by start time)
                played_notes = []
                for instrument in midi.instruments:
                    if not instrument.is_drum:
                        sorted_notes = sorted(instrument.notes, key=lambda n: n.start)
                        for note in sorted_notes:
                            name = pretty_midi.note_number_to_name(note.pitch)
                            played_notes.append(name)

                        if (participant_id == "JE13CL"):
                            print(f"Played notes for {participant_id}: {played_notes}")

                # Count correct sequences using a sliding window
                correct_sequences = 0
                for i in range(len(played_notes) - sequence_len + 1):
                    if played_notes[i:i+sequence_len] == expected_sequence:
                        correct_sequences += 1


                # prepare the data for DataFrame
                info = {
                    'Participant_ID': participant_id,
                    'Appointment': appointment,
                    'Song': song,
                    'Attempt': attempt,
                    'Keystrokes': len(played_notes),
                    'Correct_Sequences': correct_sequences,
                }

                data.append(info)

                print(f"✅ Loaded: {file_path}")
            except Exception as e:
                print(f"❌ Failed to load {file_path}: {e}")


df_finger = pd.DataFrame(data)

pd.set_option('display.max_rows', None)      # Show all rows
pd.set_option('display.max_columns', None)   # Show all columns
pd.set_option('display.width', None)         # No limit on display width
pd.set_option('display.max_colwidth', None)  # Don't truncate column contents

# Create label column for wide format
df_finger['label'] = df_finger['Song'] + '_'  + df_finger['Appointment'].astype(str) + '-' +  df_finger['Attempt'].astype(str)

# Pivot to get one row per participant
df_correct = df_finger.pivot(index='Participant_ID', columns='label', values='Correct_Sequences')
df_keys = df_finger.pivot(index='Participant_ID', columns='label', values='Keystrokes')
df_ratio = df_correct * 5 / df_keys

# rename columns for clarity
df_correct.columns = [f"{col}_correct" for col in df_correct.columns]
df_keys.columns = [f"{col}_keys" for col in df_keys.columns]
df_ratio.columns = [f"{col}_ratio" for col in df_ratio.columns]


#combine the dataframes
df_combined = pd.concat([df_correct, df_keys, df_ratio], axis=1)
df_combined.reset_index(inplace=True)


df_combined.to_csv("C:/Users/tobia/Desktop/Recording-comparison/src/Examples_tests/Data/fingergeschicklichkeit.csv", index=False)

# print(df_finger)
print(df_combined)