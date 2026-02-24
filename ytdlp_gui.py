import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

# --- パス設定 ---
# PyInstaller でビルドした単体EXEでは __file__ が一時展開先を指すため、
# sys.frozen が True のときは sys.executable (EXE自身) の親を使う
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent
YTDLP_EXE = BASE_DIR / "yt-dlp.exe"
DOWNLOAD_DIR = BASE_DIR / "DownloadData"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# --- カラーテーマ ---
BG_DARK    = "#0f1117"
BG_PANEL   = "#1a1d27"
BG_INPUT   = "#12151f"
ACCENT     = "#7c6af7"
ACCENT2    = "#a78bfa"
SUCCESS    = "#4ade80"
ERROR      = "#f87171"
WARN       = "#fbbf24"
TEXT_MAIN  = "#e8e8f0"
TEXT_SUB   = "#8888aa"
BORDER     = "#2a2d40"
HOVER      = "#2a2d40"

FONT_MAIN  = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_MONO  = ("Consolas", 9)


class YtdlpGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("yt-dlp Downloader")
        self.geometry("900x680")
        self.minsize(700, 500)
        self.configure(bg=BG_DARK)

        # アイコン設定（あれば）
        ico_path = BASE_DIR / "ytdlp.ico"
        if ico_path.exists():
            try:
                self.iconbitmap(str(ico_path))
            except Exception:
                pass

        self.download_queue: list[str] = []
        self.is_downloading = False
        self.current_process: subprocess.Popen | None = None
        self.total_in_batch = 0
        self.done_in_batch = 0

        # _build_ui() で設定されるウィジェット（型宣言）
        self.ver_label: tk.Label
        self.url_text: tk.Text
        self.quality_var: tk.StringVar
        self.format_var: tk.StringVar
        self.audio_only_var: tk.BooleanVar
        self.audio_cb: tk.Checkbutton
        self.extra_opts_var: tk.StringVar
        self.dl_btn: tk.Button
        self.stop_btn: tk.Button
        self.clear_btn: tk.Button
        self.open_btn: tk.Button
        self.progress_label: tk.Label
        self.progress_bar: ttk.Progressbar
        self.log_text: scrolledtext.ScrolledText

        self._build_ui()
        self._apply_styles()

    # ──────────────────────────────────────────────
    # UI 構築
    # ──────────────────────────────────────────────
    def _build_ui(self):
        # タイトルバー
        title_bar = tk.Frame(self, bg=BG_PANEL, height=56)
        title_bar.pack(fill="x", side="top")
        title_bar.pack_propagate(False)

        tk.Label(title_bar, text="⬇  yt-dlp Downloader", bg=BG_PANEL,
                 fg=TEXT_MAIN, font=("Segoe UI", 13, "bold")).pack(side="left", padx=20, pady=12)

        # バージョン表示ラベル
        self.ver_label = tk.Label(title_bar, text="", bg=BG_PANEL, fg=TEXT_SUB, font=FONT_MAIN)
        self.ver_label.pack(side="right", padx=20)
        self._check_version()

        # メインコンテナ
        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        # ── URL入力エリア ──
        url_frame = tk.LabelFrame(main, text=" URL ", bg=BG_PANEL, fg=ACCENT2,
                                  font=FONT_BOLD, bd=1, relief="flat",
                                  highlightbackground=BORDER, highlightthickness=1)
        url_frame.pack(fill="x", pady=(0, 10))

        url_inner = tk.Frame(url_frame, bg=BG_PANEL)
        url_inner.pack(fill="x", padx=12, pady=10)

        tk.Label(url_inner, text="URLを入力（複数行OK）:", bg=BG_PANEL,
                 fg=TEXT_SUB, font=FONT_MAIN).pack(anchor="w")

        self.url_text = tk.Text(url_inner, height=5, bg=BG_INPUT, fg=TEXT_MAIN,
                                font=FONT_MONO, bd=0, relief="flat",
                                insertbackground=ACCENT2, selectbackground=ACCENT,
                                wrap="none")
        self.url_text.pack(fill="x", pady=(4, 0))

        # ── オプションエリア ──
        opt_frame = tk.LabelFrame(main, text=" オプション ", bg=BG_PANEL, fg=ACCENT2,
                                  font=FONT_BOLD, bd=1, relief="flat",
                                  highlightbackground=BORDER, highlightthickness=1)
        opt_frame.pack(fill="x", pady=(0, 10))

        opt_inner = tk.Frame(opt_frame, bg=BG_PANEL)
        opt_inner.pack(fill="x", padx=12, pady=8)

        # 行1: 品質 / フォーマット / 音声のみ
        row1 = tk.Frame(opt_inner, bg=BG_PANEL)
        row1.pack(fill="x", pady=2)

        tk.Label(row1, text="画質:", bg=BG_PANEL, fg=ACCENT2, font=FONT_MAIN).pack(side="left")
        self.quality_var = tk.StringVar(value="best")
        quality_cb = ttk.Combobox(row1, textvariable=self.quality_var, width=12,
                                  values=["best", "1080p", "720p", "480p", "360p", "worst"],
                                  state="readonly", font=FONT_MAIN)
        quality_cb.pack(side="left", padx=(4, 16))

        tk.Label(row1, text="フォーマット:", bg=BG_PANEL, fg=ACCENT2, font=FONT_MAIN).pack(side="left")
        self.format_var = tk.StringVar(value="mp4")
        format_cb = ttk.Combobox(row1, textvariable=self.format_var, width=8,
                                 values=["mp4", "mkv", "webm", "mp3", "m4a", "opus", "flac", "wav"],
                                 state="readonly", font=FONT_MAIN)
        format_cb.pack(side="left", padx=(4, 16))

        self.audio_only_var = tk.BooleanVar(value=False)
        self.audio_cb = tk.Checkbutton(row1, text="音声のみ", variable=self.audio_only_var,
                                       bg=BG_PANEL, fg=TEXT_MAIN, selectcolor=BG_INPUT,
                                       activebackground=BG_PANEL, activeforeground=TEXT_MAIN,
                                       font=FONT_MAIN, command=self._on_audio_toggle)
        self.audio_cb.pack(side="left", padx=(0, 16))



        # 行2: 追加オプション
        row2 = tk.Frame(opt_inner, bg=BG_PANEL)
        row2.pack(fill="x", pady=2)

        tk.Label(row2, text="追加オプション:", bg=BG_PANEL, fg=ACCENT2, font=FONT_MAIN).pack(side="left")
        self.extra_opts_var = tk.StringVar()
        tk.Entry(row2, textvariable=self.extra_opts_var, bg=BG_INPUT, fg=TEXT_MAIN,
                 font=FONT_MONO, bd=0, relief="flat", insertbackground=ACCENT2,
                 width=50).pack(side="left", padx=(4, 0))

        # ── ボタンエリア ──
        btn_frame = tk.Frame(main, bg=BG_DARK)
        btn_frame.pack(fill="x", pady=(0, 10))

        self.dl_btn = tk.Button(btn_frame, text="▶  ダウンロード開始",
                                command=self._start_download,
                                bg=ACCENT, fg="white", font=FONT_BOLD,
                                bd=0, relief="flat", padx=20, pady=8,
                                cursor="hand2", activebackground=ACCENT2,
                                activeforeground="white")
        self.dl_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = tk.Button(btn_frame, text="■  停止",
                                  command=self._stop_download,
                                  bg="#3a3d50", fg=TEXT_MAIN, font=FONT_BOLD,
                                  bd=0, relief="flat", padx=16, pady=8,
                                  cursor="hand2", activebackground=HOVER,
                                  activeforeground=TEXT_MAIN, state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 8))

        self.clear_btn = tk.Button(btn_frame, text="🗑  クリア",
                                   command=self._clear_log,
                                   bg="#3a3d50", fg=TEXT_MAIN, font=FONT_BOLD,
                                   bd=0, relief="flat", padx=16, pady=8,
                                   cursor="hand2", activebackground=HOVER,
                                   activeforeground=TEXT_MAIN)
        self.clear_btn.pack(side="left", padx=(0, 8))

        self.open_btn = tk.Button(btn_frame, text="📂  フォルダを開く",
                                  command=self._open_folder,
                                  bg="#3a3d50", fg=TEXT_MAIN, font=FONT_BOLD,
                                  bd=0, relief="flat", padx=16, pady=8,
                                  cursor="hand2", activebackground=HOVER,
                                  activeforeground=TEXT_MAIN)
        self.open_btn.pack(side="left")

        # ── プログレス ──
        prog_frame = tk.Frame(main, bg=BG_DARK)
        prog_frame.pack(fill="x", pady=(0, 8))

        self.progress_label = tk.Label(prog_frame, text="待機中", bg=BG_DARK,
                                       fg=TEXT_SUB, font=FONT_MAIN)
        self.progress_label.pack(side="left")

        self.progress_bar = ttk.Progressbar(prog_frame, mode="indeterminate", length=200)
        self.progress_bar.pack(side="right", padx=(8, 0))

        # ── ログエリア ──
        log_frame = tk.LabelFrame(main, text=" ログ ", bg=BG_PANEL, fg=ACCENT2,
                                  font=FONT_BOLD, bd=1, relief="flat",
                                  highlightbackground=BORDER, highlightthickness=1)
        log_frame.pack(fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame, bg=BG_INPUT, fg=TEXT_MAIN, font=FONT_MONO,
            bd=0, relief="flat", state="disabled", wrap="none"
        )
        self.log_text.pack(fill="both", expand=True, padx=2, pady=2)

        # ログのタグ設定
        self.log_text.tag_configure("info",    foreground=TEXT_MAIN)
        self.log_text.tag_configure("success", foreground=SUCCESS)
        self.log_text.tag_configure("error",   foreground=ERROR)
        self.log_text.tag_configure("warn",    foreground=WARN)
        self.log_text.tag_configure("accent",  foreground=ACCENT2)

    def _apply_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=BG_INPUT, background=BG_INPUT,
                        foreground=TEXT_MAIN, selectbackground=ACCENT,
                        borderwidth=0)
        style.configure("Horizontal.TProgressbar",
                        troughcolor=BG_PANEL, background=ACCENT,
                        borderwidth=0, thickness=6)

    # ──────────────────────────────────────────────
    # バージョン確認
    # ──────────────────────────────────────────────
    def _check_version(self):
        def run():
            try:
                result = subprocess.run(
                    [str(YTDLP_EXE), "--version"],
                    capture_output=True, text=True, encoding="utf-8"
                )
                ver = result.stdout.strip()
                self.after(0, lambda: self.ver_label.config(text=f"yt-dlp {ver}"))
            except Exception:
                self.after(0, lambda: self.ver_label.config(text="yt-dlp (version unknown)"))
        threading.Thread(target=run, daemon=True).start()

    # ──────────────────────────────────────────────
    # オプション切り替え
    # ──────────────────────────────────────────────
    def _on_audio_toggle(self):
        if self.audio_only_var.get():
            self.format_var.set("mp3")
        else:
            self.format_var.set("mp4")

    # ──────────────────────────────────────────────
    # ダウンロード開始
    # ──────────────────────────────────────────────
    def _start_download(self):
        raw = self.url_text.get("1.0", "end").strip()
        urls = [u.strip() for u in raw.splitlines() if u.strip()]
        if not urls:
            messagebox.showwarning("URLなし", "URLを1つ以上入力してください。")
            return

        self.download_queue = urls
        self.total_in_batch = len(urls)
        self.done_in_batch = 0
        self.is_downloading = True
        self._set_ui_downloading(True)
        self._log(f"== {len(urls)}件のダウンロードを開始 ==\n", "accent")
        threading.Thread(target=self._process_queue, daemon=True).start()

    def _process_queue(self):
        while self.download_queue and self.is_downloading:
            url = self.download_queue.pop(0)
            self.after(0, lambda u=url: self.progress_label.config(
                text=f"[{self.done_in_batch + 1}/{self.total_in_batch}] {u[:60]}..."
            ))
            self._download_one(url)
            self.done_in_batch += 1

        self.after(0, self._download_finished)

    def _download_one(self, url: str):
        self._log(f"\n▶ {url}\n", "accent")

        # 出力テンプレート: DownloadData/%(extractor)s/%(uploader)s/%(title)s.%(ext)s
        output_template = str(DOWNLOAD_DIR / "%(extractor)s" / "%(uploader|Unknown)s" / "%(title)s.%(ext)s")

        cmd = [str(YTDLP_EXE)]

        # 品質 / フォーマット
        quality = self.quality_var.get()
        fmt = self.format_var.get()
        audio_only = self.audio_only_var.get()

        if audio_only:
            # 音声のみ
            cmd += ["-x", "--audio-format", fmt]
        else:
            # 映像品質
            if quality == "best":
                if fmt in ("mp4", "mkv", "webm"):
                    cmd += ["-f", f"bestvideo[ext={fmt}]+bestaudio/best[ext={fmt}]/best",
                            "--merge-output-format", fmt]
                else:
                    cmd += ["-f", "bestvideo+bestaudio/best",
                            "--merge-output-format", fmt]
            elif quality in ("1080p", "720p", "480p", "360p"):
                h = quality.replace("p", "")
                cmd += ["-f", f"bestvideo[height<={h}]+bestaudio/best[height<={h}]/best",
                        "--merge-output-format", fmt]
            else:  # worst
                cmd += ["-f", "worstvideo+worstaudio/worst",
                        "--merge-output-format", fmt]

        # サムネイル（常時埋め込み）
        embed_supported = fmt in ("mp4", "m4a", "mp3", "ogg", "opus", "flac")
        if embed_supported:
            cmd += ["--embed-thumbnail"]
        else:
            # webm / mkv など埋め込み非対応 → 画像ファイルとして保存
            cmd += ["--write-thumbnail", "--convert-thumbnails", "jpg"]

        # 出力パス
        cmd += ["-o", output_template]

        # 進捗をログへ
        cmd += ["--newline"]

        # 追加オプション
        extra = self.extra_opts_var.get().strip()
        if extra:
            import shlex
            cmd += shlex.split(extra)

        cmd.append(url)

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"

        # CREATE_NO_WINDOW はWindows専用フラグ（他OSでは0を使用）
        no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        try:
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                creationflags=no_window
            )
            proc: subprocess.Popen[str] = self.current_process
            assert proc.stdout is not None

            for line in proc.stdout:
                line = line.rstrip("\n")
                if not line:
                    continue
                tag = self._classify_line(line)
                self._log(line + "\n", tag)

            proc.wait()
            retcode = proc.returncode

            if retcode == 0:
                self._log(f"✔ 完了: {url}\n", "success")
            else:
                self._log(f"✘ エラー(コード {retcode}): {url}\n", "error")

        except Exception as e:
            self._log(f"✘ 例外発生: {e}\n", "error")
        finally:
            self.current_process = None

    def _classify_line(self, line: str) -> str:
        l = line.lower()
        if any(k in l for k in ("[error]", "error:", "failed", "✘")):
            return "error"
        if any(k in l for k in ("[warning]", "warn")):
            return "warn"
        if any(k in l for k in ("[download]", "100%", "destination:", "merging")):
            return "success"
        return "info"

    def _download_finished(self):
        self.is_downloading = False
        self._set_ui_downloading(False)
        self._log("\n== すべてのダウンロードが完了しました ==\n", "success")
        self.progress_label.config(text="完了")

    # ──────────────────────────────────────────────
    # 停止
    # ──────────────────────────────────────────────
    def _stop_download(self):
        self.is_downloading = False
        self.download_queue.clear()
        if self.current_process:
            try:
                self.current_process.terminate()
            except Exception:
                pass
        self._log("\n⚠ ダウンロードを停止しました\n", "warn")
        self._set_ui_downloading(False)
        self.progress_label.config(text="停止")

    # ──────────────────────────────────────────────
    # UI 状態切り替え
    # ──────────────────────────────────────────────
    def _set_ui_downloading(self, active: bool):
        if active:
            self.dl_btn.config(state="disabled", bg="#444458")
            self.stop_btn.config(state="normal")
            self.progress_bar.start(12)
        else:
            self.dl_btn.config(state="normal", bg=ACCENT)
            self.stop_btn.config(state="disabled")
            self.progress_bar.stop()

    # ──────────────────────────────────────────────
    # ログ
    # ──────────────────────────────────────────────
    def _log(self, msg: str, tag: str = "info"):
        def _write():
            self.log_text.config(state="normal")
            self.log_text.insert("end", msg, tag)
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.after(0, _write)

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self.url_text.delete("1.0", "end")

    # ──────────────────────────────────────────────
    # フォルダを開く
    # ──────────────────────────────────────────────
    def _open_folder(self):
        os.startfile(str(DOWNLOAD_DIR))  # type: ignore[attr-defined]


if __name__ == "__main__":
    app = YtdlpGUI()
    app.mainloop()
