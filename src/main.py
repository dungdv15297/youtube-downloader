"""
Tools Hub - Main Entry Point
A collection of useful tools including YouTube Downloader and CapCut Caption Extractor.
"""

import sys
import os

# Add src to path for imports when running directly
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Now import with absolute imports
from ui.tool_launcher import ToolLauncher


def main():
    """Main application entry point."""
    app = ToolLauncher()
    app.mainloop()


if __name__ == "__main__":
    main()

