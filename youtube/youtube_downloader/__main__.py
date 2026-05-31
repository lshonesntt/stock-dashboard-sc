"""Entry point -- run with: python -m youtube_downloader"""

from youtube_downloader.gui import main as _main


def main():
     """Launch the GUI application."""
     _main()


if __name__ == "__main__":
      # python -m youtube_downloader (package mode)
     main()
