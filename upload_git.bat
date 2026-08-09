@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"

if "%~1"=="" goto :usage
if not "%~3"=="" goto :usage

set "STORY_FOLDER=%~1"
set "RUN_MODE="
if not "%~2"=="" (
    if /I not "%~2"=="--dry-run" goto :usage
    set "RUN_MODE=--dry-run"
)

call :find_python
if errorlevel 1 exit /b 1

echo [5/6] Git stage 및 commit 중...
"%HAPPYPANG_PYTHON%" publish_story.py commit "%STORY_FOLDER%" %RUN_MODE%
if errorlevel 1 exit /b 1

if defined RUN_MODE (
    echo.
    echo [6/6] GitHub 배포 생략 - DRY-RUN
    exit /b 0
)

echo.
echo [6/6] GitHub 배포 중...
git push origin main
if errorlevel 1 (
    echo 오류: git push origin main에 실패했습니다.
    exit /b 1
)

"%HAPPYPANG_PYTHON%" publish_story.py verify-push "%STORY_FOLDER%"
if errorlevel 1 exit /b 1
exit /b 0

:find_python
if defined HAPPYPANG_PYTHON (
    if exist "%HAPPYPANG_PYTHON%" exit /b 0
)
for /f "delims=" %%P in ('where python.exe 2^>nul') do (
    if not defined HAPPYPANG_PYTHON set "HAPPYPANG_PYTHON=%%P"
)
if not defined HAPPYPANG_PYTHON (
    set "CODEX_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if exist "%CODEX_PYTHON%" set "HAPPYPANG_PYTHON=%CODEX_PYTHON%"
)
if not defined HAPPYPANG_PYTHON (
    echo 오류: Python 실행 파일을 찾을 수 없습니다.
    exit /b 1
)
"%HAPPYPANG_PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo 오류: Python을 실행할 수 없습니다: %HAPPYPANG_PYTHON%
    exit /b 1
)
exit /b 0

:usage
echo 사용법: upload_git.bat bible-storybook-^<slug^> [--dry-run]
exit /b 2
