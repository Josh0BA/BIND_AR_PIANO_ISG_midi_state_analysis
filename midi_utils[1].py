import mido

def get_sec_per_tick(mid: mido.MidiFile) -> float:
    tempo = 500000
    for msg in mid.tracks[0]:
        if msg.type == "set_tempo":
            tempo = msg.tempo
            break
    return tempo / 1_000_000 / mid.ticks_per_beat

def merge_music_tracks(mid: mido.MidiFile):
    return mido.merge_tracks(mid.tracks[1:]) if len(mid.tracks) > 1 else mid.tracks[0]
