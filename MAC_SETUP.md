# MacBook 최초 설정

처음 한 번만 Terminal에서 아래 순서대로 실행하세요.

## 1. Command Line Tools 확인

```bash
xcode-select --install
```

이미 설치되어 있다는 메시지가 나오면 다음 단계로 진행합니다.

## 2. Homebrew 설치

Homebrew가 없다면 [brew.sh](https://brew.sh/ko/)에 표시된 설치 명령을 복사해 실행합니다.

## 3. 필요한 프로그램 설치

```bash
brew install git python ffmpeg gh
git --version
python3 --version
ffmpeg -version
ffprobe -version
```

별도의 Python 패키지나 virtualenv는 필요하지 않습니다.

## 4. GitHub 로그인

```bash
gh auth login
gh auth setup-git
```

화면에서 `GitHub.com`과 `HTTPS`를 선택하고 브라우저 로그인을 완료합니다.

## 5. 저장소 복제

```bash
git clone https://github.com/ryuyh0223-art/bible-storybook.git
cd bible-storybook
```

## 6. 영상 작업 폴더 준비

사용 권한이 있는 BGM을 다음 위치에 넣습니다.

```text
video-work/bgm.mp3
```

동화별 녹음 파일은 다음 구조로 준비합니다.

```text
video-work/bible-storybook-<slug>/audio/title.m4a
video-work/bible-storybook-<slug>/audio/scene_01.m4a
...
```

`video-work/`의 BGM, 녹음, MP4는 GitHub에 올라가지 않습니다.

## 7. 최초 테스트

웹 배포 검증만 실행하고 commit/push하지 않으려면:

```bash
./업로드실행.command bible-storybook-god-is-near --dry-run
```

영상 생성을 테스트하려면:

```bash
./영상만들기.command bible-storybook-god-is-near
```

Finder에서 `.command` 파일을 더블클릭해도 됩니다. macOS가 최초 실행을 차단하면 Finder에서 파일을 Control-클릭하고 `열기`를 선택하세요.

## 매주 사용법

작업 시작:

```bash
git pull origin main
```

웹 배포: `업로드실행.command` 더블클릭 또는

```bash
./업로드실행.command bible-storybook-<slug>
```

영상 생성: `영상만들기.command` 더블클릭 또는

```bash
./영상만들기.command bible-storybook-<slug>
```
