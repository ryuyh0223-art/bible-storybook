import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STORY_FOLDER_PATTERN = re.compile(
    r"^bible-storybook-([a-z0-9]+(?:-[a-z0-9]+)*)$"
)
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
GENERATED_FILES = {"index.html", "style.css", "script.js"}
DEPLOYMENT_ROOT_FILES = {"index.html", "archive-style.css"}
AUTOMATION_DEVELOPMENT_FILES = {
    "generate_archive.py",
    "generate_story.py",
    "publish_story.py",
    "upload_git.bat",
    "업로드실행.bat",
}


class PublishError(Exception):
    """주간 배포를 안전하게 중단해야 하는 오류."""


def run_git(arguments, check=True):
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        raise PublishError(
            f"git {' '.join(arguments)} 실행에 실패했습니다."
            + (f"\n{details}" if details else "")
        )
    return result


def git_value(*arguments):
    return run_git(list(arguments)).stdout.strip()


def resolve_story_folder(folder_argument):
    if not folder_argument or Path(folder_argument).name != folder_argument:
        raise PublishError(
            "동화 폴더명만 입력하세요. 예: bible-storybook-new-story"
        )

    match = STORY_FOLDER_PATTERN.fullmatch(folder_argument)
    if not match:
        raise PublishError(
            "동화 폴더명은 bible-storybook-<slug> 형식이어야 합니다."
        )

    story_dir = ROOT / folder_argument
    if not story_dir.is_dir():
        raise PublishError(f"동화 폴더가 없습니다: {folder_argument}")

    story_json_path = story_dir / "story.json"
    if not story_json_path.is_file():
        raise PublishError(f"story.json이 없습니다: {story_json_path}")
    return story_dir, match.group(1)


def require_string(container, field_name, source_path):
    value = container.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise PublishError(
            f"{source_path}: '{field_name}'은 비어 있지 않은 문자열이어야 합니다."
        )
    return value.strip()


def load_story_metadata(story_dir, folder_slug):
    story_json_path = story_dir / "story.json"
    try:
        data = json.loads(story_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise PublishError(
            f"story.json 문법 오류: {error.lineno}행 {error.colno}열 - {error.msg}"
        ) from error
    except UnicodeDecodeError as error:
        raise PublishError(
            "story.json을 UTF-8 텍스트로 저장해야 합니다."
        ) from error
    except OSError as error:
        raise PublishError(f"story.json을 읽을 수 없습니다: {error}") from error

    if not isinstance(data, dict):
        raise PublishError("story.json의 최상위 값은 JSON 객체여야 합니다.")

    slug = require_string(data, "slug", story_json_path)
    if slug != folder_slug:
        raise PublishError(
            f"story.json의 slug와 폴더명이 다릅니다: {slug} != {folder_slug}"
        )
    title = require_string(data, "title", story_json_path)
    cover_image = require_string(data, "cover_image", story_json_path)

    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise PublishError("story.json의 scenes에는 장면이 하나 이상 있어야 합니다.")

    image_names = [cover_image]
    for index, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            raise PublishError(f"scenes[{index}]은 JSON 객체여야 합니다.")
        image_names.append(
            require_string(scene, "image", story_json_path)
        )

    images_dir = story_dir / "assets" / "images"
    if not images_dir.is_dir():
        raise PublishError(f"이미지 폴더가 없습니다: {images_dir}")

    actual_names = {
        item.name for item in images_dir.iterdir() if item.is_file()
    }
    for image_name in image_names:
        image_path = Path(image_name)
        if image_path.name != image_name or image_name in {".", ".."}:
            raise PublishError(
                f"이미지 항목에는 파일명만 입력하세요: {image_name}"
            )
        if image_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            raise PublishError(f"지원하지 않는 이미지 형식입니다: {image_name}")
        if image_name not in actual_names:
            case_matches = [
                name
                for name in actual_names
                if name.casefold() == image_name.casefold()
            ]
            if case_matches:
                raise PublishError(
                    "이미지 파일명의 대소문자가 다릅니다: "
                    f"JSON='{image_name}', 실제='{case_matches[0]}'"
                )
            raise PublishError(f"story.json에 선언된 이미지가 없습니다: {image_name}")

    return {
        "title": title,
        "slug": slug,
        "image_names": image_names,
        "page_count": len(scenes) + 1,
    }


def validate_story_file_set(story_dir, metadata, generated):
    expected = {"story.json"}
    expected.update(
        f"assets/images/{image_name}"
        for image_name in metadata["image_names"]
    )
    if generated:
        expected.update(GENERATED_FILES)

    actual = {
        item.relative_to(story_dir).as_posix()
        for item in story_dir.rglob("*")
        if item.is_file()
    }
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing:
        raise PublishError("필수 파일이 없습니다: " + ", ".join(missing))
    if unexpected:
        raise PublishError(
            "동화 폴더에 배포 대상이 아닌 파일이 있습니다: "
            + ", ".join(unexpected)
        )


def git_status_entries():
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        details = result.stderr.decode("utf-8", errors="replace").strip()
        raise PublishError(f"git status 실행에 실패했습니다.\n{details}")

    fields = result.stdout.split(b"\0")
    entries = []
    index = 0
    while index < len(fields):
        raw_entry = fields[index]
        if not raw_entry:
            index += 1
            continue
        entry = raw_entry.decode("utf-8", errors="replace")
        status = entry[:2]
        path = entry[3:].replace("\\", "/")
        entries.append((status, path))
        if status[0] in {"R", "C"} and index + 1 < len(fields):
            index += 1
            old_path = fields[index].decode("utf-8", errors="replace")
            entries.append((status, old_path.replace("\\", "/")))
        index += 1
    return entries


def is_story_path(path):
    return path.startswith("bible-storybook-")


def is_target_path(path, folder_name):
    return path == folder_name or path.startswith(folder_name + "/")


def validate_change_scope(folder_name, phase, dry_run):
    entries = git_status_entries()
    disallowed = []
    for _status, path in entries:
        if path == "dramatic-epilogue" or path.startswith("dramatic-epilogue/"):
            raise PublishError("dramatic-epilogue 변경이 감지되어 중단합니다.")
        if is_story_path(path) and not is_target_path(path, folder_name):
            raise PublishError(
                f"기존 동화의 의도하지 않은 변경이 감지되었습니다: {path}"
            )

        allowed = is_target_path(path, folder_name)
        if phase == "after-generation" and path in DEPLOYMENT_ROOT_FILES:
            allowed = True
        if dry_run and (
            path in AUTOMATION_DEVELOPMENT_FILES
            or path in DEPLOYMENT_ROOT_FILES
        ):
            allowed = True
        if not allowed:
            disallowed.append(path)

    if disallowed:
        raise PublishError(
            "이번 동화와 관계없는 변경이 있습니다: "
            + ", ".join(sorted(set(disallowed)))
        )
    return entries


def ensure_no_staged_changes():
    result = run_git(["diff", "--cached", "--quiet"], check=False)
    if result.returncode == 1:
        raise PublishError(
            "이미 stage된 변경이 있습니다. 주간 배포와 분리해서 먼저 처리하세요."
        )
    if result.returncode != 0:
        raise PublishError("stage 상태를 확인할 수 없습니다.")


def ensure_no_merge_or_conflict():
    merge_head = run_git(
        ["rev-parse", "-q", "--verify", "MERGE_HEAD"], check=False
    )
    if merge_head.returncode == 0:
        raise PublishError("진행 중인 merge가 있어 배포를 중단합니다.")
    for marker in ("rebase-merge", "rebase-apply"):
        marker_path = Path(git_value("rev-parse", "--git-path", marker))
        if not marker_path.is_absolute():
            marker_path = ROOT / marker_path
        if marker_path.exists():
            raise PublishError("진행 중인 rebase가 있어 배포를 중단합니다.")
    conflicts = git_value("diff", "--name-only", "--diff-filter=U")
    if conflicts:
        raise PublishError("충돌 파일이 있어 배포를 중단합니다.\n" + conflicts)


def ensure_remote_sync(dry_run):
    fetch = run_git(["fetch", "origin"], check=False)
    if fetch.returncode != 0:
        details = (fetch.stderr or fetch.stdout).strip()
        raise PublishError(
            "git fetch origin에 실패했습니다."
            + (f"\n{details}" if details else "")
        )

    local_main = git_value("rev-parse", "main")
    origin_main = git_value("rev-parse", "origin/main")
    if local_main != origin_main:
        raise PublishError(
            "local main과 origin/main이 다릅니다. pull/merge/rebase를 자동으로 "
            "진행하지 않습니다."
        )

    branch = git_value("branch", "--show-current")
    head = git_value("rev-parse", "HEAD")
    if dry_run:
        ancestor = run_git(
            ["merge-base", "--is-ancestor", "origin/main", "HEAD"],
            check=False,
        )
        if ancestor.returncode != 0:
            raise PublishError(
                "현재 dry-run 브랜치가 최신 origin/main을 기반으로 하지 않습니다."
            )
    elif branch != "main" or head != origin_main:
        raise PublishError(
            "실제 배포는 최신 origin/main과 동일한 local main에서만 가능합니다."
        )


def run_diff_check():
    result = run_git(["diff", "--check"], check=False)
    if result.returncode != 0:
        details = (result.stdout or result.stderr).strip()
        raise PublishError(
            "git diff --check에 실패했습니다."
            + (f"\n{details}" if details else "")
        )


def validate_generated_html(story_dir, expected_page_count):
    required = [story_dir / name for name in sorted(GENERATED_FILES)]
    missing = [path.name for path in required if not path.is_file()]
    if missing:
        raise PublishError("생성된 필수 파일이 없습니다: " + ", ".join(missing))

    try:
        page_html = (story_dir / "index.html").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise PublishError(f"생성된 index.html을 읽을 수 없습니다: {error}") from error

    def class_count(class_name):
        attributes = re.findall(r'class=["\']([^"\']*)["\']', page_html)
        return sum(class_name in value.split() for value in attributes)

    counts = {
        "image-slide": class_count("image-slide"),
        "text-page": class_count("text-page"),
        "dot": class_count("dot"),
    }
    if any(value != expected_page_count for value in counts.values()):
        details = ", ".join(f"{name}={value}" for name, value in counts.items())
        raise PublishError(
            f"페이지 개수가 맞지 않습니다. 예상={expected_page_count}, {details}"
        )


def validate_archive(folder_name, title):
    archive_path = ROOT / "index.html"
    try:
        archive_html = archive_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise PublishError(f"루트 index.html을 읽을 수 없습니다: {error}") from error

    cards = re.findall(
        r'<a href="([^"]+)/index\.html" class="story-card">[\s\S]*?'
        r'<h3 class="card-title">([\s\S]*?)</h3>',
        archive_html,
    )
    if not cards:
        raise PublishError("아카이브 카드를 찾을 수 없습니다.")

    normalized_cards = [
        (folder, html.unescape(re.sub(r"<[^>]+>", "", card_title)).strip())
        for folder, card_title in cards
    ]
    expected = (folder_name, title)
    if normalized_cards.count(expected) != 1:
        raise PublishError(
            "새 동화가 아카이브에 정확히 한 번 포함되지 않았습니다."
        )
    if normalized_cards[0] != expected:
        raise PublishError("새 동화가 아카이브 최상단에 있지 않습니다.")


def deployment_changes(folder_name):
    result = []
    for status, path in git_status_entries():
        if is_target_path(path, folder_name) or path in DEPLOYMENT_ROOT_FILES:
            result.append((status, path))
    return result


def expected_pages_url(folder_name):
    remote = git_value("remote", "get-url", "origin")
    match = re.fullmatch(
        r"https://github\.com/([^/]+)/([^/]+?)(?:\.git)?", remote
    )
    if not match:
        return f"https://<GitHub-Pages>/{folder_name}/"
    owner, repository = match.groups()
    return f"https://{owner}.github.io/{repository}/{folder_name}/"


def command_preflight(args):
    story_dir, folder_slug = resolve_story_folder(args.folder)
    metadata = load_story_metadata(story_dir, folder_slug)
    validate_story_file_set(story_dir, metadata, generated=args.dry_run)
    ensure_no_merge_or_conflict()
    ensure_no_staged_changes()
    ensure_remote_sync(args.dry_run)
    validate_change_scope(args.folder, "before-generation", args.dry_run)

    tracked_story = run_git(
        ["ls-files", "--error-unmatch", f"{args.folder}/story.json"],
        check=False,
    )
    if args.dry_run:
        if tracked_story.returncode != 0:
            raise PublishError(
                "기존 배포 동화를 사용하는 dry-run에서는 story.json이 tracked 상태여야 합니다."
            )
    elif tracked_story.returncode == 0:
        raise PublishError("이미 Git에 등록된 동화 폴더는 새로 배포할 수 없습니다.")

    print(f"story.json 및 이미지 {len(metadata['image_names'])}개 검사 완료")
    print("local main과 origin/main 최신 상태 확인 완료")


def command_validate(args):
    story_dir, folder_slug = resolve_story_folder(args.folder)
    metadata = load_story_metadata(story_dir, folder_slug)
    validate_story_file_set(story_dir, metadata, generated=True)
    validate_generated_html(story_dir, metadata["page_count"])
    validate_archive(args.folder, metadata["title"])
    run_diff_check()
    validate_change_scope(args.folder, "after-generation", args.dry_run)

    print("생성 파일, 이미지, 페이지 수, 아카이브 검사 완료")
    print("git diff --check 및 기존 동화 변경 범위 검사 완료")
    print("배포 예정 변경:")
    changes = deployment_changes(args.folder)
    if changes:
        for status, path in changes:
            print(f"  {status} {path}")
    else:
        print("  변경 없음")


def staged_paths():
    output = run_git(["diff", "--cached", "--name-only", "-z"]).stdout
    return {
        path.replace("\\", "/")
        for path in output.split("\0")
        if path
    }


def command_commit(args):
    story_dir, folder_slug = resolve_story_folder(args.folder)
    metadata = load_story_metadata(story_dir, folder_slug)
    validate_story_file_set(story_dir, metadata, generated=True)
    validate_generated_html(story_dir, metadata["page_count"])
    validate_archive(args.folder, metadata["title"])
    run_diff_check()
    validate_change_scope(args.folder, "after-generation", args.dry_run)
    ensure_no_merge_or_conflict()
    ensure_no_staged_changes()
    ensure_remote_sync(args.dry_run)

    commit_message = f"Add new story: {metadata['title']}"
    changes = deployment_changes(args.folder)
    if args.dry_run:
        print(f"DRY-RUN 커밋 메시지: {commit_message}")
        print("DRY-RUN: git add와 commit을 실행하지 않았습니다.")
        print(f"예상 주소: {expected_pages_url(args.folder)}")
        return

    if not any(is_target_path(path, args.folder) for _status, path in changes):
        raise PublishError("새 동화 폴더에 Git 변경 사항이 없습니다.")

    add_paths = [args.folder, "index.html"]
    archive_style_changed = any(
        path == "archive-style.css" for _status, path in changes
    )
    if archive_style_changed:
        add_paths.append("archive-style.css")
    run_git(["add", "--", *add_paths])

    staged = staged_paths()
    allowed = {"index.html", "archive-style.css"}
    invalid = sorted(
        path
        for path in staged
        if not is_target_path(path, args.folder) and path not in allowed
    )
    if invalid:
        raise PublishError(
            "허용되지 않은 파일이 stage되었습니다: " + ", ".join(invalid)
        )
    if not staged:
        raise PublishError("commit할 stage 파일이 없습니다.")

    staged_check = run_git(["diff", "--cached", "--check"], check=False)
    if staged_check.returncode != 0:
        details = (staged_check.stdout or staged_check.stderr).strip()
        raise PublishError(
            "stage 파일의 git diff --check에 실패했습니다."
            + (f"\n{details}" if details else "")
        )

    print("stage된 파일:")
    for path in sorted(staged):
        print(f"  {path}")
    run_git(["commit", "-m", commit_message])
    commit_hash = git_value("rev-parse", "HEAD")
    print(f"Git commit 완료: {commit_hash}")


def command_verify_push(args):
    ensure_no_merge_or_conflict()
    ensure_remote_sync(False)
    local_main = git_value("rev-parse", "main")
    origin_main = git_value("rev-parse", "origin/main")
    if local_main != origin_main:
        raise PublishError("push 후 local main과 origin/main이 일치하지 않습니다.")
    print(f"배포 완료: {local_main}")
    print(f"예상 주소: {expected_pages_url(args.folder)}")


def build_parser():
    parser = argparse.ArgumentParser(description="해피팡 주간 동화 배포 검사")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, handler in (
        ("preflight", command_preflight),
        ("validate", command_validate),
        ("commit", command_commit),
    ):
        subparser = subparsers.add_parser(name)
        subparser.add_argument("folder")
        subparser.add_argument("--dry-run", action="store_true")
        subparser.set_defaults(handler=handler)

    verify_parser = subparsers.add_parser("verify-push")
    verify_parser.add_argument("folder")
    verify_parser.set_defaults(handler=command_verify_push)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.handler(args)
    except PublishError as error:
        print(f"오류: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
