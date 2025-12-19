"""Module entry point to launch the CLI."""

import sys
import os

# Support running as a module (-m midi_state_analysis) and direct file execution
try:
    from midi_state_analysis import main
except ImportError:
    # When executed directly, add project root to sys.path and retry
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(pkg_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from midi_state_analysis import main


if __name__ == "__main__":
    main()
