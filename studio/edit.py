#!/usr/bin/env python3
"""Assemble supplied clips into social-ready MP4 using offline FFmpeg (no AI API)."""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

RESOLUTIONS = {
    "vertical": (1080, 1920),
    "horizontal": (1920, 1080),
    "square": (1080, 1080),
}


def checked(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"FFmpeg process failed (exit {result.returncode}): {result.stderr[-1000:]}")
    return result.stdout


def probe(filepath):
    if not filepath.is_file():
        raise FileNotFoundError(str(filepath))
    raw = checked(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(filepath)])
    return json.loads(raw)


def media_info(filepath):
    value = probe(filepath)
    v = next((s for s in value["streams"] if s["codec_type"] == "video"), None)
    if not v:
        raise ValueError(f"No video stream found in {filepath}")
    duration = float(value.get("format", {}).get("duration", "0") or 0)
    if duration <= 0:
        raise ValueError(f"No positive video duration in {filepath}")
    return {"width": v["width"], "height": v["height"], "duration_seconds": duration,
            "video_codec": v.get("codec_name"),
            "audio": any(s["codec_type"] == "audio" for s in value["streams"])}


def burn_subtitles_filter(filename):
    # Path escapes for FFmpeg's filtergraph. Keep files under temporary dir with no spaces.
    if not filename.is_file():
        raise FileNotFoundError(filename)
    if '\n' in str(filename) or "'" in str(filename) or ':' in str(filename):
        raise ValueError("Caption path must not contain apostrophes, colons or newlines")
    return f"subtitles={filename.as_posix()}:force_style='FontName=DejaVu Sans,Alignment=2,FontSize=20,Outline=2,MarginV=180'"


def assemble(clips, output, layout="vertical", voice=None, music=None, subtitles=None, width=None, height=None):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg and ffprobe must be installed")
    if not clips:
        raise ValueError("At least one video clip is required")
    w, h = RESOLUTIONS[layout]
    w, h = width or w, height or h
    if w < 100 or h < 100 or w % 2 or h % 2:
        raise ValueError("Width/height must be >=100 and even")
    for f in clips:
        media_info(f)
    for p in (voice, music):
        if p and not p.is_file():
            raise FileNotFoundError(p)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ai-studio-") as d:
        tmp = Path(d)
        clean = []
        for n, original in enumerate(clips):
            target = tmp / f"shot{n:03}.mp4"
            filter_expr = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps=30,format=yuv420p,setsar=1"
            checked(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(original),
                     "-vf", filter_expr, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                     "-movflags", "+faststart", str(target)])
            clean.append(target)
        concat_manifest = tmp / "join.txt"
        concat_manifest.write_text("".join(f"file '{p.as_posix()}'\n" for p in clean), encoding="utf-8")
        joined = tmp / "joined.mp4"
        checked(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
                 "-i", str(concat_manifest), "-c", "copy", str(joined)])
        duration = media_info(joined)["duration_seconds"]
        command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(joined)]
        audio_idxs = []
        for p in (voice, music):
            if p is not None:
                audio_idxs.append(len(audio_idxs) + 1)
                command += ["-i", str(p)]
        if not audio_idxs:
            command += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
            audio_map = ["-map", "0:v:0", "-map", "1:a:0"]
        elif len(audio_idxs) == 1:
            command += ["-filter_complex", f"[1:a]volume={'0.18' if music and not voice else '1.0'},apad[a]",
                        "-map", "0:v:0", "-map", "[a]"]
            audio_map = []
        else:
            command += ["-filter_complex", "[1:a]volume=1,apad[voice];[2:a]volume=0.12,apad[music];"
                        "[voice][music]amix=inputs=2:duration=longest:normalize=0[a]",
                        "-map", "0:v:0", "-map", "[a]"]
            audio_map = []
        command += audio_map
        if subtitles:
            # Copy SRT to predictable local path; libass avoids source path escaping.
            cap = tmp / "captions.srt"
            cap.write_bytes(subtitles.read_bytes())
            command += ["-vf", burn_subtitles_filter(cap)]
        command += ["-t", f"{duration:.3f}", "-c:v", "libx264" if subtitles else "copy",
                    "-preset", "veryfast"] if subtitles else ["-t", f"{duration:.3f}", "-c:v", "copy"]
        command += ["-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(output)]
        checked(command)
    return media_info(output)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clips", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--layout", choices=sorted(RESOLUTIONS), default="vertical")
    ap.add_argument("--voice", type=Path)
    ap.add_argument("--music", type=Path)
    ap.add_argument("--subtitles", type=Path, help="Timed SRT transcript made/reviewed by you")
    ap.add_argument("--width", type=int, help="Testing only: even output width")
    ap.add_argument("--height", type=int, help="Testing only: even output height")
    args = ap.parse_args()
    print(json.dumps(assemble(args.clips, args.out, args.layout, args.voice, args.music,
                              args.subtitles, args.width, args.height), indent=2))

if __name__ == "__main__":
    main()
