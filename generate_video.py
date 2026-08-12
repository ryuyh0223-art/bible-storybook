import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path


# ===== 쉽게 조절할 수 있는 영상 설정 =====
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
VIDEO_CRF = 20
VIDEO_PRESET = "medium"

TRANSITION_DURATION = 0.25
POST_SPEECH_HOLD = 0.05
TRANSITION_AUDIO_LEAD = 0.15
VIDEO_FADE_IN_SECONDS = 0.50
VIDEO_FADE_OUT_SECONDS = 0.75

TITLE_SPEECH_START = 0.50
LAST_SCENE_EXTRA_SECONDS = 1.50

SILENCE_TRIM_ENABLED = True
SILENCE_THRESHOLD_DB = -50.0
SILENCE_START_MIN_DURATION = 0.05
SILENCE_START_KEEP = 0.05
SILENCE_END_MIN_DURATION = 0.08
SILENCE_END_KEEP = 0.10
EDGE_SILENCE_MEASURE_MIN = 0.01
FINAL_DURATION_TOLERANCE_FRAMES = 2
SCENE_FRAME_SSIM_MINIMUM = 0.82

# 자연스러운 나레이션 보정을 위한 de-click / 노이즈 제거 / EQ / 치찰음 / 음량 설정
DECLICK_ENABLED = True
DECLICK_WINDOW_MS = 55.0
DECLICK_OVERLAP_PERCENT = 75.0
DECLICK_AR_ORDER = 2.0
DECLICK_THRESHOLD = 3.0
DECLICK_BURST_FUSION = 1.0
NOISE_REDUCTION_ENABLED = True
NOISE_REDUCTION_STRENGTH = 8.0
NOISE_REDUCTION_FLOOR_DB = -50.0
NOISE_REDUCTION_SMOOTHING = 5
VOICE_EQ_LOW_FREQUENCY = 120.0
VOICE_EQ_LOW_GAIN_DB = -1.75
VOICE_EQ_LOW_Q = 0.80
VOICE_EQ_MID_FREQUENCY = 220.0
VOICE_EQ_MID_GAIN_DB = -1.25
VOICE_EQ_MID_Q = 0.90
DEESSER_INTENSITY = 0.15
DEESSER_MAX_REDUCTION = 0.50
DEESSER_FREQUENCY = 0.50
LOUDNESS_TARGET_I = -16.0
LOUDNESS_TARGET_LRA = 11.0
LOUDNESS_TARGET_TP = -1.5
NARRATION_LIMITER_PEAK = 0.95
NARRATION_MICRO_FADE_SECONDS = 0.015
FINAL_LIMITER_PEAK = 0.95

BGM_VOLUME = 0.08
BGM_FADE_OUT_SECONDS = 1.50
AUDIO_SAMPLE_RATE = 48000
AUDIO_BITRATE = "192k"

# ASS 자막 스타일 설정
WINDOWS_SUBTITLE_FONT_NAME = "Malgun Gothic"
MACOS_SUBTITLE_FONT_NAME = "Apple SD Gothic Neo"
OTHER_SUBTITLE_FONT_NAME = "Noto Sans CJK KR"
SUBTITLE_FONT_SIZE = 54
SUBTITLE_MARGIN_LEFT = 120
SUBTITLE_MARGIN_RIGHT = 120
SUBTITLE_MARGIN_BOTTOM = 70
SUBTITLE_OUTLINE = 2
SUBTITLE_PRIMARY_COLOR = "&H00FFFFFF"
SUBTITLE_OUTLINE_COLOR = "&H80000000"
SUBTITLE_BACKGROUND_COLOR = "&H70000000"


ROOT = Path(__file__).resolve().parent
VIDEO_WORK_ROOT = ROOT / "video-work"
STORY_FOLDER_PATTERN = re.compile(
    r"^bible-storybook-([a-z0-9]+(?:-[a-z0-9]+)*)$"
)
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".m4a"}
REQUIRED_FFMPEG_FILTERS = {
    "adeclick",
    "afftdn",
    "alimiter",
    "deesser",
    "equalizer",
    "loudnorm",
    "ssim",
    "subtitles",
    "xfade",
}


class VideoGenerationError(Exception):
    """사용자가 입력 파일을 고쳐야 하는 영상 생성 오류."""


def run_process(command, description, timeout=None):
    try:
        result = subprocess.run(
            [str(value) for value in command],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise VideoGenerationError(f"{description} 실행에 실패했습니다: {error}") from error

    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        raise VideoGenerationError(
            f"{description} 실행에 실패했습니다."
            + (f"\n{details}" if details else "")
        )
    return result


def tool_is_usable(path):
    if not path:
        return False
    try:
        result = subprocess.run(
            [str(path), "-version"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def find_ffmpeg_tools():
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if tool_is_usable(ffmpeg) and tool_is_usable(ffprobe):
        return Path(ffmpeg), Path(ffprobe)

    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            packages_root = (
                Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
            )
        else:
            packages_root = (
                Path.home()
                / "AppData"
                / "Local"
                / "Microsoft"
                / "WinGet"
                / "Packages"
            )

        if packages_root.is_dir():
            package_dirs = sorted(
                packages_root.glob("Gyan.FFmpeg_*"),
                key=lambda path: path.name.casefold(),
                reverse=True,
            )
            for package_dir in package_dirs:
                for ffmpeg_path in package_dir.rglob("ffmpeg.exe"):
                    ffprobe_path = ffmpeg_path.with_name("ffprobe.exe")
                    if (
                        ffprobe_path.is_file()
                        and tool_is_usable(ffmpeg_path)
                        and tool_is_usable(ffprobe_path)
                    ):
                        return ffmpeg_path, ffprobe_path
        guidance = (
            "새 명령창에서 ffmpeg -version과 ffprobe -version을 확인하거나 "
            "WinGet Gyan.FFmpeg 설치 상태를 확인하세요."
        )
    elif sys.platform == "darwin":
        for bin_dir in (Path("/opt/homebrew/bin"), Path("/usr/local/bin")):
            ffmpeg_path = bin_dir / "ffmpeg"
            ffprobe_path = bin_dir / "ffprobe"
            if tool_is_usable(ffmpeg_path) and tool_is_usable(ffprobe_path):
                return ffmpeg_path, ffprobe_path
        guidance = (
            "Homebrew에서 'brew install ffmpeg'를 실행한 뒤 새 Terminal에서 "
            "ffmpeg -version과 ffprobe -version을 확인하세요."
        )
    else:
        guidance = (
            "ffmpeg와 ffprobe를 설치하고 두 실행 파일이 PATH에 포함되었는지 "
            "확인하세요."
        )

    raise VideoGenerationError(f"ffmpeg 또는 ffprobe를 찾을 수 없습니다. {guidance}")


def get_subtitle_font_name():
    configured = os.environ.get("HAPPYPANG_SUBTITLE_FONT", "").strip()
    if configured:
        return configured
    if sys.platform == "win32":
        return WINDOWS_SUBTITLE_FONT_NAME
    if sys.platform == "darwin":
        return MACOS_SUBTITLE_FONT_NAME
    return OTHER_SUBTITLE_FONT_NAME


def verify_ffmpeg_filters(ffmpeg):
    result = run_process(
        [ffmpeg, "-hide_banner", "-filters"],
        "FFmpeg 필터 지원 검사",
        timeout=30,
    )
    available = set()
    for line in result.stdout.splitlines():
        match = re.match(r"^\s*[.A-Z|]{2,4}\s+([a-zA-Z0-9_]+)\s", line)
        if match:
            available.add(match.group(1))
    missing = sorted(REQUIRED_FFMPEG_FILTERS - available)
    if missing:
        raise VideoGenerationError(
            "설치된 FFmpeg에 영상 자동화 필터가 부족합니다: "
            + ", ".join(missing)
            + ". 자막을 포함한 full FFmpeg 빌드를 설치하세요."
        )


def require_string(container, field_name, source_path):
    value = container.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise VideoGenerationError(
            f"{source_path}: '{field_name}'은 비어 있지 않은 문자열이어야 합니다."
        )
    return value.strip()


def resolve_story_folder(folder_argument):
    if not folder_argument or Path(folder_argument).name != folder_argument:
        raise VideoGenerationError(
            "동화 폴더명만 입력하세요. 예: bible-storybook-god-is-near"
        )
    match = STORY_FOLDER_PATTERN.fullmatch(folder_argument)
    if not match:
        raise VideoGenerationError(
            "동화 폴더명은 bible-storybook-<slug> 형식이어야 합니다."
        )
    story_dir = ROOT / folder_argument
    if not story_dir.is_dir():
        raise VideoGenerationError(f"동화 폴더가 없습니다: {folder_argument}")
    return story_dir, match.group(1)


def load_video_story(story_dir, folder_slug):
    story_json_path = story_dir / "story.json"
    if not story_json_path.is_file():
        raise VideoGenerationError(f"story.json이 없습니다: {story_json_path}")
    try:
        data = json.loads(story_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise VideoGenerationError(
            f"story.json 문법 오류: {error.lineno}행 {error.colno}열 - {error.msg}"
        ) from error
    except UnicodeDecodeError as error:
        raise VideoGenerationError(
            "story.json을 UTF-8 텍스트로 저장해야 합니다."
        ) from error
    except OSError as error:
        raise VideoGenerationError(f"story.json을 읽을 수 없습니다: {error}") from error

    if not isinstance(data, dict):
        raise VideoGenerationError("story.json의 최상위 값은 JSON 객체여야 합니다.")

    slug = require_string(data, "slug", story_json_path)
    if slug != folder_slug:
        raise VideoGenerationError(
            f"story.json의 slug와 폴더명이 다릅니다: {slug} != {folder_slug}"
        )
    title = require_string(data, "title", story_json_path)
    cover_image = require_string(data, "cover_image", story_json_path)
    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise VideoGenerationError("story.json의 scenes에는 장면이 하나 이상 있어야 합니다.")

    scene_images = []
    scene_paragraphs = []
    for index, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            raise VideoGenerationError(f"scenes[{index}]은 JSON 객체여야 합니다.")
        scene_images.append(require_string(scene, "image", story_json_path))
        paragraphs = scene.get("paragraphs")
        if not isinstance(paragraphs, list) or not paragraphs:
            raise VideoGenerationError(
                f"scenes[{index}].paragraphs에는 문장이 하나 이상 있어야 합니다."
            )
        checked_paragraphs = []
        for paragraph_index, paragraph in enumerate(paragraphs, start=1):
            if not isinstance(paragraph, str) or not paragraph.strip():
                raise VideoGenerationError(
                    f"scenes[{index}].paragraphs[{paragraph_index}]은 "
                    "비어 있지 않은 문자열이어야 합니다."
                )
            checked_paragraphs.append(paragraph.strip())
        scene_paragraphs.append(checked_paragraphs)

    return {
        "slug": slug,
        "title": title,
        "cover_image": cover_image,
        "scene_images": scene_images,
        "scene_paragraphs": scene_paragraphs,
    }


def find_exact_file(directory, filename, field_name, extensions):
    filename_path = Path(filename)
    if filename_path.name != filename or filename in {".", ".."}:
        raise VideoGenerationError(
            f"'{field_name}'에는 파일명만 입력해야 합니다: {filename}"
        )
    if filename_path.suffix.lower() not in extensions:
        raise VideoGenerationError(f"지원하지 않는 파일 형식입니다: {filename}")

    actual_files = {item.name: item for item in directory.iterdir() if item.is_file()}
    if filename in actual_files:
        return actual_files[filename]
    case_matches = [
        name for name in actual_files if name.casefold() == filename.casefold()
    ]
    if case_matches:
        raise VideoGenerationError(
            f"파일명의 대소문자가 다릅니다. 요청='{filename}', 실제='{case_matches[0]}'"
        )
    raise VideoGenerationError(f"필수 파일이 없습니다: {directory / filename}")


def validate_inputs(folder_name, story_dir, story):
    images_dir = story_dir / "assets" / "images"
    if not images_dir.is_dir():
        raise VideoGenerationError(f"이미지 폴더가 없습니다: {images_dir}")

    image_names = [story["cover_image"], *story["scene_images"]]
    image_paths = [
        find_exact_file(
            images_dir,
            image_name,
            "cover_image" if index == 0 else f"scenes[{index}].image",
            SUPPORTED_IMAGE_EXTENSIONS,
        )
        for index, image_name in enumerate(image_names)
    ]

    work_dir = VIDEO_WORK_ROOT / folder_name
    audio_dir = work_dir / "audio"
    if not audio_dir.is_dir():
        raise VideoGenerationError(f"녹음 폴더가 없습니다: {audio_dir}")

    expected_audio_stems = ["title"] + [
        f"scene_{index:02d}"
        for index in range(1, len(story["scene_images"]) + 1)
    ]
    supported_audio_files = [
        item for item in audio_dir.iterdir()
        if item.is_file() and item.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
    ]
    expected_audio_set = set(expected_audio_stems)
    unexpected_audio = sorted(
        item.name for item in supported_audio_files
        if item.stem not in expected_audio_set
    )
    if unexpected_audio:
        raise VideoGenerationError(
            "장면 수와 맞지 않는 WAV/M4A 파일이 있습니다: "
            + ", ".join(unexpected_audio)
        )

    audio_paths = []
    missing_audio = []
    duplicate_audio = []
    for stem in expected_audio_stems:
        matches = [item for item in supported_audio_files if item.stem == stem]
        if not matches:
            missing_audio.append(f"{stem}.wav 또는 {stem}.m4a")
        elif len(matches) > 1:
            duplicate_audio.append(", ".join(sorted(item.name for item in matches)))
        else:
            audio_paths.append(matches[0])

    if missing_audio:
        raise VideoGenerationError(
            "필수 녹음 파일이 없습니다: " + ", ".join(missing_audio)
        )
    if duplicate_audio:
        raise VideoGenerationError(
            "같은 녹음의 WAV와 M4A가 동시에 있습니다. 하나만 남겨 주세요: "
            + "; ".join(duplicate_audio)
        )

    bgm_path = VIDEO_WORK_ROOT / "bgm.mp3"
    if not bgm_path.is_file():
        raise VideoGenerationError(f"BGM 파일이 없습니다: {bgm_path}")

    return {
        "work_dir": work_dir,
        "image_paths": image_paths,
        "audio_paths": audio_paths,
        "bgm_path": bgm_path,
    }


def probe_duration(ffprobe, media_path, label):
    result = run_process(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            media_path,
        ],
        f"{label} 길이 검사",
        timeout=30,
    )
    try:
        duration = float(json.loads(result.stdout)["format"]["duration"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise VideoGenerationError(f"{label}의 실제 길이를 확인할 수 없습니다.") from error
    if not math.isfinite(duration) or duration <= 0:
        raise VideoGenerationError(f"{label}의 길이가 올바르지 않습니다: {duration}")
    return duration


def render_pcm_audio(ffmpeg, input_path, output_path, audio_filter, description):
    run_process(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-y",
            "-i",
            input_path,
            "-map",
            "0:a:0",
            "-af",
            audio_filter,
            "-c:a",
            "pcm_s24le",
            "-ar",
            str(AUDIO_SAMPLE_RATE),
            "-ac",
            "2",
            output_path,
        ],
        description,
        timeout=180,
    )


def measure_edge_silence(ffmpeg, audio_path, duration):
    result = run_process(
        [
            ffmpeg,
            "-hide_banner",
            "-nostats",
            "-i",
            audio_path,
            "-af",
            (
                f"silencedetect=noise={SILENCE_THRESHOLD_DB:.3f}dB:"
                f"d={EDGE_SILENCE_MEASURE_MIN:.6f}"
            ),
            "-f",
            "null",
            os.devnull,
        ],
        f"음성 경계 무음 검사 ({audio_path.name})",
        timeout=60,
    )
    intervals = []
    active_start = None
    for line in result.stderr.splitlines():
        start_match = re.search(r"silence_start:\s*([0-9.]+)", line)
        if start_match:
            active_start = float(start_match.group(1))
            continue
        end_match = re.search(r"silence_end:\s*([0-9.]+)", line)
        if end_match and active_start is not None:
            intervals.append((active_start, float(end_match.group(1))))
            active_start = None
    leading = 0.0
    trailing = 0.0
    if intervals and intervals[0][0] <= 0.002:
        leading = max(0.0, intervals[0][1] - intervals[0][0])
    if intervals and intervals[-1][1] >= duration - 0.03:
        trailing = max(0.0, intervals[-1][1] - intervals[-1][0])
    return min(leading, duration), min(trailing, duration - leading)


def preprocess_audio_files(ffmpeg, ffprobe, audio_paths, temp_dir):
    processed = []
    audio_temp_dir = temp_dir / "processed-audio"
    audio_temp_dir.mkdir()

    for index, source_path in enumerate(audio_paths):
        label = "title" if index == 0 else f"scene_{index:02d}"
        decoded_path = audio_temp_dir / f"{label}-decoded.wav"
        trimmed_path = audio_temp_dir / f"{label}-trimmed.wav"
        processed_path = audio_temp_dir / f"{label}-processed.wav"

        original_duration = probe_duration(ffprobe, source_path, f"{label} 원본")
        render_pcm_audio(
            ffmpeg,
            source_path,
            decoded_path,
            f"aresample={AUDIO_SAMPLE_RATE},aformat=channel_layouts=stereo",
            f"{label} 디코딩",
        )
        decoded_duration = probe_duration(ffprobe, decoded_path, f"{label} 디코딩")
        original_leading_silence, original_trailing_silence = measure_edge_silence(
            ffmpeg, decoded_path, decoded_duration
        )

        if SILENCE_TRIM_ENABLED:
            removed_start = (
                max(0.0, original_leading_silence - SILENCE_START_KEEP)
                if original_leading_silence >= SILENCE_START_MIN_DURATION
                else 0.0
            )
            removed_end = (
                max(0.0, original_trailing_silence - SILENCE_END_KEEP)
                if original_trailing_silence >= SILENCE_END_MIN_DURATION
                else 0.0
            )
            trim_end = decoded_duration - removed_end
            render_pcm_audio(
                ffmpeg,
                decoded_path,
                trimmed_path,
                (
                    f"atrim=start={removed_start:.6f}:end={trim_end:.6f},"
                    "asetpts=PTS-STARTPTS"
                ),
                f"{label} 경계 무음 정리",
            )
            trimmed_duration = probe_duration(
                ffprobe, trimmed_path, f"{label} 무음 정리"
            )
        else:
            trimmed_path = decoded_path
            trimmed_duration = decoded_duration
            removed_start = 0.0
            removed_end = 0.0

        filters = []
        if DECLICK_ENABLED:
            filters.append(
                f"adeclick=w={DECLICK_WINDOW_MS:.3f}:"
                f"o={DECLICK_OVERLAP_PERCENT:.3f}:"
                f"a={DECLICK_AR_ORDER:.3f}:"
                f"t={DECLICK_THRESHOLD:.3f}:"
                f"b={DECLICK_BURST_FUSION:.3f}:m=a"
            )
        if NOISE_REDUCTION_ENABLED:
            filters.append(
                f"afftdn=nr={NOISE_REDUCTION_STRENGTH:.3f}:"
                f"nf={NOISE_REDUCTION_FLOOR_DB:.3f}:tn=1:"
                f"gs={NOISE_REDUCTION_SMOOTHING}"
            )
        filters.extend(
            [
                f"equalizer=f={VOICE_EQ_LOW_FREQUENCY:.3f}:t=q:"
                f"w={VOICE_EQ_LOW_Q:.3f}:g={VOICE_EQ_LOW_GAIN_DB:.3f}",
                f"equalizer=f={VOICE_EQ_MID_FREQUENCY:.3f}:t=q:"
                f"w={VOICE_EQ_MID_Q:.3f}:g={VOICE_EQ_MID_GAIN_DB:.3f}",
                f"deesser=i={DEESSER_INTENSITY:.3f}:"
                f"m={DEESSER_MAX_REDUCTION:.3f}:"
                f"f={DEESSER_FREQUENCY:.3f}:s=o",
                f"loudnorm=I={LOUDNESS_TARGET_I:.3f}:"
                f"LRA={LOUDNESS_TARGET_LRA:.3f}:TP={LOUDNESS_TARGET_TP:.3f}",
                f"alimiter=limit={NARRATION_LIMITER_PEAK:.4f}:"
                "level=false:latency=true",
            ]
        )
        micro_fade = min(NARRATION_MICRO_FADE_SECONDS, trimmed_duration / 2)
        if micro_fade > 0:
            filters.extend(
                [
                    f"afade=t=in:st=0:d={micro_fade:.6f}",
                    "areverse",
                    f"afade=t=in:st=0:d={micro_fade:.6f}",
                    "areverse",
                ]
            )
        filters.extend(
            [
                f"aresample={AUDIO_SAMPLE_RATE}",
                "aformat=sample_fmts=fltp:channel_layouts=stereo",
            ]
        )
        render_pcm_audio(
            ffmpeg,
            trimmed_path,
            processed_path,
            ",".join(filters),
            f"{label} 음성 후처리",
        )
        processed_duration = probe_duration(
            ffprobe, processed_path, f"{label} 후처리"
        )
        leading_silence, trailing_silence = measure_edge_silence(
            ffmpeg, processed_path, processed_duration
        )
        audible_duration = processed_duration - leading_silence - trailing_silence
        if audible_duration <= 0.05:
            raise VideoGenerationError(f"{label}에서 실제 발화를 찾을 수 없습니다.")
        processed.append(
            {
                "label": label,
                "source_path": source_path,
                "processed_path": processed_path,
                "original_duration": original_duration,
                "decoded_duration": decoded_duration,
                "original_leading_silence": original_leading_silence,
                "original_trailing_silence": original_trailing_silence,
                "trimmed_duration": trimmed_duration,
                "removed_start": removed_start,
                "removed_end": removed_end,
                "processed_duration": processed_duration,
                "leading_silence": leading_silence,
                "trailing_silence": trailing_silence,
                "audible_duration": audible_duration,
            }
        )
    return processed


def build_master_timeline(processed_audio):
    timeline = []
    speech_gap = POST_SPEECH_HOLD + TRANSITION_AUDIO_LEAD
    for index, audio in enumerate(processed_audio):
        entry = dict(audio)
        if index == 0:
            speech_start = TITLE_SPEECH_START
            clip_start = max(0.0, speech_start - audio["leading_silence"])
            speech_start = clip_start + audio["leading_silence"]
            visual_start = 0.0
            visual_full_start = 0.0
        else:
            previous = timeline[-1]
            transition_start = previous["speech_end"] + POST_SPEECH_HOLD
            transition_end = transition_start + TRANSITION_DURATION
            previous["transition_start"] = transition_start
            previous["transition_end"] = transition_end
            speech_start = transition_start + TRANSITION_AUDIO_LEAD
            clip_start = speech_start - audio["leading_silence"]
            visual_start = transition_start
            visual_full_start = transition_end
            if clip_start + 0.001 < previous["clip_end"]:
                raise VideoGenerationError(
                    f"{previous['label']}와 {audio['label']}의 처리된 음성이 겹칩니다. "
                    "무음 유지값 또는 발화 간격을 조정하세요."
                )
            actual_gap = speech_start - previous["speech_end"]
            if abs(actual_gap - speech_gap) > 0.002:
                raise VideoGenerationError("master timeline 발화 간격 계산이 일치하지 않습니다.")

        speech_end = (
            clip_start + audio["processed_duration"] - audio["trailing_silence"]
        )
        clip_end = clip_start + audio["processed_duration"]
        entry.update(
            {
                "clip_start": clip_start,
                "clip_end": clip_end,
                "speech_start": speech_start,
                "speech_end": speech_end,
                "visual_start": visual_start,
                "visual_full_start": visual_full_start,
                "transition_start": None,
                "transition_end": None,
            }
        )
        timeline.append(entry)

    master_duration = timeline[-1]["clip_end"] + LAST_SCENE_EXTRA_SECONDS
    for index, entry in enumerate(timeline):
        if index < len(timeline) - 1:
            entry["visual_end"] = entry["transition_end"]
        else:
            entry["visual_end"] = master_duration
    return timeline, master_duration


def render_visual_segment(ffmpeg, image_path, duration, output_path):
    video_filter = (
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:"
        "force_original_aspect_ratio=decrease:force_divisible_by=2,"
        f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"setsar=1,fps={VIDEO_FPS},format=yuv420p"
    )
    run_process(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-y",
            "-loop",
            "1",
            "-framerate",
            str(VIDEO_FPS),
            "-i",
            image_path,
            "-vf",
            video_filter,
            "-t",
            f"{duration:.6f}",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            VIDEO_PRESET,
            "-crf",
            str(VIDEO_CRF),
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(VIDEO_FPS),
            output_path,
        ],
        f"장면 영상 생성 ({image_path.name})",
    )


def combine_visual_segments(ffmpeg, segment_paths, timeline, master_duration, temp_dir):
    visual_path = temp_dir / "visual.mp4"
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-y",
    ]
    for segment_path in segment_paths:
        command.extend(["-i", segment_path])

    filters = []
    video_labels = []
    for index in range(len(timeline)):
        video_label = f"v{index}in"
        filters.append(
            f"[{index}:v]settb=AVTB,setpts=PTS-STARTPTS[{video_label}]"
        )
        video_labels.append(video_label)

    current_video = video_labels[0]
    for index in range(1, len(video_labels)):
        output_label = f"vx{index}"
        filters.append(
            f"[{current_video}][{video_labels[index]}]"
            f"xfade=transition=fade:duration={TRANSITION_DURATION:.6f}:"
            f"offset={timeline[index]['visual_start']:.6f}[{output_label}]"
        )
        current_video = output_label
    filters.append(
        f"[{current_video}]trim=duration={master_duration:.6f},"
        "setpts=PTS-STARTPTS,format=yuv420p[vout]"
    )

    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[vout]",
            "-t",
            f"{master_duration:.6f}",
            "-map_metadata",
            "-1",
            "-map_chapters",
            "-1",
            "-sn",
            "-dn",
            "-c:v",
            "libx264",
            "-preset",
            VIDEO_PRESET,
            "-crf",
            str(VIDEO_CRF),
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(VIDEO_FPS),
            "-an",
            "-movflags",
            "+faststart",
            visual_path,
        ]
    )
    run_process(
        command,
        "master timeline 장면 크로스페이드 연결",
    )
    return visual_path


def render_master_narration(ffmpeg, timeline, master_duration, temp_dir):
    narration_path = temp_dir / "narration.wav"
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y"]
    for entry in timeline:
        command.extend(["-i", entry["processed_path"]])
    filters = []
    delayed_labels = []
    for index, entry in enumerate(timeline):
        delay_ms = round(entry["clip_start"] * 1000)
        label = f"a{index}"
        filters.append(
            f"[{index}:a]adelay={delay_ms}:all=1,asetpts=N/SR/TB[{label}]"
        )
        delayed_labels.append(label)
    audio_inputs = "".join(f"[{label}]" for label in delayed_labels)
    filters.append(
        f"{audio_inputs}amix=inputs={len(delayed_labels)}:duration=longest:"
        "dropout_transition=0:normalize=0,"
        f"apad=pad_dur={master_duration:.6f},"
        f"atrim=duration={master_duration:.6f},asetpts=N/SR/TB[aout]"
    )
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[aout]",
            "-t",
            f"{master_duration:.6f}",
            "-c:a",
            "pcm_s24le",
            "-ar",
            str(AUDIO_SAMPLE_RATE),
            "-ac",
            "2",
            narration_path,
        ]
    )
    run_process(command, "master timeline 나레이션 배치")
    return narration_path


def format_ass_time(seconds):
    centiseconds = max(0, round(seconds * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    whole_seconds, fraction = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{whole_seconds:02d}.{fraction:02d}"


def escape_ass_text(text):
    return (
        text.replace("\\", r"\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("\r\n", r"\N")
        .replace("\n", r"\N")
        .replace("\r", r"\N")
    )


def write_ass_subtitles(story, timeline, subtitle_path):
    subtitle_font_name = get_subtitle_font_name()
    style = (
        f"Style: Default,{subtitle_font_name},{SUBTITLE_FONT_SIZE},"
        f"{SUBTITLE_PRIMARY_COLOR},&H000000FF,{SUBTITLE_OUTLINE_COLOR},"
        f"{SUBTITLE_BACKGROUND_COLOR},0,0,0,0,100,100,0,0,3,"
        f"{SUBTITLE_OUTLINE},0,2,{SUBTITLE_MARGIN_LEFT},"
        f"{SUBTITLE_MARGIN_RIGHT},{SUBTITLE_MARGIN_BOTTOM},1"
    )
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {VIDEO_WIDTH}",
        f"PlayResY: {VIDEO_HEIGHT}",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        "",
        "[V4+ Styles]",
        (
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
            "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding"
        ),
        style,
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    subtitle_texts = [escape_ass_text(story["title"])] + [
        r"\N".join(escape_ass_text(paragraph) for paragraph in paragraphs)
        for paragraphs in story["scene_paragraphs"]
    ]
    for timing, text in zip(timeline, subtitle_texts):
        lines.append(
            "Dialogue: 0,"
            f"{format_ass_time(timing['speech_start'])},"
            f"{format_ass_time(timing['speech_end'])},"
            f"Default,,0,0,0,,{text}"
        )

    subtitle_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def escape_filter_path(path):
    return (
        path.resolve().as_posix()
        .replace("\\", r"\\")
        .replace(":", r"\:")
        .replace("'", r"\'")
    )


def mix_bgm(
    ffmpeg,
    visual_path,
    narration_path,
    bgm_path,
    subtitle_path,
    duration,
    output_path,
):
    fade_duration = min(BGM_FADE_OUT_SECONDS, duration)
    fade_start = max(0.0, duration - fade_duration)
    filter_complex = (
        f"[1:a]aresample={AUDIO_SAMPLE_RATE},"
        "aformat=sample_fmts=fltp:channel_layouts=stereo[narration];"
        f"[2:a]aresample={AUDIO_SAMPLE_RATE},"
        "aformat=sample_fmts=fltp:channel_layouts=stereo,"
        f"volume={BGM_VOLUME:.4f},atrim=duration={duration:.6f},"
        f"afade=t=out:st={fade_start:.6f}:d={fade_duration:.6f}[bgm];"
        "[narration][bgm]amix=inputs=2:duration=first:"
        f"dropout_transition=0:normalize=0,"
        f"alimiter=limit={FINAL_LIMITER_PEAK:.4f}:"
        "level=false:latency=true[aout]"
    )
    video_filters = [
        f"subtitles=filename='{escape_filter_path(subtitle_path)}'"
    ]
    if VIDEO_FADE_IN_SECONDS > 0:
        fade_duration = min(VIDEO_FADE_IN_SECONDS, duration)
        video_filters.append(f"fade=t=in:st=0:d={fade_duration:.6f}")
    if VIDEO_FADE_OUT_SECONDS > 0:
        fade_duration = min(VIDEO_FADE_OUT_SECONDS, duration)
        fade_start = max(0.0, duration - fade_duration)
        video_filters.append(
            f"fade=t=out:st={fade_start:.6f}:d={fade_duration:.6f}"
        )
    video_filter = ",".join(video_filters)
    run_process(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-y",
            "-i",
            visual_path,
            "-i",
            narration_path,
            "-stream_loop",
            "-1",
            "-i",
            bgm_path,
            "-filter_complex",
            filter_complex,
            "-map",
            "0:v:0",
            "-map",
            "[aout]",
            "-vf",
            video_filter,
            "-map_metadata",
            "-1",
            "-map_chapters",
            "-1",
            "-sn",
            "-dn",
            "-c:v",
            "libx264",
            "-preset",
            VIDEO_PRESET,
            "-crf",
            str(VIDEO_CRF),
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(VIDEO_FPS),
            "-t",
            f"{duration:.6f}",
            "-c:a",
            "aac",
            "-b:a",
            AUDIO_BITRATE,
            "-ar",
            str(AUDIO_SAMPLE_RATE),
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            output_path,
        ],
        "BGM 믹싱",
    )


def probe_final_video(
    ffprobe,
    video_path,
    expected_duration,
    last_scene_end,
    expected_input_count,
    rendered_image_count,
    rendered_audio_count,
):
    result = run_process(
        [
            ffprobe,
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            video_path,
        ],
        "최종 MP4 검사",
        timeout=60,
    )
    try:
        probe = json.loads(result.stdout)
        streams = probe["streams"]
        duration = float(probe["format"]["duration"])
        video_stream = next(
            stream for stream in streams if stream.get("codec_type") == "video"
        )
        audio_stream = next(
            stream for stream in streams if stream.get("codec_type") == "audio"
        )
        frame_rate = float(Fraction(video_stream["avg_frame_rate"]))
    except (KeyError, StopIteration, TypeError, ValueError, json.JSONDecodeError) as error:
        raise VideoGenerationError("최종 MP4의 영상·음성 정보를 확인할 수 없습니다.") from error

    problems = []
    media_streams = [
        stream for stream in streams
        if stream.get("codec_type") in {"video", "audio", "subtitle", "data"}
    ]
    if len(media_streams) != 2:
        stream_types = ", ".join(
            str(stream.get("codec_type")) for stream in media_streams
        )
        problems.append(f"불필요한 스트림 포함={stream_types}")
    if video_stream.get("codec_name") != "h264":
        problems.append(f"영상 코덱={video_stream.get('codec_name')}")
    if audio_stream.get("codec_name") != "aac":
        problems.append(f"음성 코덱={audio_stream.get('codec_name')}")
    if video_stream.get("width") != VIDEO_WIDTH or video_stream.get("height") != VIDEO_HEIGHT:
        problems.append(
            f"해상도={video_stream.get('width')}x{video_stream.get('height')}"
        )
    if abs(frame_rate - VIDEO_FPS) > 0.01:
        problems.append(f"프레임레이트={frame_rate}")
    if video_stream.get("pix_fmt") != "yuv420p":
        problems.append(f"픽셀 형식={video_stream.get('pix_fmt')}")
    duration_tolerance = FINAL_DURATION_TOLERANCE_FRAMES / VIDEO_FPS
    if (
        not math.isfinite(duration)
        or abs(duration - expected_duration) > duration_tolerance
    ):
        problems.append(
            f"영상 길이={duration:.3f}초, 예상={expected_duration:.3f}초"
        )
    if duration + duration_tolerance < last_scene_end:
        problems.append(
            f"마지막 장면 종료={last_scene_end:.3f}초, 영상={duration:.3f}초"
        )
    if rendered_image_count != expected_input_count:
        problems.append(
            f"이미지 입력={rendered_image_count}, 예상={expected_input_count}"
        )
    if rendered_audio_count != expected_input_count:
        problems.append(
            f"오디오 입력={rendered_audio_count}, 예상={expected_input_count}"
        )
    if problems:
        raise VideoGenerationError("최종 MP4 규격 검증 실패: " + ", ".join(problems))

    return {
        "duration": duration,
        "video_codec": video_stream.get("codec_name"),
        "audio_codec": audio_stream.get("codec_name"),
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "frame_rate": frame_rate,
        "pixel_format": video_stream.get("pix_fmt"),
    }


def verify_scene_images(ffmpeg, video_path, image_paths, timeline, master_duration):
    if len(image_paths) != len(timeline):
        raise VideoGenerationError("장면 이미지 검증 개수가 master timeline과 다릅니다.")
    scores = []
    for index, (image_path, entry) in enumerate(zip(image_paths, timeline)):
        stable_start = entry["visual_full_start"] + 0.10
        if index < len(timeline) - 1:
            stable_end = entry["transition_start"] - 0.10
        else:
            stable_end = master_duration - VIDEO_FADE_OUT_SECONDS - 0.10
        if stable_end <= stable_start:
            sample_time = (entry["visual_full_start"] + entry["visual_end"]) / 2
        else:
            sample_time = (stable_start + stable_end) / 2
        expected_filter = (
            f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:"
            "force_original_aspect_ratio=decrease:force_divisible_by=2,"
            f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,"
            "setsar=1,format=yuv420p"
        )
        result = run_process(
            [
                ffmpeg,
                "-hide_banner",
                "-nostats",
                "-ss",
                f"{sample_time:.6f}",
                "-i",
                video_path,
                "-loop",
                "1",
                "-i",
                image_path,
                "-filter_complex",
                (
                    "[0:v]trim=end_frame=1,setpts=PTS-STARTPTS[actual];"
                    f"[1:v]{expected_filter},trim=end_frame=1,"
                    "setpts=PTS-STARTPTS[expected];"
                    "[actual][expected]ssim"
                ),
                "-frames:v",
                "1",
                "-f",
                "null",
                os.devnull,
            ],
            f"최종 영상 장면 확인 ({image_path.name})",
            timeout=60,
        )
        matches = re.findall(r"All:([0-9.]+)", result.stderr)
        if not matches:
            raise VideoGenerationError(
                f"최종 영상에서 {image_path.name} 장면을 확인할 수 없습니다."
            )
        score = float(matches[-1])
        if score < SCENE_FRAME_SSIM_MINIMUM:
            raise VideoGenerationError(
                f"최종 영상 장면 불일치: {image_path.name}, SSIM={score:.4f}"
            )
        scores.append({"image": image_path.name, "time": sample_time, "ssim": score})
    return scores


def format_duration(duration):
    total_seconds = max(0, round(duration))
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def validate_video_settings():
    if TRANSITION_DURATION <= 0:
        raise VideoGenerationError("TRANSITION_DURATION은 0보다 커야 합니다.")
    if POST_SPEECH_HOLD < 0 or TRANSITION_AUDIO_LEAD <= 0:
        raise VideoGenerationError("전환 전 유지와 오디오 진입 시간 설정이 올바르지 않습니다.")
    if TRANSITION_AUDIO_LEAD >= TRANSITION_DURATION:
        raise VideoGenerationError(
            "다음 나레이션은 crossfade 종료 전에 시작하도록 설정해야 합니다."
        )
    speech_gap = POST_SPEECH_HOLD + TRANSITION_AUDIO_LEAD
    if not 0.20 <= speech_gap <= 0.30:
        raise VideoGenerationError(
            "실제 speech-to-speech 간격은 0.20~0.30초여야 합니다."
        )
    if VIDEO_FADE_IN_SECONDS < 0 or VIDEO_FADE_OUT_SECONDS < 0:
        raise VideoGenerationError("영상 페이드 시간은 0 이상이어야 합니다.")
    if TITLE_SPEECH_START < 0 or LAST_SCENE_EXTRA_SECONDS < 0:
        raise VideoGenerationError("표지 시작과 마지막 여운은 0 이상이어야 합니다.")
    if not isinstance(SILENCE_TRIM_ENABLED, bool):
        raise VideoGenerationError("SILENCE_TRIM_ENABLED는 True 또는 False여야 합니다.")
    if not -80 <= SILENCE_THRESHOLD_DB <= -20:
        raise VideoGenerationError("SILENCE_THRESHOLD_DB는 -80부터 -20 사이여야 합니다.")
    if SILENCE_START_KEEP < 0 or SILENCE_END_KEEP < 0:
        raise VideoGenerationError("앞뒤에 유지할 무음은 0 이상이어야 합니다.")
    if not 0 < SCENE_FRAME_SSIM_MINIMUM <= 1:
        raise VideoGenerationError("SCENE_FRAME_SSIM_MINIMUM은 0보다 크고 1 이하여야 합니다.")
    if not isinstance(NOISE_REDUCTION_ENABLED, bool):
        raise VideoGenerationError("NOISE_REDUCTION_ENABLED는 True 또는 False여야 합니다.")
    if not isinstance(DECLICK_ENABLED, bool):
        raise VideoGenerationError("DECLICK_ENABLED는 True 또는 False여야 합니다.")
    if not 10 <= DECLICK_WINDOW_MS <= 100:
        raise VideoGenerationError("DECLICK_WINDOW_MS는 10부터 100 사이여야 합니다.")
    if not 50 <= DECLICK_OVERLAP_PERCENT <= 95:
        raise VideoGenerationError(
            "DECLICK_OVERLAP_PERCENT는 50부터 95 사이여야 합니다."
        )
    if not 0 <= DECLICK_AR_ORDER <= 25:
        raise VideoGenerationError("DECLICK_AR_ORDER는 0부터 25 사이여야 합니다.")
    if not 1 <= DECLICK_THRESHOLD <= 100:
        raise VideoGenerationError("DECLICK_THRESHOLD는 1부터 100 사이여야 합니다.")
    if not 0 <= DECLICK_BURST_FUSION <= 10:
        raise VideoGenerationError("DECLICK_BURST_FUSION은 0부터 10 사이여야 합니다.")
    if not 0.01 <= NOISE_REDUCTION_STRENGTH <= 97:
        raise VideoGenerationError("NOISE_REDUCTION_STRENGTH는 0.01부터 97 사이여야 합니다.")
    if not -80 <= NOISE_REDUCTION_FLOOR_DB <= -20:
        raise VideoGenerationError("NOISE_REDUCTION_FLOOR_DB는 -80부터 -20 사이여야 합니다.")
    if not 0 <= NARRATION_MICRO_FADE_SECONDS <= 0.03:
        raise VideoGenerationError(
            "NARRATION_MICRO_FADE_SECONDS는 0부터 0.03초 사이여야 합니다."
        )
    if not 0 <= BGM_VOLUME <= 1:
        raise VideoGenerationError("BGM_VOLUME은 0부터 1 사이여야 합니다.")
    if not 0.0625 <= NARRATION_LIMITER_PEAK <= 1:
        raise VideoGenerationError("NARRATION_LIMITER_PEAK는 0.0625부터 1 사이여야 합니다.")
    if not 0.0625 <= FINAL_LIMITER_PEAK <= 1:
        raise VideoGenerationError("FINAL_LIMITER_PEAK는 0.0625부터 1 사이여야 합니다.")


def generate_video(folder_argument):
    validate_video_settings()
    ffmpeg, ffprobe = find_ffmpeg_tools()
    verify_ffmpeg_filters(ffmpeg)
    story_dir, folder_slug = resolve_story_folder(folder_argument)
    story = load_video_story(story_dir, folder_slug)
    inputs = validate_inputs(folder_argument, story_dir, story)

    inputs["work_dir"].mkdir(parents=True, exist_ok=True)
    temp_dir = Path(
        tempfile.mkdtemp(prefix=".tmp-video-", dir=inputs["work_dir"])
    )
    output_dir = inputs["work_dir"] / "output"
    final_output = output_dir / f"{story['slug']}.mp4"
    temp_output = temp_dir / f"{story['slug']}.mp4"

    try:
        print(f"FFmpeg: {ffmpeg}")
        print(f"ffprobe: {ffprobe}")
        print("[1/8] 무음 정리 및 음성 후처리 중...")
        processed_audio = preprocess_audio_files(
            ffmpeg, ffprobe, inputs["audio_paths"], temp_dir
        )
        timeline, master_duration = build_master_timeline(processed_audio)
        probe_duration(ffprobe, inputs["bgm_path"], "BGM")

        expected_input_count = len(story["scene_images"]) + 1
        if not (
            len(inputs["image_paths"])
            == len(inputs["audio_paths"])
            == len(processed_audio)
            == len(timeline)
            == expected_input_count
        ):
            raise VideoGenerationError(
                "이미지·오디오·master timeline 입력 개수가 일치하지 않습니다."
            )

        print("  [음성 전처리 계측]")
        print("  구간 | 원본 | trim후 | 앞제거 | 뒤제거 | processed")
        for entry in timeline:
            print(
                f"  {entry['label']} | {entry['original_duration']:.3f} | "
                f"{entry['trimmed_duration']:.3f} | {entry['removed_start']:.3f} | "
                f"{entry['removed_end']:.3f} | {entry['processed_duration']:.3f}"
            )

        print("  [master timeline]")
        print("  구간 | speech_start | speech_end | transition_start | transition_end")
        for entry in timeline:
            transition_start = (
                "-" if entry["transition_start"] is None
                else f"{entry['transition_start']:.3f}"
            )
            transition_end = (
                "-" if entry["transition_end"] is None
                else f"{entry['transition_end']:.3f}"
            )
            print(
                f"  {entry['label']} | {entry['speech_start']:.3f} | "
                f"{entry['speech_end']:.3f} | {transition_start} | {transition_end}"
            )

        print(f"[2/8] 장면 영상 {len(timeline)}개 생성 중...")
        segment_paths = []
        for index, (image_path, entry) in enumerate(
            zip(inputs["image_paths"], timeline), start=0
        ):
            segment_path = temp_dir / f"segment_{index:03d}.mp4"
            segment_start = 0.0 if index == 0 else entry["visual_start"]
            segment_duration = entry["visual_end"] - segment_start
            render_visual_segment(
                ffmpeg, image_path, segment_duration, segment_path
            )
            segment_paths.append(segment_path)
            print(
                f"  {entry['label']}: {image_path.name}, "
                f"최종 {entry['visual_start']:.3f}~{entry['visual_end']:.3f}초"
            )

        print("[3/8] master timeline 장면 크로스페이드 연결 중...")
        visual_path = combine_visual_segments(
            ffmpeg, segment_paths, timeline, master_duration, temp_dir
        )
        visual_duration = probe_duration(ffprobe, visual_path, "연결 영상")
        if abs(visual_duration - master_duration) > FINAL_DURATION_TOLERANCE_FRAMES / VIDEO_FPS:
            raise VideoGenerationError(
                f"시각 타임라인 길이 불일치: {visual_duration:.3f} != {master_duration:.3f}"
            )

        print("[4/8] master timeline 나레이션 배치 중...")
        narration_path = render_master_narration(
            ffmpeg, timeline, master_duration, temp_dir
        )
        narration_duration = probe_duration(ffprobe, narration_path, "나레이션")
        if abs(narration_duration - master_duration) > 1 / AUDIO_SAMPLE_RATE:
            raise VideoGenerationError(
                f"나레이션 길이 불일치: {narration_duration:.6f} != "
                f"{master_duration:.6f}"
            )

        print("[5/8] 발화 시점 기준 ASS 자막 생성 중...")
        subtitle_path = temp_dir / "subtitles.ass"
        write_ass_subtitles(story, timeline, subtitle_path)

        print("[6/8] 자막 적용 및 BGM 믹싱 중...")
        mix_bgm(
            ffmpeg,
            visual_path,
            narration_path,
            inputs["bgm_path"],
            subtitle_path,
            master_duration,
            temp_output,
        )

        print("[7/8] 최종 MP4 규격·길이·입력 개수 검증 중...")
        video_info = probe_final_video(
            ffprobe,
            temp_output,
            master_duration,
            timeline[-1]["visual_end"],
            expected_input_count,
            len(segment_paths),
            len(processed_audio),
        )

        print("[8/8] 최종 영상의 전체 장면 존재 검증 중...")
        scene_scores = verify_scene_images(
            ffmpeg,
            temp_output,
            inputs["image_paths"],
            timeline,
            master_duration,
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        os.replace(temp_output, final_output)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "title": story["title"],
        "output": final_output,
        "expected_duration": master_duration,
        "timeline": timeline,
        "scene_scores": scene_scores,
        **video_info,
    }


def main():
    if len(sys.argv) != 2:
        print("사용법: python generate_video.py bible-storybook-<slug>")
        return 2
    try:
        result = generate_video(sys.argv[1])
    except VideoGenerationError as error:
        print(f"오류: {error}")
        return 1

    print()
    print("영상 생성 완료")
    print(f"제목: {result['title']}")
    print(
        f"영상 길이: {format_duration(result['duration'])} "
        f"({result['duration']:.3f}초)"
    )
    print(f"저장 위치: {result['output']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
