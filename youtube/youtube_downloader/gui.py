"""YouTube Downloader GUI - PyQt5 application for macOS."""

import sys
import os
import glob
import yt_dlp
from datetime import datetime

from PyQt5.QtWidgets import (
     QApplication,
     QMainWindow,
     QWidget,
     QVBoxLayout,
     QHBoxLayout,
     QLabel,
     QLineEdit,
     QPushButton,
     QProgressBar,
     QTextEdit,
     QMessageBox,
     QFileDialog,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont


class DownloadWorker(QThread):
    """Runs yt-dlp in a background thread."""

    progress_signal = pyqtSignal(str, float)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, url, save_dir):
        super().__init__()
        self.url = url
        self.save_dir = save_dir

    def run(self):
        try:
            ydl_opts = {
                 "outtmpl": os.path.join(
                     self.save_dir, "%(title)s.%(ext)s"
                 ),
                 "progress_hooks": [self._progress_hook],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                title = info.get("title", "downloaded_video")
                pattern = os.path.join(self.save_dir, "*" + title + "*.*")
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
            speed_str = self._fmt_size(speed) + "/s"
            eta_str = f"{eta}s 남음" if eta > 0 else ""
            msg = f"[{pct:.1f}%] 속도: {speed_str} {eta_str}".strip()
            self.progress_signal.emit(msg, float(pct))
        elif d["status"] == "finished":
            self.progress_signal.emit("최종 정리 중...", 100.0)

    @staticmethod
    def _fmt_size(b):
        if b < 1024:
            return f"{b}B"
        elif b < 1024 * 1024:
            return f"{b/1024:.1f}KB"
        return f"{b/1024/1024:.1f}MB"


class YouTubeDownloader(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setMinimumSize(660, 460)
        self.resize(700, 480)
        self.worker = None
        self.default_dir = os.path.expanduser("~/Downloads")
        self._font = QFont("Apple SD Gothic Neo", 11)
        self._init_ui()

    # ── UI ───────────────────────────────────

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

        sub = QLabel("URL 입력 후 다운로드하세요")
        sub.setFont(QFont("SF Pro", 10))
        sub.setStyleSheet("color: #888;")
        sub.setAlignment(Qt.AlignCenter)
        lay.addWidget(sub)

        # URL row
        row = QHBoxLayout()
        row.addWidget(QLabel("URL: "))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "https://www.youtube.com/watch?v=..."
        )
        self.url_input.setFont(self._font)
        row.addWidget(self.url_input)
        lay.addLayout(row)

        # Save dir row
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
        self.dl_btn.setFont(QFont("SF Pro", 13, QFont.Bold))
        self.dl_btn.setFixedHeight(40)
        self.dl_btn.clicked.connect(self._start_dl)
        lay.addWidget(self.dl_btn)

        # Progress
        self.progress = QProgressBar()
        self.progress.setFixedHeight(22)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        lay.addWidget(self.progress)

        # Status
        self.status_lbl = QLabel("준비됨")
        self.status_lbl.setFont(QFont("SF Mono", 9))
        self.status_lbl.setStyleSheet("color: #777;")
        lay.addWidget(self.status_lbl)

        # Log
        log_title = QLabel("로그")
        log_title.setFont(QFont("SF Pro", 10, QFont.Bold))
        lay.addWidget(log_title)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("SF Mono", 9))
        self.log_view.setPlaceholderText("로그가 여기에 표시됩니다...")
        self.log_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.log_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.log_view.setMinimumHeight(110)
        self.log_view.setMaximumHeight(300)
        lay.addWidget(self.log_view)

        # Footer
        frow = QHBoxLayout()
        frow.addStretch()
        b_clear = QPushButton("로그 지우기")
        b_clear.setFixedSize(90, 30)
        b_clear.setFont(self._font)
        b_clear.clicked.connect(self._clear_log)
        frow.addWidget(b_clear)
        lay.addLayout(frow)

    # ── Actions ───────────────────────────────

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
                self._log(f"위치 변경: {self.default_dir}")

    def _start_dl(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "경고", "URL을 입력하세요.")
            return
        if not url.startswith("http"):
            QMessageBox.warning(
                self, "경고", "올바른 URL을 입력하세요."
            )
            return
        if self.worker is not None and self.worker.isRunning():
            QMessageBox.warning(
                self, "경고", "이미 다운로드 중입니다."
            )
            return

        self.dl_btn.setEnabled(False)
        self.url_input.setEnabled(False)
        self.progress.setValue(0)
        self.status_lbl.setText("준비 중...")
        self._log("=" * 55)
        self._log(f"시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log(f"URL: {url}")
        self._log(f"위치: {self.default_dir}")
        self._log("-" * 55)

        self.worker = DownloadWorker(url, self.default_dir)
        self.worker.progress_signal.connect(self._on_progress)
        self.worker.finished_signal.connect(self._on_done)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()
        self._log("yt-dlp로 다운로드 시작...")

    def _on_progress(self, msg, pct):
        self.progress.setValue(int(pct))
        self.status_lbl.setText(msg)
        self._log(msg)
        self._auto_resize()

    def _on_done(self, save_dir):
        self._reset_ui()
        self._log("-" * 55)
        self._log(f"완료! {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log(f"저장 위치: {save_dir}")
        self._log("=" * 55)
        self._auto_resize()
        QMessageBox.information(
            self, "완료",
            f"다운로드 완료!\n\n저장 위치: {save_dir}",
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
            self, "오류", f"다운로드 오류:\n\n{err}"
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
    """Launch the YouTube Downloader GUI app."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("YouTube Downloader")
    win = YouTubeDownloader()
    win.show()
    sys.exit(app.exec_())
