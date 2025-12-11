# BIND_AR_PIANO_ISG_midi_state_analysis
Analyse von MIDI-Dateien für das Motorik-lernen am Klavier mit AR. 

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
│   ├── __init__.py                                                                                
│   ├── config.py                                                                
│   ├── midi_utils.py                                            
│   ├── state_detection.py                                        
│   ├── transitions.py                                    
│   ├── folder_utils.py                                            
│   ├── analyzer.py                                            
│   └── cli.py                                                
│                                                        
└── setup.py                                            

Performance-Optimierungen:
- Effizientes Track-Merging und State-Erkennung
- zip+comprehension für schnelle Transition-Berechnung
- Kompakte Frequenzzuordnung ohne redundante Schleifen

Voraussetzungen:
    pip install mido
