from typing import List, Tuple, Set
import mido
import pandas as pd
from .config import COMBO_TO_STATE, STATE_DEFS
from .midi_utils import get_sec_per_tick, merge_music_tracks

def detect_states_in_midi(mid: mido.MidiFile) -> pd.DataFrame:
    sec_per_tick = get_sec_per_tick(mid)
    track = merge_music_tracks(mid)
    pressed: Set[int] = set()
    events = []
    last_state = None
    ticks = 0
    for msg in track:
        ticks += msg.time
        if msg.type == "note_on" and msg.velocity > 0:
            pressed.add(msg.note)
        elif msg.type in ("note_on", "note_off"):
            pressed.discard(msg.note)
        
        state = None
        extra_keys = []
        
        if len(pressed) == 6:
            state = COMBO_TO_STATE.get(frozenset(pressed))
        elif len(pressed) > 6:
            # Prüfe ob einer der definierten States ein Subset der gedrückten Tasten ist
            for state_id, state_notes in STATE_DEFS.items():
                if state_notes.issubset(pressed):
                    state = state_id
                    extra_keys = list(pressed - state_notes)
                    break
        
        if state is not None and state != last_state:
            event = {
                "time_s": ticks * sec_per_tick, 
                "state": state,
                "extra_keys": extra_keys if extra_keys else None,
                "total_keys_pressed": len(pressed)
            }
            events.append(event)
            last_state = state
    return pd.DataFrame(events)
