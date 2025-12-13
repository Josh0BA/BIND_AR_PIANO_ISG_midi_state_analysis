from typing import List, Tuple, Set
import mido
from .config import COMBO_TO_STATE
from .midi_utils import get_sec_per_tick, merge_music_tracks

def detect_states_in_midi(mid: mido.MidiFile) -> List[Tuple[float, int]]:
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
        if len(pressed) == 6:
            state = COMBO_TO_STATE.get(frozenset(pressed))
            if state is not None and state != last_state:
                events.append((ticks * sec_per_tick, state))
                last_state = state
    return events
