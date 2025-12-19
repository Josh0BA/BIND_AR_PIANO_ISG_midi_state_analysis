"""
midi_state_analysis package.
CLI entrypoint plus grouped helpers for detection, transitions, config, and path utils.
"""

# Entrypoints
from .cli import main
from .analyzer import analyze_root_folder

# Detection / transitions
from .state_detection import detect_states_in_midi
from .transitions import compute_transitions, choose_freq_pattern, compute_transition_id

# Config / sequences
from .config import (
    STATE_DEFS,
    COMBO_TO_STATE,
    TEST_TRANSITION_SEQUENCE,
    BLOCK_TRANSITION_SEQUENCE,
    TRANSITION_FREQUENCIES,
    map_transition_index_to_states,
    get_transition_sequence,
    get_expected_transition_at_index,
)

# Path / MIDI utils
from .folder_utils import find_midi_data_folder, parse_subject_and_block, normalize_block_name
from .midi_utils import get_sec_per_tick, merge_music_tracks

__all__ = [
    # Entrypoints
    "main",
    "analyze_root_folder",
    # Detection / transitions
    "detect_states_in_midi",
    "compute_transitions",
    "choose_freq_pattern",
    "compute_transition_id",
    # Config / sequences
    "STATE_DEFS",
    "COMBO_TO_STATE",
    "TEST_TRANSITION_SEQUENCE",
    "BLOCK_TRANSITION_SEQUENCE",
    "TRANSITION_FREQUENCIES",
    "map_transition_index_to_states",
    "get_transition_sequence",
    "get_expected_transition_at_index",
    # Path / MIDI utils
    "find_midi_data_folder",
    "parse_subject_and_block",
    "normalize_block_name",
    "get_sec_per_tick",
    "merge_music_tracks",
]
