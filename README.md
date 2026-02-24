# yt-dlp GUI Downloader


---

## 概要

[yt-dlp](https://github.com/yt-dlp/yt-dlp) のシンプルな Windows 向け GUI ラッパーです。  
YouTube・ニコニコ動画など数千のサイトから動画・音声を手軽にダウンロードできます。

## スクリーンショット

> GUI を起動すると以下のような画面が表示されます。

- URL を複数行まとめて貼り付け可能
- 画質・フォーマット・音声のみ などをドロップダウンで選択
- リアルタイムのダウンロードログ表示

## 動作環境

| 項目 | 要件 |
|------|------|
| OS | Windows 10 / 11 |
| Python | 3.10 以上（スクリプト版のみ） |
| yt-dlp | `yt-dlp.exe` を同フォルダに配置 |

> **EXE 版**（`dist/ytdlp_gui.exe`）は Python 不要でそのまま実行できます。

## ファイル構成

```
ytdlp-gui/
├── ytdlp_gui.py        # メインスクリプト
├── ytdlp_gui.spec      # PyInstaller ビルド設定
├── start_gui.bat       # スクリプト版の起動用バッチ
├── yt-dlp.exe          # yt-dlp 本体（別途配置）
├── DownloadData/       # ダウンロード先フォルダ（自動生成）
│   └── <サイト名>/
│       └── <投稿者名>/
│           └── <ファイル名>
└── dist/
    └── ytdlp_gui.exe   # ビルド済み実行ファイル
```

## 使い方

### EXE 版（推奨）

1. `dist/ytdlp_gui.exe` と `yt-dlp.exe` を同じフォルダに置く
2. `ytdlp_gui.exe` をダブルクリックして起動
3. URL 欄に URL を貼り付け（複数行一括入力可）
4. 画質・フォーマットを選択して **▶ ダウンロード開始** をクリック

### スクリプト版

```bash
# 依存ライブラリは標準ライブラリのみ（追加インストール不要）
python ytdlp_gui.py
# または
start_gui.bat
```

## オプション

| オプション | 説明 |
|-----------|------|
| 画質 | `best` / `1080p` / `720p` / `480p` / `360p` / `worst` |
| フォーマット | `mp4` / `mkv` / `webm` / `mp3` / `m4a` / `opus` / `flac` / `wav` |
| 音声のみ | チェックで音声抽出モードに切り替え（`-x` オプション相当） |
| 追加オプション | yt-dlp の任意のコマンドラインオプションをそのまま入力可 |

ダウンロードファイルは自動的に  
`DownloadData/<サイト名>/<投稿者名>/<タイトル>.<拡張子>`  
に保存されます。サムネイルは対応フォーマット（mp4・mp3 など）に自動埋め込みされます。

## ライセンス

本プロジェクトは MIT License のもとで公開されています。

本配布物には yt-dlp が含まれています。
yt-dlp は Unlicense のもとでライセンスされています。
そのライセンス全文は `yt-dlp_LICENSE.txt` として同梱されています。

### 法的注意事項

本ソフトウェアは、ユーザーが合法的に取得可能なコンテンツのダウンロードを目的としたツールです。
各サービスの利用規約、関連法令、著作権法等を遵守して使用してください。

本ソフトウェアの使用によって発生したいかなる損害、法的責任についても、開発者は一切の責任を負いません。

違法行為、公序良俗に反する目的での使用を禁止します。

---

# yt-dlp GUI Downloader (English)

## Overview

A simple Windows GUI wrapper for [yt-dlp](https://github.com/yt-dlp/yt-dlp).  
Easily download videos and audio from YouTube, Niconico, and thousands of other sites.

## Features

- Paste multiple URLs at once
- Select quality, format, and audio-only mode from dropdowns
- Real-time download log with color-coded output

## Requirements

| Item | Requirement |
|------|-------------|
| OS | Windows 10 / 11 |
| Python | 3.10+ (script version only) |
| yt-dlp | Place `yt-dlp.exe` in the same folder |

> The **EXE version** (`dist/ytdlp_gui.exe`) runs without Python installed.

## File Structure

```
ytdlp-gui/
├── ytdlp_gui.py        # Main script
├── ytdlp_gui.spec      # PyInstaller build config
├── start_gui.bat       # Batch launcher for script version
├── yt-dlp.exe          # yt-dlp binary (place here manually)
├── DownloadData/       # Download output folder (auto-created)
│   └── <site>/
│       └── <uploader>/
│           └── <filename>
└── dist/
    └── ytdlp_gui.exe   # Built executable
```

## Usage

### EXE Version (Recommended)

1. Place `dist/ytdlp_gui.exe` and `yt-dlp.exe` in the same folder
2. Double-click `ytdlp_gui.exe` to launch
3. Paste URL(s) into the URL box (multiple lines supported)
4. Choose quality and format, then click **▶ Start Download**

### Script Version

```bash
# No extra dependencies required (standard library only)
python ytdlp_gui.py
# or
start_gui.bat
```

## Options

| Option | Description |
|--------|-------------|
| Quality | `best` / `1080p` / `720p` / `480p` / `360p` / `worst` |
| Format | `mp4` / `mkv` / `webm` / `mp3` / `m4a` / `opus` / `flac` / `wav` |
| Audio Only | Extracts audio only (equivalent to the `-x` flag) |
| Extra Options | Pass any yt-dlp command-line flags directly |

Downloads are saved to:  
`DownloadData/<site>/<uploader>/<title>.<ext>`  
Thumbnails are automatically embedded into supported formats (mp4, mp3, etc.).

## License

This project is released under the MIT License.

This distribution includes yt-dlp.  
yt-dlp is licensed under the Unlicense.  
The full license text is included as `yt-dlp_LICENSE.txt`.

### Legal Notice

This software is provided as a graphical interface for downloading content that users are legally permitted to access.

Users are solely responsible for ensuring compliance with:

Applicable laws and regulations

Copyright laws

Terms of service of respective platforms

The developer assumes no liability for any misuse of this software.

Use of this software for illegal activities or violation of platform policies is strictly prohibited.