#!/bin/bash

set -u

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

INTERACTIVE_MODE=0
STORY_FOLDER="${1-}"
RUN_MODE="${2-}"

pause_if_interactive() {
    if [ "$INTERACTIVE_MODE" -eq 1 ]; then
        echo
        read -r -p "내용을 확인한 뒤 Enter 키를 누르면 창이 닫힙니다. " _
    fi
}

fail() {
    echo
    echo "오류가 발생하여 배포를 중단했습니다. commit과 push 상태를 확인하세요."
    pause_if_interactive
    exit 1
}

usage() {
    echo "사용법: ./업로드실행.command bible-storybook-<slug> [--dry-run]"
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

if [ "$#" -gt 2 ]; then
    usage
fi

if [ -z "$STORY_FOLDER" ]; then
    INTERACTIVE_MODE=1
    echo "배포할 동화 폴더명을 입력하세요:"
    echo "예: bible-storybook-god-is-near"
    read -r -p "> " STORY_FOLDER
fi

if [ -z "$STORY_FOLDER" ]; then
    echo "오류: 동화 폴더명을 입력하지 않았습니다."
    fail
fi
if [ -n "$RUN_MODE" ] && [ "$RUN_MODE" != "--dry-run" ]; then
    usage
fi
if [ ! -d "$STORY_FOLDER" ]; then
    echo "오류: 동화 폴더가 없습니다: $STORY_FOLDER"
    fail
fi
if [ ! -f "$STORY_FOLDER/story.json" ]; then
    echo "오류: story.json이 없습니다: $STORY_FOLDER/story.json"
    fail
fi
find_python || fail

echo "=================================================="
echo "해피팡 성경동화 주간 배포"
if [ "$RUN_MODE" = "--dry-run" ]; then
    echo "DRY-RUN 모드: commit과 push를 실행하지 않습니다."
fi
echo "=================================================="
echo

echo "[1/6] story.json 및 Git 최신 상태 검사 중..."
if [ "$RUN_MODE" = "--dry-run" ]; then
    "$PYTHON" publish_story.py preflight "$STORY_FOLDER" --dry-run || fail
else
    "$PYTHON" publish_story.py preflight "$STORY_FOLDER" || fail
fi

echo
echo "[2/6] 웹 동화 생성 중..."
if [ "$RUN_MODE" = "--dry-run" ]; then
    "$PYTHON" generate_story.py --validate-only "$STORY_FOLDER/story.json" || fail
else
    "$PYTHON" generate_story.py "$STORY_FOLDER/story.json" || fail
fi

echo
echo "[3/6] 아카이브 갱신 중..."
"$PYTHON" generate_archive.py || fail

echo
echo "[4/6] 생성 파일과 변경 범위 검증 중..."
if [ "$RUN_MODE" = "--dry-run" ]; then
    "$PYTHON" publish_story.py validate "$STORY_FOLDER" --dry-run || fail
else
    "$PYTHON" publish_story.py validate "$STORY_FOLDER" || fail
fi

echo
echo "[5/6] Git stage 및 commit 중..."
if [ "$RUN_MODE" = "--dry-run" ]; then
    "$PYTHON" publish_story.py commit "$STORY_FOLDER" --dry-run || fail
    echo
    echo "[6/6] GitHub 배포 생략 - DRY-RUN"
else
    "$PYTHON" publish_story.py commit "$STORY_FOLDER" || fail
    echo
    echo "[6/6] GitHub 배포 중..."
    git push origin main || {
        echo "오류: git push origin main에 실패했습니다."
        fail
    }
    "$PYTHON" publish_story.py verify-push "$STORY_FOLDER" || fail
fi

echo
echo "=================================================="
if [ "$RUN_MODE" = "--dry-run" ]; then
    echo "DRY-RUN 완료 - commit과 push는 실행하지 않았습니다."
else
    echo "배포 완료"
fi
echo "=================================================="
pause_if_interactive
