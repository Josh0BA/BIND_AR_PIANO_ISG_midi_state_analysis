import sys, os

# Prefer package-relative import; fall back to absolute when run as a script
try:
    from .cli import main
except ImportError:
    # When executed directly (no parent package), add project root to sys.path
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(pkg_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from midi_state_analysis.cli import main

if __name__ == "__main__":
    main()
