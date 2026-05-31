#!/bin/bash
# YouTube Downloader wrapper - ensures ffmpeg is found
export PATH="/opt/homebrew/bin:$PATH"
export PYINSTALLER_PYTHONPATH="/opt/homebrew/bin:/opt/homebrew/lib"

APP_PATH="$(dirname "$0")/../"

if [ -d "${APP_PATH}YouTube Downloader.app" ]; then
    exec open "${APP_PATH}YouTube Downloader.app" --args --ffmpeg-path="/opt/homebrew/bin/ffmpeg"
else
    exec python3 "${APP_PATH}youtube_downloader.py"
fi
