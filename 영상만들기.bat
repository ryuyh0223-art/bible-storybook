@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"

set "INTERACTIVE_MODE=0"
if "%~1"=="" (
    set "INTERACTIVE_MODE=1"
    echo 영상으로 만들 동화 폴더명을 입력하세요:
    echo 예: bible-storybook-god-is-near
    set /p "STORY_FOLDER=^> "
) else (
    set "STORY_FOLDER=%~1"
)

if not "%~2"=="" goto :usage
if not defined STORY_FOLDER (
    echo 오류: 동화 폴더명을 입력하지 않았습니다.
    goto :failed
)
if not exist "%STORY_FOLDER%\" (
    echo 오류: 동화 폴더가 없습니다: %STORY_FOLDER%
    goto :failed
)

call :find_python
if errorlevel 1 goto :failed

echo ==================================================
echo 해피팡 성경동화 영상 자동 생성
echo ==================================================
echo.

"%HAPPYPANG_PYTHON%" generate_video.py "%STORY_FOLDER%"
if errorlevel 1 goto :failed

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
echo 사용법: 영상만들기.bat bible-storybook-^<slug^>
call :pause_if_interactive
exit /b 2

:failed
echo.
echo 오류가 발생하여 영상 생성을 중단했습니다.
call :pause_if_interactive
exit /b 1

:pause_if_interactive
if "%INTERACTIVE_MODE%"=="1" (
    echo.
    echo 내용을 확인한 뒤 아무 키나 누르면 창이 닫힙니다.
    pause >nul
)
exit /b 0
