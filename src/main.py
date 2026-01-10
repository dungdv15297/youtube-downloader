"""
YouTube Downloader - Main Entry Point
A simple tool to download YouTube videos.
"""

import sys
import os

# Add src to path for imports when running directly
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Now import with absolute imports
from ui.main_window import MainWindow


def main():
    """Main application entry point."""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()

