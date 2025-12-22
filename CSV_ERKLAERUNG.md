# Erklärung der CSV-Ausgabe

## Was gibt die erste Spalte aus?

Die **erste Spalte `idx_from`** gibt den **Index der Position** des Ausgangszustands (Start-State) in der MIDI-Datei an.

### Beispiel:
```
idx_from,state_from,onset_from_s,idx_to,state_to,onset_to_s,transition_time_s,transition_id,state_from_freq,subject,block
0,6,6.900625,1,7,8.73,1.8293750000000006,67,h,BE13RE,B1
1,7,8.73,2,8,11.046875,2.3168749999999996,78,h,BE13RE,B1
2,8,11.046875,3,9,12.67,1.623125,89,h,BE13RE,B1
```

- **Zeile 1**: `idx_from=0` bedeutet, dass dies der Übergang vom 0. State (Position 0) ist
- **Zeile 2**: `idx_from=1` bedeutet, dass dies der Übergang vom 1. State (Position 1) ist
- **Zeile 3**: `idx_from=2` bedeutet, dass dies der Übergang vom 2. State (Position 2) ist

Die Spalte `idx_to` zeigt entsprechend den Index des Ziel-States.

## Wieso gibt es Unterbrechungen in der Sequenz?

Die **Unterbrechungen (Lücken) in der `idx_from`-Sequenz** entstehen, weil **nur gültige Übergänge** in der CSV-Datei gespeichert werden.

### Erklärung:

1. **Das Programm erkennt alle States** in der MIDI-Datei (z.B. Position 0, 1, 2, 3, 4, ...)

2. **Es berechnet alle möglichen Übergänge** zwischen aufeinanderfolgenden States

3. **Es filtert die Übergänge**: Nur Übergänge, die zur erwarteten Sequenz gehören, werden gespeichert
   - Für **Trainingsblöcke (B1-B8)**: 72 erwartete Übergänge (siehe `BLOCK_TRANSITION_SEQUENCE` in `config.py`)
   - Für **Tests (Pretest/Posttest)**: 54 erwartete Übergänge (siehe `TEST_TRANSITION_SEQUENCE` in `config.py`)

4. **Wenn ein Übergang nicht in der erwarteten Sequenz liegt**, wird er **herausgefiltert**
   - Dies geschieht z.B. wenn:
     - Der Teilnehmer einen Fehler macht
     - Der Teilnehmer einen unerwarteten State spielt
     - Der Teilnehmer die Sequenz wiederholt oder überspringt

### Beispiel für eine Lücke:

```
idx_from,state_from,...
45,5,...        ← Übergang von Position 45 ist gültig
48,9,...        ← Übergang von Position 48 ist gültig
                ← Positionen 46 und 47 fehlen!
```

**Warum fehlen 46 und 47?**
- Die Übergänge von Position 46→47 und 47→48 waren **nicht in der erwarteten Sequenz**
- Sie wurden daher vom Algorithmus herausgefiltert (Zeile 31-33 in `analyzer.py`)
- Dies könnte bedeuten, dass der Teilnehmer hier einen Fehler gemacht oder einen unerwarteten Übergang gespielt hat

## Technische Details

### Code-Stelle für die Filterung
In `analyzer.py` (Zeilen 24-34):
```python
# Bestimme Block-Typ und erwartete Übergangssequenz
pattern = choose_freq_pattern(block, len(events))
block_type = 'Test' if pattern == 'Test' else 'Block'
sequence = get_transition_sequence(block_type)
valid_transitions = set(sequence)

# Filtere nur Übergänge, die in der erwarteten Sequenz vorkommen
transitions_filtered = transitions[transitions['transition_id'].isin(valid_transitions)].copy()
```

### Was bedeuten die transition_id Werte?

Die `transition_id` ist eine **zweistellige Zahl**, die den Übergang codiert:
- **Erste Ziffer**: Start-State (1-9)
- **Zweite Ziffer**: Ziel-State (1-9)

**Beispiele:**
- `67` = Übergang von State 6 zu State 7
- `78` = Übergang von State 7 zu State 8
- `91` = Übergang von State 9 zu State 1
- `13` = Übergang von State 1 zu State 3

### Was bedeutet state_from_freq?

- **`h`** = häufiger Übergang (high frequency)
- **`s`** = seltener Übergang (seldom/low frequency)

Diese Klassifikation basiert auf dem vordefinierten Mapping in `config.py`:
```python
TRANSITION_FREQUENCIES = {
    12: "h", 13: "s", 23: "h", 24: "s", 32: "s", 34: "h", 
    45: "h", 46: "s", 56: "h", 57: "s", 65: "s", 67: "h", 
    78: "h", 79: "s", 81: "s", 89: "h", 91: "h", 98: "s"
}
```

## Zusammenfassung

- **`idx_from`** = Position des Start-States in der MIDI-Datei
- **Lücken entstehen**, weil ungültige/unerwartete Übergänge herausgefiltert werden
- Dies ermöglicht die **Analyse nur der relevanten, erwarteten Übergänge**
- Lücken können auf **Fehler oder Abweichungen** des Teilnehmers hinweisen
