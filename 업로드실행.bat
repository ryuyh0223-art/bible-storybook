@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"

if not "%~3"=="" goto :usage

set "INTERACTIVE_MODE=0"
set "RUN_MODE="
if "%~1"=="" (
    set "INTERACTIVE_MODE=1"
    echo 배포할 동화 폴더명을 입력하세요:
    echo 예: bible-storybook-god-is-near
    set /p "STORY_FOLDER=^> "
) else (
    set "STORY_FOLDER=%~1"
)

if not defined STORY_FOLDER (
    echo 오류: 동화 폴더명을 입력하지 않았습니다.
    goto :failed
)

if not "%~2"=="" (
    if /I not "%~2"=="--dry-run" goto :usage
    set "RUN_MODE=--dry-run"
)

if not exist "%STORY_FOLDER%\" (
    echo 오류: 동화 폴더가 없습니다: %STORY_FOLDER%
    goto :failed
)
if not exist "%STORY_FOLDER%\story.json" (
    echo 오류: story.json이 없습니다: %STORY_FOLDER%\story.json
    goto :failed
)

call :find_python
if errorlevel 1 goto :failed

echo ==================================================
echo 해피팡 성경동화 주간 배포
if defined RUN_MODE echo DRY-RUN 모드: commit과 push를 실행하지 않습니다.
echo ==================================================
echo.

echo [1/6] story.json 및 Git 최신 상태 검사 중...
"%HAPPYPANG_PYTHON%" publish_story.py preflight "%STORY_FOLDER%" %RUN_MODE%
if errorlevel 1 goto :failed

echo.
echo [2/6] 웹 동화 생성 중...
if defined RUN_MODE (
    "%HAPPYPANG_PYTHON%" generate_story.py --validate-only "%STORY_FOLDER%\story.json"
) else (
    "%HAPPYPANG_PYTHON%" generate_story.py "%STORY_FOLDER%\story.json"
)
if errorlevel 1 goto :failed

echo.
echo [3/6] 아카이브 갱신 중...
"%HAPPYPANG_PYTHON%" generate_archive.py
if errorlevel 1 goto :failed

echo.
echo [4/6] 생성 파일과 변경 범위 검증 중...
"%HAPPYPANG_PYTHON%" publish_story.py validate "%STORY_FOLDER%" %RUN_MODE%
if errorlevel 1 goto :failed

echo.
call upload_git.bat "%STORY_FOLDER%" %RUN_MODE%
if errorlevel 1 goto :failed

echo.
echo ==================================================
if defined RUN_MODE (
    echo DRY-RUN 완료 - commit과 push는 실행하지 않았습니다.
) else (
    echo 배포 완료
)
echo ==================================================
call :pause_if_interactive
exit /b 0

:find_python
if defined HAPPYPANG_PYTHON (
    if exist "%HAPPYPANG_PYTHON%" (
        "%HAPPYPANG_PYTHON%" --version >nul 2>&1
        if not errorlevel 1 exit /b 0
    )
    set "HAPPYPANG_PYTHON="
)
set "CODEX_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%CODEX_PYTHON%" (
    "%CODEX_PYTHON%" --version >nul 2>&1
    if not errorlevel 1 set "HAPPYPANG_PYTHON=%CODEX_PYTHON%"
)
if not defined HAPPYPANG_PYTHON for /f "delims=" %%P in ('where python.exe 2^>nul') do (
    if not defined HAPPYPANG_PYTHON (
        "%%P" --version >nul 2>&1
        if not errorlevel 1 set "HAPPYPANG_PYTHON=%%P"
    )
)
if not defined HAPPYPANG_PYTHON (
    echo 오류: Python 실행 파일을 찾을 수 없습니다.
    exit /b 1
)
exit /b 0

:usage
echo 사용법: 업로드실행.bat bible-storybook-^<slug^> [--dry-run]
call :pause_if_interactive
exit /b 2

:failed
echo.
echo 오류가 발생하여 배포를 중단했습니다. commit과 push 상태를 확인하세요.
call :pause_if_interactive
exit /b 1

:pause_if_interactive
if "%INTERACTIVE_MODE%"=="1" (
    echo.
    echo 내용을 확인한 뒤 아무 키나 누르면 창이 닫힙니다.
    pause >nul
)
exit /b 0
