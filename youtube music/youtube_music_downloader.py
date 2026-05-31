#!/usr/bin/env python3
"""
YouTube Music Downloader
- 유튜브 URL 입력 -> 음원만 다운로드
- yt-dlp가 MP3로 자동 변환
- 메타데이터 있으면: 제목_가수.mp3
- 메타데이터 없으면: 파장 분석으로 분할
"""

import sys
import os
import subprocess
import tempfile
import shutil
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox,
    QProgressBar, QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

import yt_dlp
import mutagen


class YouTubeMusicWorker(QThread):
    """유튜브 영상 다운로드 및 음원 분할 워커"""
    progress_signal = pyqtSignal(str, float)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, url, save_dir, cookies_file=None):
        super().__init__()
        self.url = url
        self.save_dir = save_dir
        self.cookies_file = cookies_file
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def _log(self, msg):
        self.progress_signal.emit(msg, 0)

    def _get_ydl_opts(self, extra_opts=None, cookies_file=None):
        """yt-dlp 옵션 생성 (MP3 자동 변환 + 403 오류 해결)"""
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(tempfile.gettempdir(), 'ytmusic_temp_%(id)s.%(ext)s'),
            'noplaylist': False,
            'writethumbnail': False,
            'quiet': False,
            'no_warnings': True,
            'progress_hooks': [self._yt_dlp_hook],
            'ffmpeg_location': '/opt/homebrew/Cellar/ffmpeg/8.1.1/bin/ffmpeg',
            # 403 Forbidden 해결: 브라우저 쿠키 + 검증된 플레이어 클라이언트
            'extractor_args': {
                'youtube': {
                    'player_client': ['basic', 'ios', 'web'],
                    'player_skip': ['noauthorincidents'],
                }
            },
            'retries': 5,
            'retry_sleep': 3,
            # 오디오 -> MP3 자동 변환 (mp4, m4a, webm 등 모두 지원)
            'postprocessors': [{
                 'key': 'FFmpegExtractAudio',
                 'codec': 'mp3',
                 'quality': '192k',
             }],
        }
        if cookies_file and os.path.exists(cookies_file):
            opts['cookiefile'] = cookies_file
        # yt-dlp에서 브라우저 쿠키 직접 사용 (Chrome/Safari/Firefox/Edge)
        if 'cookiefile' not in opts:
            for browser in ['safari', 'chrome', 'firefox', 'edge', 'chromium']:
                try:
                    opts['cookies_from_browser'] = browser
                    break
                except Exception:
                    continue
        if extra_opts:
            opts.update(extra_opts)
        return opts

    def _process_single_file(self, audio_path, title, artist):
        """단일 오디오 파일을 MP3로 конвертер하여 저장"""
        if not audio_path or not os.path.exists(audio_path):
            return False

        self._log(f"오디오 처리: {os.path.basename(audio_path)}")

        try:
             # 파일 형식 확인
            ext = os.path.splitext(audio_path)[1].lower()

             # 이미 mp3면 그대로 사용
            if ext == '.mp3':
                convert_path = audio_path
            else:
                 # ffmpeg로 MP3 변환 시도 (mp4, m4a, webm, ogg, flac, wav 등 모든 포맷 지원)
                self._log(f"MP3 변환 시작 ({ext} -> mp3)")
                convert_path = audio_path.replace(ext, '.mp3')

                subprocess.run([
                    '/opt/homebrew/Cellar/ffmpeg/8.1.1/bin/ffmpeg', '-y',
                    '-i', audio_path, '-b:a', '192k', '-vn', convert_path
                ], capture_output=True, timeout=120)

                # ffmpeg 실패 시 pydub으로 재시도
                if not os.path.exists(convert_path):
                    try:
                        from pydub import AudioSegment
                        audio = AudioSegment.from_file(audio_path)
                        audio.export(convert_path, format="mp3", bitrate="192k")
                    except Exception as pe:
                        self._log(f"pydub 변환 실패: {pe}")
                        # pydub도 실패하면 ffmpeg stdout/stderr 로그 출력
                        if not os.path.exists(convert_path):
                            self._log("변환 실패 - 원본 파일 형식 시도")
                            return False

            # 메타데이터 삽입
            try:
                audio_meta = mutagen.File(convert_path, easy=True)
                if audio_meta is not None:
                    audio_meta['TIT2'] = title or '미정'
                    if artist:
                        audio_meta['TPE1'] = artist
                    audio_meta.save()
            except Exception as e:
                self._log(f"메타데이터 삽입 실패: {e}")

            # 원본 임시 파일 삭제 (mp3가 아니면)
            if ext != '.mp3':
                try:
                    os.remove(audio_path)
                except:
                    pass

            # 저장 폴더로 이동
            if artist:
                final_name = f"{title}_{artist}.mp3"
            else:
                final_name = f"{title}.mp3"

            final_path = os.path.join(self.save_dir, final_name)
            shutil.move(convert_path, final_path)

            self._log(f"저장 완료: {final_name}")
            return True

        except Exception as e:
            self._log(f"파일 처리 오류: {e}")
            return False

    def _autodetect_and_split(self, audio_file, save_dir, default_title, default_artist):
        """
        자동 분할: 에너지 기반 곡 경계 감지
        리턴: 분할 성공 여부
        """
        try:
            from pydub import AudioSegment
            import numpy as np

            # 오디오 로드
            audio = AudioSegment.from_file(audio_file)

            # samples를 numpy 배열로 변환
            raw = audio.get_array_of_samples()
            if audio.channels > 1:
                raw_array = np.array(raw).reshape(-1, audio.channels).astype(np.float32)[:, 0]
            else:
                raw_array = np.array(raw).astype(np.float32) / (1 << (8 * audio.sample_width - 1))

            # rms 에너지 계산 (100ms 윈도우)
            frame_ms = 100
            frame_samples = int(frame_ms * audio.frame_rate / 1000)
            hop_ms = 25
            hop_samples = int(hop_ms * audio.frame_rate / 1000)

            rms_values = []
            for i in range(0, len(raw_array) - frame_samples, hop_samples):
                chunk = raw_array[i:i + frame_samples]
                rms = float(np.sqrt(np.mean(chunk ** 2)))
                rms_values.append(rms)

            rms_values = np.array(rms_values, dtype=np.float32)

            # 에너지가 매우 낮은 구간을 정적으로 판별
            threshold = np.percentile(rms_values, 3)
            is_silence = rms_values < threshold

            # silence mask dilate (작은 끊김은 무시)
            kernel = int(300 // hop_ms)
            dilated = np.zeros(len(is_silence), dtype=bool)
            for i in range(len(is_silence)):
                start_j = max(0, i - kernel)
                end_j = min(len(is_silence), i + kernel + 1)
                dilated[i] = bool(np.any(is_silence[start_j:end_j]))
            is_silence = dilated

            # 분할 지점 찾기 (정적에서 음악으로 바뀌는 지점)
            splits = []
            for i in range(1, len(is_silence)):
                if not is_silence[i] and is_silence[i - 1]:
                    split_sample = i * hop_samples
                    splits.append(split_sample)

            # 최소 2개 이상의 분할 지점이 있어야 의미 있음
            if len(splits) < 2:
                self._log("분할 지점이 2개 미만 - 원본 저장")
                return False

            # 분할 지점 정리 (최소 10초 간격)
            min_interval = int(10 * audio.frame_rate)
            filtered_splits = [splits[0]]
            for s in splits[1:]:
                if s - filtered_splits[-1] >= min_interval:
                    filtered_splits.append(s)

            if len(filtered_splits) < 2:
                return False

            # 분할 + 저장
            from pydub.silence import remove_silence
            saved_count = 0
            for i in range(len(filtered_splits)):
                start_s = filtered_splits[i]
                end_s = filtered_splits[i + 1] if i + 1 < len(filtered_splits) else None

                # 샘플을 ms로 변환
                start_ms = max(0, int(start_s / audio.frame_rate * 1000))
                if end_s is not None:
                    end_ms = min(len(audio), int(end_s / audio.frame_rate * 1000))
                else:
                    end_ms = len(audio)

                chunk = audio[start_ms:end_ms]
                if len(chunk) < int(2 * audio.frame_rate):
                    continue

                # 정적 제거
                try:
                    clean_chunk = remove_silence(chunk, silence_threshold=-40, silence_thresh=200, keep_silence=100)[0]
                except Exception:
                    clean_chunk = chunk

                if len(clean_chunk) < int(2 * audio.frame_rate):
                    continue

                saved_count += 1
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"[자동분할_{ts}_{saved_count:02d}]"
                out_path = os.path.join(save_dir, f"{filename}.mp3")

                clean_chunk.export(out_path, format="mp3", bitrate="192k")
                self._log(f"  분할 저장: {os.path.basename(out_path)}")

            return saved_count >= 2

        except Exception as e:
            import traceback
            self._log(f"자동 분할 예외: {e}\n{traceback.format_exc()}")
            return False

    def run(self):
        try:
            self._log(f"음원 다운로드 시작: {self.url}")

            ydl_opts = self._get_ydl_opts()

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)

            # 다운로드된 파일 찾기 (임시 디렉토리에서)
            downloaded_files = []
            for f in os.listdir(tempfile.gettempdir()):
                fp = os.path.join(tempfile.gettempdir(), f)
                if (os.path.isfile(fp) and
                    f.startswith('ytmusic_temp_') and
                    f.endswith(('.mp3', '.m4a', '.webm', '.opus', '.wav', '.flac'))):
                    downloaded_files.append(fp)

            if not downloaded_files:
                self.error_signal.emit("음원을 다운로드하지 못했습니다.")
                return

            # 전체 메타데이터 추출
            self._log("메타데이터 분석 중...")
            all_metadata = info.get('artist', '') or info.get('creator', '') or ''
            all_title = info.get('title', '미정') or '미정'

            # tracks 정보 (재생목록인 경우)
            tracks = info.get('entries', [])

            if tracks:
                # 재생목록 처리
                self._log(f"재생목록 감지됨: 총 {len(tracks)}개 곡")
                for i, entry in enumerate(tracks, 1):
                    if self._cancelled:
                        break

                    artist = entry.get('artist', '') or entry.get('creator', '') or all_metadata
                    title = entry.get('title', '미정') or '미정'

                    self._log(f"[{i}/{len(tracks)}] 다운로드: {title} - {artist or '미정'}")

                    # yt-dlp로 개별 트랙 다운로드
                    track_outtmpl = os.path.join(tempfile.gettempdir(), f'ytmusic_track_{i:03d}.%(ext)s')
                    track_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': track_outtmpl,
                        'noplaylist': True,
                        'writethumbnail': False,
                        'quiet': True,
                        'no_warnings': True,
                        'ffmpeg_location': '/opt/homebrew/Cellar/ffmpeg/8.1.1/bin/ffmpeg',
                        'extractor_args': {
                            'youtube': {
                                'player_client': ['basic', 'ios', 'web'],
                            }
                        },
                        'postprocessors': [{
                             'key': 'FFmpegExtractAudio',
                             'codec': 'mp3',
                             'quality': '192k',
                         }],
                    }

                    track_path = None
                    try:
                        with yt_dlp.YoutubeDL(track_opts) as track_ydl:
                            track_ydl.download([entry.url])

                        # 변환된 파일 찾기
                        for f in os.listdir(tempfile.gettempdir()):
                            fp = os.path.join(tempfile.gettempdir(), f)
                            if f.startswith('ytmusic_track_') and f.endswith(('.mp3', '.m4a', '.webm')):
                                track_path = fp
                                break

                    except Exception as e:
                        self._log(f"트랙 {i} 다운로드 실패: {e}")
                        continue

                    if track_path:
                        self._process_single_file(track_path, title, artist)

                self._log(f"완료: 재생목록 처리 종료")
                self.finished_signal.emit(f"총 {len(tracks)}개 곡 다운로드 완료!")

            elif len(downloaded_files) == 1:
                # 단곡 - 자동 분할 시도
                audio_file = downloaded_files[0]
                self._log(f"단곡 감지됨: {os.path.basename(audio_file)}")

                # MP3 변환 (jt-dlp가 이미 변환했거나 _process_single_file에서 수행)
                converted = self._process_single_file(audio_file, all_title, all_metadata)

                if not converted or not os.path.exists(os.path.join(self.save_dir, f"{all_title}.mp3")):
                    # 분할 시도
                    self._log("단일 파일 자동 분할 시도...")
                    split_done = self._autodetect_and_split(
                        audio_file, self.save_dir, all_title, all_metadata
                    )

                    if not split_done:
                        if converted:
                            pass
                        else:
                            self._log("저장 실패")
            else:
                # 여러 파일 - 개별 처리
                for fp in downloaded_files:
                    if self._cancelled:
                        break
                    self._process_single_file(fp, all_title, all_metadata)

                self._log(f"완료: {len(downloaded_files)}개 파일 처리")
                self.finished_signal.emit(f"{len(downloaded_files)}개 파일 다운로드 완료!")

            self.finished_signal.emit("모든 작업 완료!")

        except Exception as e:
            import traceback
            self.error_signal.emit(f"오류: {str(e)}\n{traceback.format_exc()}")

    def _yt_dlp_hook(self, d):
        if d['status'] == 'downloading':
            pct = d.get('percent', 0)
            self.progress_signal.emit(f"다운로드 중: {pct:.0f}%", pct / 100.0)
        elif d['status'] == 'finished':
            self.progress_signal.emit("MP3 변환 중...", 0.5)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.cookies_file = None
        self.setWindowTitle("YouTube Music Downloader")
        self.setMinimumSize(750, 550)
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # 타이틀
        title = QLabel("YouTube Music Downloader")
        title.setFont(QFont("Helvetica Neue", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # URL 입력 영역
        url_group = QGroupBox("URL 입력")
        url_layout = QHBoxLayout(url_group)

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://www.youtube.com/watch?v=... 또는 재생목록 URL")
        self.url_edit.setMinimumHeight(40)

        url_btn = QPushButton("다운로드")
        url_btn.setMinimumHeight(40)
        url_btn.setMaximumWidth(120)
        url_btn.clicked.connect(self._start_download)

        url_layout.addWidget(self.url_edit)
        url_layout.addWidget(url_btn)
        main_layout.addWidget(url_group)

        # 쿠키 파일 선택 (403 오류 우회용)
        cookie_group = QGroupBox("쿠키 파일 (선택사항)")
        cookie_layout = QHBoxLayout(cookie_group)

        self.cookie_edit = QLineEdit()
        self.cookie_edit.setPlaceholderText("Safari/Chrome 쿠키 파일 경로 (없으면 자동 감지)")
        self.cookie_edit.setReadOnly(True)

        cookie_btn = QPushButton("쿠키 파일 선택")
        cookie_btn.clicked.connect(self._browse_cookie)

            # 자동 감지 체크박스
        self.auto_cookie_check = QCheckBox("브라우저 쿠키 자동 감지")
        self.auto_cookie_check.setChecked(True)

        cookie_layout.addWidget(self.cookie_edit)
        cookie_layout.addWidget(cookie_btn)
        cookie_layout.addWidget(self.auto_cookie_check)
        main_layout.addWidget(cookie_group)

        # 저장 폴더 선택
        folder_group = QGroupBox("저장 폴더")
        folder_layout = QHBoxLayout(folder_group)

        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("음악을 저장할 폴더를 선택하세요...")
        self.folder_edit.setReadOnly(True)

        folder_btn = QPushButton("폴더 선택")
        folder_btn.clicked.connect(self._browse_folder)

        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(folder_btn)
        main_layout.addWidget(folder_group)

        # 진행 상태
        progress_group = QGroupBox("진행 상태")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setMinimumHeight(25)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("대기 중...")
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        progress_layout.addLayout(status_layout)
        main_layout.addWidget(progress_group)

        # 로그 영역
        log_group = QGroupBox("로그")
        log_layout = QVBoxLayout(log_group)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Menlo", 10))
        log_layout.addWidget(self.log_view)
        main_layout.addWidget(log_group)

        # 버튼 영역
        btn_layout = QHBoxLayout()
        main_layout.addLayout(btn_layout)

        self.clear_log_btn = QPushButton("로그 지우기")
        self.clear_log_btn.clicked.connect(self._clear_log)
        btn_layout.addWidget(self.clear_log_btn)

    def _browse_cookie(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "쿠키 파일 선택", "", "Cookies (*.txt);;All Files (*)"
        )
        if path:
            self.cookie_edit.setText(path)
            self.cookies_file = path
            self._log(f"쿠키 파일 로드: {path}")

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "저장 폴더 선택", "")
        if folder:
            self.folder_edit.setText(folder)
            self._log(f"저장 폴더: {folder}")

    def _start_download(self):
        url = self.url_edit.text().strip()
        save_dir = self.folder_edit.text().strip()

        if not url:
            QMessageBox.warning(self, "경고", "유튜브 URL을 입력하세요.")
            return
        if not save_dir or not os.path.isdir(save_dir):
            QMessageBox.warning(self, "경고", "저장 폴더를 선택하세요.")
            return

        # 이전 워커가 있다면 취소
        if self.worker and self.worker.isRunning():
            self.worker.cancel()

        # 쿠키 파일 결정
        cookies_file = None
        if not self.auto_cookie_check.isChecked():
            cookies_file = self.cookies_file

        self._log(f"URL: {url}")
        self._log(f"저장 폴더: {save_dir}")
        if cookies_file:
            self._log(f"쿠키 파일: {cookies_file}")
        else:
            self._log("브라우저 쿠키 자동 감지 사용 중...")

        self.worker = YouTubeMusicWorker(url, save_dir, cookies_file=cookies_file)
        self.worker.progress_signal.connect(self._on_progress)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.error_signal.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, msg, value):
        self.status_label.setText(msg)
        if 0 < value <= 1:
            self.progress_bar.setValue(int(value * 100))
        else:
            self.progress_bar.setValue(0)

    def _on_finished(self, msg):
        self.status_label.setText(msg)
        self.worker = None

    def _on_error(self, msg):
        self.status_label.setText("오류!")
        QMessageBox.critical(self, "오류", msg)
        self.worker = None

    def _clear_log(self):
        self.log_view.clear()

    def _log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_view.append(f"[{ts}] {msg}")
        # 자동 스크롤
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Helvetica Neue", 11))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
