#!/bin/bash

set -u

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

INTERACTIVE_MODE=0
STORY_FOLDER="${1-}"

pause_if_interactive() {
    if [ "$INTERACTIVE_MODE" -eq 1 ]; then
        echo
        read -r -p "내용을 확인한 뒤 Enter 키를 누르면 창이 닫힙니다. " _
    fi
}

fail() {
    echo
    echo "오류가 발생하여 영상 생성을 중단했습니다."
    pause_if_interactive
    exit 1
}

usage() {
    echo "사용법: ./영상만들기.command bible-storybook-<slug>"
    pause_if_interactive
    exit 2
}

find_python() {
    is_python3() {
        "$1" -c 'import sys; raise SystemExit(0 if sys.version_info.major == 3 else 1)' \
            >/dev/null 2>&1
    }
    if [ -n "${HAPPYPANG_PYTHON-}" ] && \
       is_python3 "$HAPPYPANG_PYTHON"; then
        PYTHON="$HAPPYPANG_PYTHON"
        return 0
    fi
    if command -v python3 >/dev/null 2>&1 && is_python3 "$(command -v python3)"; then
        PYTHON="$(command -v python3)"
        return 0
    fi
    if command -v python >/dev/null 2>&1 && is_python3 "$(command -v python)"; then
        PYTHON="$(command -v python)"
        return 0
    fi
    echo "오류: Python 3 실행 파일을 찾을 수 없습니다."
    return 1
}

if [ "$#" -gt 1 ]; then
    usage
fi
if [ -z "$STORY_FOLDER" ]; then
    INTERACTIVE_MODE=1
    echo "영상으로 만들 동화 폴더명을 입력하세요:"
    echo "예: bible-storybook-god-is-near"
    read -r -p "> " STORY_FOLDER
fi
if [ -z "$STORY_FOLDER" ]; then
    echo "오류: 동화 폴더명을 입력하지 않았습니다."
    fail
fi
if [ ! -d "$STORY_FOLDER" ]; then
    echo "오류: 동화 폴더가 없습니다: $STORY_FOLDER"
    fail
fi
find_python || fail

echo "=================================================="
echo "해피팡 성경동화 영상 자동 생성"
echo "=================================================="
echo

"$PYTHON" generate_video.py "$STORY_FOLDER" || fail
pause_if_interactive
