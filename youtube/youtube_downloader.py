#!/usr/bin/env python3
"""YouTube Downloader - YouTube video downloader for macOS."""

import sys
import os
import glob
import subprocess
import yt_dlp
from datetime import datetime

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QProgressBar, QTextEdit,
        QMessageBox, QFileDialog,
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QFont
except ImportError:
    print("PyQt5 is required. Install: python3 -m pip install PyQt5")
    sys.exit(1)


def find_ffmpeg_location():
    """Find ffmpeg binary location for yt-dlp."""
    # Try system PATH first
    try:
        result = subprocess.run(
             ["which", "ffmpeg"],
            capture_output=True, text=True, timeout=3
         )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

     # Try PyInstaller bundled ffmpeg - multiple possible locations
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        possible_locs = [
            os.path.join(exe_dir, 'ffmpeg'),
            os.path.join(exe_dir, '..', 'MacOS', 'ffmpeg'),
            os.path.join(exe_dir, '..', 'Contents', 'MacOS', 'ffmpeg'),
            os.path.join(exe_dir, '..', 'Resources', 'ffmpeg'),
            os.path.join(exe_dir, '..', '..', 'MacOS', 'ffmpeg'),
         ]
        for candidate in possible_locs:
            real = os.path.realpath(candidate)
            if os.path.isfile(real) and os.access(real, os.X_OK):
                 # Check if the bundled binary actually works
                try:
                    check = subprocess.run([real, '-version'], capture_output=True, timeout=3)
                    if check.returncode == 0 or 'ffmpeg' in check.stdout.decode('utf-8', errors='ignore').lower():
                        return real
                except Exception:
                    pass # Bundled binary doesn't work (SIP, corrupted, etc)

     # Last resort: try common brew paths
    # Hardcoded fallback for Apple Silicon Macs — this is where homebrew installs ffmpeg
    if os.path.isfile('/opt/homebrew/bin/ffmpeg'):
        return '/opt/homebrew/bin/ffmpeg'
    if os.path.isfile('/opt/homebrew/Cellar/ffmpeg/*/bin/ffmpeg'):
        return glob.glob('/opt/homebrew/Cellar/ffmpeg/*/bin/ffmpeg')[-1]
    return None


def set_ffmpeg_frameworks():
    """Set DYLD_FRAMEWORK_PATH for ffmpeg bundled dylibs."""
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        # Try multiple possible locations for ffmpeg libs
        lib_dir = os.path.join(exe_dir, '..', 'Frameworks', 'ffmpeg_libs')
        if not os.path.isdir(lib_dir):
            lib_dir = os.path.join(exe_dir, '..', 'Resources', 'ffmpeg_libs')
        if os.path.isdir(lib_dir):
            try:
                lib_path = os.environ.get('DYLD_LIBRARY_PATH', '')
                fw_path = os.environ.get('DYLD_FRAMEWORK_PATH', '')
                if lib_path:
                    os.environ['DYLD_LIBRARY_PATH'] = lib_dir + ':' + lib_path
                if fw_path:
                    os.environ['DYLD_FRAMEWORK_PATH'] = lib_dir + ':' + fw_path
            except Exception:
                pass


class DownloadWorker(QThread):
    """yt-dlp downloads in background thread."""

    progress_signal = pyqtSignal(str, float)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, url, save_dir):
        super().__init__()
        self.url = url
        self.save_dir = save_dir

    def run(self):
        try:
            # Find ffmpeg location for yt-dlp
            ffmpeg_bin = find_ffmpeg_location()

            ydl_opts = {
                "outtmpl": os.path.join(
                    self.save_dir, "%(title)s.%(ext)s"
                ),
                "progress_hooks": [self._progress_hook],
                "writethumbnail": False,
                "writesubtitles": False,
                "extract_flat": False,
                # KEY FIX: Load cookies from Chrome/Safari to bypass 403
                "cookies_from_browser": "chrome",
                "socket_timeout": 30,
                # Retry 3 times on failure
                "retries": 3,
                # Format: best video+audio merged, both in MP4
                 "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best[ext=mp4]/best",
                "user_agent": "",
                # Explicitly set ffmpeg path so yt-dlp can merge formats
                "ffmpeg_location": ffmpeg_bin,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                title = info.get("title", "downloaded_video")
                pattern = os.path.join(
                    self.save_dir, "*" + title + "*.*"
                )
                files = glob.glob(pattern)
                if not files:
                    files = sorted(
                        glob.glob(os.path.join(self.save_dir, "*.*")),
                        key=os.path.getmtime,
                        reverse=True,
                    )[:1]
                if files:
                    self.finished_signal.emit(os.path.dirname(files[0]))
                else:
                    self.finished_signal.emit(self.save_dir)
        except Exception as e:
            self.error_signal.emit(str(e))

    def _progress_hook(self, d):
        if d["status"] == "downloading":
            pct = d.get("percent", 0)
            speed = d.get("speed", 0) or 0
            eta = d.get("eta", 0) or 0
            if speed < 1024:
                speed_str = f"{speed}B/s"
            elif speed < 1024 * 1024:
                speed_str = f"{speed/1024:.1f}KB/s"
            else:
                speed_str = f"{speed/1024/1024:.1f}MB/s"
            eta_str = f"{eta}s left" if eta > 0 else ""
            msg = (
                f"[{pct:.1f}%] Speed: {speed_str}       {eta_str}"
            ).strip()
            self.progress_signal.emit(msg, float(pct))
        elif d["status"] == "finished":
            self.progress_signal.emit(
                "Finalizing downloads...", 100.0
            )


class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setMinimumSize(660, 500)
        self.resize(700, 520)
        self.worker = None
        self.default_dir = os.path.expanduser("~/Downloads")
        self._font = QFont("SF Pro Display", 11)
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(10)

        # Title
        t = QLabel("YouTube Downloader")
        t.setFont(QFont("SF Pro Display", 18, QFont.Bold))
        t.setAlignment(Qt.AlignCenter)
        lay.addWidget(t)

        sub = QLabel(
            "URL 입력 후 다운로드\n(Browser cookies auto-loading 방식)"
        )
        sub.setFont(QFont("SF Pro Display", 10))
        sub.setStyleSheet("color: #888;")
        sub.setAlignment(Qt.AlignCenter)
        lay.addWidget(sub)

        # URL input row
        row = QHBoxLayout()
        row.addWidget(QLabel("URL: "))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "https://www.youtube.com/watch?v=..."
        )
        self.url_input.setFont(self._font)
        row.addWidget(self.url_input)
        lay.addLayout(row)

        # Save directory row
        srow = QHBoxLayout()
        srow.addWidget(QLabel("저장 위치: "))
        self.save_label = QLabel(self.default_dir)
        self.save_label.setFont(QFont("SF Mono", 9))
        srow.addWidget(self.save_label)
        srow.addStretch()
        b_change = QPushButton("변경")
        b_change.setFixedSize(72, 30)
        b_change.setFont(self._font)
        b_change.clicked.connect(self._pick_dir)
        srow.addWidget(b_change)
        lay.addLayout(srow)

        # Download button
        self.dl_btn = QPushButton("Download")
        self.dl_btn.setFont(
            QFont("SF Pro Display", 13, QFont.Bold)
        )
        self.dl_btn.setFixedHeight(40)
        self.dl_btn.clicked.connect(self._start_dl)
        lay.addWidget(self.dl_btn)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setFixedHeight(22)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        lay.addWidget(self.progress)

        # Status label
        self.status_lbl = QLabel("준비됨 (Ready)")
        self.status_lbl.setFont(QFont("SF Mono", 9))
        self.status_lbl.setStyleSheet("color: #777;")
        lay.addWidget(self.status_lbl)

        # Log title
        log_title = QLabel("로그 (스크롤 없음)")
        log_title.setFont(
            QFont("SF Pro Display", 10, QFont.Bold)
        )
        lay.addWidget(log_title)

        # Log area - scroll free, auto resize
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("SF Mono", 9))
        self.log_view.setPlaceholderText(
            "로그가 여기에 표시됩니다..."
        )
        self.log_view.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        self.log_view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        self.log_view.setMinimumHeight(110)
        self.log_view.setMaximumHeight(300)
        lay.addWidget(self.log_view)

        # Footer button row
        frow = QHBoxLayout()
        frow.addStretch()
        b_clear = QPushButton("로그 지우기")
        b_clear.setFixedSize(100, 30)
        b_clear.setFont(self._font)
        b_clear.clicked.connect(self._clear_log)
        frow.addWidget(b_clear)
        lay.addLayout(frow)

    def _pick_dir(self):
        dlg = QFileDialog(self, "저장 위치 선택")
        dlg.setFileMode(QFileDialog.Directory)
        dlg.setOption(QFileDialog.ShowDirsOnly, True)
        dlg.setDirectory(self.default_dir)
        if dlg.exec_() == QFileDialog.Accepted:
            d = dlg.selectedFiles()
            if d:
                self.default_dir = d[0]
                self.save_label.setText(self.default_dir)
                self._log(
                    f"저장 위치 변경: {self.default_dir}"
                )

    def _start_dl(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(
                self, "경고", "URL을 입력하세요."
            )
            return
        if not url.startswith("http"):
            QMessageBox.warning(
                self, "경고", "올바른 URL을 입력하세요."
            )
            return
        if (
            self.worker is not None
            and self.worker.isRunning()
        ):
            QMessageBox.warning(
                self, "경고", "이미 다운로드 중입니다."
            )
            return

        self.dl_btn.setEnabled(False)
        self.url_input.setEnabled(False)
        self.progress.setValue(0)
        self.status_lbl.setText("준비 중...")
        self._log("=" * 55)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log(f"시작: {ts}")
        self._log(f"URL: {url}")
        self._log(f"저장 위치: {self.default_dir}")
        self._log("쿠키 출처: YouTube Chrome (자동)")
        self._log("-" * 55)

        self.worker = DownloadWorker(
            url, self.default_dir
        )
        self.worker.progress_signal.connect(
            self._on_progress
        )
        self.worker.finished_signal.connect(
            self._on_done
        )
        self.worker.error_signal.connect(
            self._on_error
        )
        self.worker.start()

    def _on_progress(self, msg, pct):
        self.progress.setValue(int(pct))
        self.status_lbl.setText(msg)
        self._log(msg)
        self._auto_resize()

    def _on_done(self, save_dir):
        self._reset_ui()
        self._log("-" * 55)
        ts2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log(f"완료! {ts2}")
        self._log(f"저장 위치: {save_dir}")
        self._log("=" * 55)
        self._auto_resize()
        QMessageBox.information(
            self, "완료",
            f"다운로드가 완료되었습니다!\n\n"
            f"저장 위치: {save_dir}",
        )

    def _on_error(self, err):
        self._reset_ui()
        self.status_lbl.setText("오류 발생")
        self.progress.setValue(0)
        self._log("-" * 55)
        self._log(f"오류: {err}")
        self._log("=" * 55)
        self._auto_resize()
        QMessageBox.critical(
            self, "오류",
            f"다운로드 중 오류가 발생했습니다:\n\n{err}"
        )

    def _reset_ui(self):
        self.dl_btn.setEnabled(True)
        self.url_input.setEnabled(True)

    def _log(self, msg):
        cur = self.log_view.toPlainText()
        self.log_view.setPlainText(
            (cur + "\n" + msg) if cur else msg
        )

    def _clear_log(self):
        self.log_view.setPlainText("")

    def _auto_resize(self):
        doc = self.log_view.document()
        n = doc.blockCount()
        lh = self.log_view.fontMetrics().lineSpacing() + 2
        h = max(110, min(n * lh + 10, 320))
        self.log_view.setMinimumHeight(h)
        self.log_view.setMaximumHeight(h)


def main():
    # Set ffmpeg library paths if bundled
    set_ffmpeg_frameworks()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("YouTube Downloader")
    win = YouTubeDownloader()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
