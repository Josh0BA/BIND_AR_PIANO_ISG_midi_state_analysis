# BIND_AR_PIANO_ISG_midi_state_analysis
Analyse von MIDI-Dateien für das Motorik-lernen am Klavier mit AR. 

Anleitung:																													
-Installation
Lade das Projekt herunter oder klone das Repository. Installiere das Paket anschließend mit:
pip install .

-Daten vorbereiten
Erstelle einen Ordner mit dem Namen „Daten (MIDI)“. Lege darin Unterordner für jede Versuchsperson an, und speichere die jeweiligen MIDI-Dateien dort ab. Beispiel:
Daten (MIDI)/BE16MI/MIDI_BE16MI_B1.mid

-Analyse starten
Öffne ein Terminal und führe das Programm aus:
-> midi-analysis .
Das Programm sucht automatisch nach dem Ordner „Daten (MIDI)“.
Optional kannst du einen eigenen Output-Dateinamen angeben:
midi-analysis . -o output.csv

-Ergebnis
Die Analyse erzeugt eine CSV-Datei (z. B. MIDI_ANALYSIS_STATES.csv).
Diese enthält pro Übergang: subject, block, state_from, state_to, onset-Zeiten, transition_time und die zugehörige Häufigkeit (h oder s).

**Hinweis:** Eine detaillierte Erklärung der CSV-Spalten und warum Lücken in der idx_from-Sequenz auftreten, findest du in [CSV_ERKLAERUNG.md](CSV_ERKLAERUNG.md).

Funktionen:
- Erkennt 9 Zustände (state0–state8) anhand fixer 6er-Kombinationen von Pitches
- Berechnet Transitionen zwischen Zuständen mit Zeiten in Sekunden
- Ordnet Häufigkeiten (h/s) aus BLOCK_FREQ_BY_INDEX den Transitionen zu
- Automatische Pattern-Erkennung: Block_Training (B1-B8, 72 States) vs Test (Pre/Post, 54 States)
- Sucht automatisch nach "Daten (MIDI)" Ordner (aktuell/übergeordnet/rekursiv)
- Extrahiert Subject-ID aus Ordnername und Block aus Dateiname
- Schreibt alle Transitionen in CSV: subject, block, state_from/to, times, frequencies

Struktur: BIND_AR_PIANO_ISG_midi_state_analysis/                                                                        
│                                                                    
├── midi_state_analysis/                                                                                            
│       ├── __init__.py                                                                                
│       ├── config.py                                                                
│       ├── midi_utils.py                                            
│       ├── state_detection.py                                        
│       ├── transitions.py                                    
│       ├── folder_utils.py                                            
│       ├── analyzer.py                                            
│       └── cli.py                                                
│                                                        
└── setup.py                                            

Performance-Optimierungen:												
- Effizientes Track-Merging und State-Erkennung
- zip+comprehension für schnelle Transition-Berechnung
- Kompakte Frequenzzuordnung ohne redundante Schleifen

Voraussetzungen:																							
    pip install mido
