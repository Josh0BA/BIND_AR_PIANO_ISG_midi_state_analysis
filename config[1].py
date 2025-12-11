from typing import Dict, Set

STATE_DEFS: Dict[int, Set[int]] = {
    0: {65, 67, 72, 74, 77, 79},
    1: {60, 62, 64, 72, 77, 79},
    2: {60, 62, 64, 67, 72, 76},
    3: {60, 62, 64, 76, 77, 79},
    4: {62, 64, 65, 76, 77, 79},
    5: {64, 65, 72, 76, 77, 79},
    6: {60, 62, 72, 74, 76, 77},
    7: {64, 65, 72, 74, 77, 79},
    8: {62, 64, 65, 67, 72, 74},
}

COMBO_TO_STATE = {frozenset(notes): s for s, notes in STATE_DEFS.items()}

BLOCK_FREQ_BY_INDEX: Dict[str, Dict[int, str]] = {
    "Block_Training": {0:"h",1:"h",2:"h",3:"h",4:"h",5:"h",6:"h",7:"h",8:"h",9:"h",10:"s"},
    "Test": {0:"h",1:"s",2:"s",3:"s"}
}
