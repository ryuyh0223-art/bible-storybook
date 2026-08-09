import datetime
import html
import json
import re
import shutil
import sys
from pathlib import Path


SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
PLACEHOLDER_PATTERN = re.compile(r"{{[A-Z0-9_]+}}")
OUTPUT_FILENAMES = ("index.html", "style.css", "script.js")


class StoryGenerationError(Exception):
    """사용자가 수정할 수 있는 입력 오류."""


def require_object(value, field_name):
    if not isinstance(value, dict):
        raise StoryGenerationError(f"'{field_name}' 항목은 JSON 객체여야 합니다.")
    return value


def require_string(container, field_name):
    if field_name not in container:
        raise StoryGenerationError(f"필수 항목 '{field_name}'이(가) 없습니다.")
    value = container[field_name]
    if not isinstance(value, str) or not value.strip():
        raise StoryGenerationError(
            f"'{field_name}' 항목은 비어 있지 않은 문자열이어야 합니다."
        )
    return value.strip()


def require_string_list(container, field_name):
    if field_name not in container:
        raise StoryGenerationError(f"필수 항목 '{field_name}'이(가) 없습니다.")
    value = container[field_name]
    if not isinstance(value, list) or not value:
        raise StoryGenerationError(
            f"'{field_name}' 항목은 문자열이 하나 이상 들어 있는 배열이어야 합니다."
        )

    result = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, str) or not item.strip():
            raise StoryGenerationError(
                f"'{field_name}' 배열의 {index}번째 값은 비어 있지 않은 문자열이어야 합니다."
            )
        result.append(item.strip())
    return result


def load_story_json(story_json_path):
    try:
        with story_json_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise StoryGenerationError(
            f"JSON 문법 오류가 있습니다. {error.lineno}행 {error.colno}열을 확인하세요: "
            f"{error.msg}"
        ) from error
    except UnicodeDecodeError as error:
        raise StoryGenerationError(
            "story.json을 UTF-8 텍스트로 읽을 수 없습니다. "
            "파일 인코딩을 UTF-8로 저장하세요."
        ) from error
    except OSError as error:
        raise StoryGenerationError(f"story.json을 읽을 수 없습니다: {error}") from error

    return require_object(data, "최상위 JSON")


def validate_published(value):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise StoryGenerationError("'published'는 YYYY-MM-DD 형식이어야 합니다.")
    try:
        datetime.date.fromisoformat(value)
    except ValueError as error:
        raise StoryGenerationError(
            "'published'에 실제로 존재하는 날짜를 입력하세요."
        ) from error


def validate_image_filename(filename, field_name, images_dir):
    path = Path(filename)
    if path.name != filename or filename in {".", ".."}:
        raise StoryGenerationError(
            f"'{field_name}'에는 assets/images 안의 파일명만 입력하세요: {filename}"
        )
    if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_IMAGE_EXTENSIONS))
        raise StoryGenerationError(
            f"'{field_name}' 이미지 확장자를 지원하지 않습니다: {filename} "
            f"(지원: {supported})"
        )

    files = [item for item in images_dir.iterdir() if item.is_file()]
    exact_names = {item.name for item in files}
    if filename in exact_names:
        return

    case_matches = [
        name for name in exact_names if name.casefold() == filename.casefold()
    ]
    if case_matches:
        raise StoryGenerationError(
            f"'{field_name}'의 파일명 대소문자가 실제 파일과 다릅니다: "
            f"JSON='{filename}', 실제='{case_matches[0]}'"
        )
    raise StoryGenerationError(
        f"'{field_name}' 이미지가 assets/images에 없습니다: {filename}"
    )


def validate_story(
    data, story_json_path, repository_root, allow_generated_files=False
):
    if story_json_path.name != "story.json":
        raise StoryGenerationError("입력 파일 이름은 'story.json'이어야 합니다.")

    story_dir = story_json_path.parent
    if story_dir.parent.resolve() != repository_root:
        raise StoryGenerationError(
            "story.json은 저장소 루트 바로 아래의 "
            "bible-storybook-<slug> 폴더에 있어야 합니다."
        )

    slug = require_string(data, "slug")
    if not SLUG_PATTERN.fullmatch(slug):
        raise StoryGenerationError(
            "'slug'는 영문 소문자, 숫자, 하이픈만 사용할 수 있으며 "
            "하이픈으로 시작하거나 끝날 수 없습니다."
        )

    expected_folder_name = f"bible-storybook-{slug}"
    if story_dir.name != expected_folder_name:
        raise StoryGenerationError(
            f"폴더명이 slug와 맞지 않습니다. 예상 폴더명: {expected_folder_name}"
        )

    allowed_entries = {"story.json", "assets"}
    if allow_generated_files:
        allowed_entries.update(OUTPUT_FILENAMES)

    unexpected_entries = sorted(
        item.name
        for item in story_dir.iterdir()
        if item.name not in allowed_entries
    )
    if unexpected_entries:
        raise StoryGenerationError(
            "기존 동화 폴더를 덮어쓰지 않기 위해 생성을 중단했습니다. "
            "새 폴더에는 story.json과 assets만 있어야 합니다. "
            f"발견된 항목: {', '.join(unexpected_entries)}"
        )

    assets_dir = story_dir / "assets"
    images_dir = assets_dir / "images"
    if not images_dir.is_dir():
        raise StoryGenerationError("assets/images 폴더가 없습니다.")

    title = require_string(data, "title")
    emoji = require_string(data, "emoji")
    published = require_string(data, "published")
    validate_published(published)
    cover_image = require_string(data, "cover_image")
    validate_image_filename(cover_image, "cover_image", images_dir)

    if "verse" not in data:
        raise StoryGenerationError("필수 항목 'verse'가 없습니다.")
    verse = require_object(data["verse"], "verse")
    verse_text = require_string(verse, "text")
    verse_reference = require_string(verse, "reference")

    opening_prayer = require_string_list(data, "opening_prayer")
    questions = require_string_list(data, "questions")
    closing_prayer = require_string_list(data, "closing_prayer")

    if "scenes" not in data:
        raise StoryGenerationError("필수 항목 'scenes'가 없습니다.")
    raw_scenes = data["scenes"]
    if not isinstance(raw_scenes, list) or not raw_scenes:
        raise StoryGenerationError(
            "'scenes' 항목은 장면이 하나 이상 들어 있는 배열이어야 합니다."
        )

    scenes = []
    for index, raw_scene in enumerate(raw_scenes, start=1):
        scene = require_object(raw_scene, f"scenes[{index}]")
        image = require_string(scene, "image")
        alt = require_string(scene, "alt")
        paragraphs = require_string_list(scene, "paragraphs")
        validate_image_filename(image, f"scenes[{index}].image", images_dir)
        scenes.append({"image": image, "alt": alt, "paragraphs": paragraphs})

    return {
        "slug": slug,
        "title": title,
        "emoji": emoji,
        "published": published,
        "cover_image": cover_image,
        "verse_text": verse_text,
        "verse_reference": verse_reference,
        "opening_prayer": opening_prayer,
        "scenes": scenes,
        "questions": questions,
        "closing_prayer": closing_prayer,
        "story_dir": story_dir,
    }


def escaped(value):
    return html.escape(value, quote=True)


def render_paragraphs(paragraphs, indentation):
    return "\n".join(
        f"{indentation}<p>{escaped(paragraph)}</p>" for paragraph in paragraphs
    )


def render_story(template, story):
    image_slides = [
        '                    <div class="image-slide active">'
        f'<img src="assets/images/{escaped(story["cover_image"])}" '
        f'alt="표지: {escaped(story["title"])}" loading="lazy"></div>'
    ]
    for scene in story["scenes"]:
        image_slides.append(
            '                    <div class="image-slide">'
            f'<img src="assets/images/{escaped(scene["image"])}" '
            f'alt="{escaped(scene["alt"])}" loading="lazy"></div>'
        )

    text_pages = []
    last_scene_index = len(story["scenes"]) - 1
    for index, scene in enumerate(story["scenes"]):
        page_lines = [
            '                <div class="text-page">',
            '                    <div class="page-content">',
            render_paragraphs(scene["paragraphs"], "                        "),
        ]
        if index == last_scene_index:
            page_lines.extend(
                [
                    "",
                    '                        <div class="highlight-box">',
                    "                            <h3>📌 함께 나누는 질문</h3>",
                    render_paragraphs(
                        story["questions"], "                            "
                    ),
                    "                        </div>",
                    '                        <div class="prayer-box">',
                    "                            <h3>🙏 마무리 기도</h3>",
                    render_paragraphs(
                        story["closing_prayer"], "                            "
                    ),
                    "                        </div>",
                ]
            )
        page_lines.extend(
            ["                    </div>", "                </div>"]
        )
        text_pages.append("\n".join(page_lines))

    page_count = 1 + len(story["scenes"])
    dots = ['                <span class="dot active"></span>']
    dots.extend(
        '                <span class="dot"></span>'
        for _ in range(page_count - 1)
    )

    replacements = {
        "{{TITLE}}": escaped(story["title"]),
        "{{EMOJI}}": escaped(story["emoji"]),
        "{{VERSE_TEXT}}": escaped(story["verse_text"]),
        "{{VERSE_REFERENCE}}": escaped(story["verse_reference"]),
        "{{OPENING_PRAYER}}": render_paragraphs(
            story["opening_prayer"], "                            "
        ),
        "{{IMAGE_SLIDES}}": "\n".join(image_slides),
        "{{SCENE_TEXT_PAGES}}": "\n\n".join(text_pages),
        "{{DOTS}}": "\n".join(dots),
    }

    rendered = template
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)

    unresolved = sorted(set(PLACEHOLDER_PATTERN.findall(rendered)))
    if unresolved:
        raise StoryGenerationError(
            f"템플릿에 치환되지 않은 항목이 있습니다: {', '.join(unresolved)}"
        )
    return rendered, page_count


def count_class(html_text, class_name):
    class_attributes = re.findall(r'class=["\']([^"\']*)["\']', html_text)
    return sum(class_name in classes.split() for classes in class_attributes)


def verify_generated_html(html_text, expected_page_count):
    counts = {
        ".image-slide": count_class(html_text, "image-slide"),
        ".text-page": count_class(html_text, "text-page"),
        ".dot": count_class(html_text, "dot"),
    }
    if any(count != expected_page_count for count in counts.values()):
        details = ", ".join(
            f"{name}={count}" for name, count in counts.items()
        )
        raise StoryGenerationError(
            f"생성 후 페이지 개수 검증에 실패했습니다. "
            f"예상={expected_page_count}, {details}"
        )


def generate_story(story_json_argument, validate_only=False):
    repository_root = Path(__file__).resolve().parent
    story_json_path = Path(story_json_argument).expanduser().resolve()
    if not story_json_path.is_file():
        raise StoryGenerationError(
            f"story.json 파일을 찾을 수 없습니다: {story_json_argument}"
        )

    data = load_story_json(story_json_path)
    story = validate_story(
        data,
        story_json_path,
        repository_root,
        allow_generated_files=validate_only,
    )

    template_dir = repository_root / "templates" / "story"
    template_path = template_dir / "index.html.tpl"
    template_style_path = template_dir / "style.css"
    template_script_path = template_dir / "script.js"
    for required_path in (
        template_path,
        template_style_path,
        template_script_path,
    ):
        if not required_path.is_file():
            raise StoryGenerationError(
                f"필수 템플릿 파일이 없습니다: {required_path}"
            )

    story_dir = story["story_dir"]
    output_paths = [
        story_dir / filename for filename in OUTPUT_FILENAMES
    ]
    existing_outputs = [path.name for path in output_paths if path.exists()]
    if existing_outputs and not validate_only:
        raise StoryGenerationError(
            "기존 동화 파일은 덮어쓸 수 없습니다. 이미 존재하는 파일: "
            + ", ".join(existing_outputs)
        )

    if validate_only:
        missing_outputs = [
            path.name for path in output_paths if not path.is_file()
        ]
        if missing_outputs:
            raise StoryGenerationError(
                "검증할 생성 파일이 없습니다: " + ", ".join(missing_outputs)
            )

    try:
        template = template_path.read_text(encoding="utf-8")
    except OSError as error:
        raise StoryGenerationError(
            f"HTML 템플릿을 읽을 수 없습니다: {error}"
        ) from error

    rendered_html, page_count = render_story(template, story)
    verify_generated_html(rendered_html, page_count)

    if validate_only:
        index_path, style_path, script_path = output_paths
        try:
            generated_html = index_path.read_text(encoding="utf-8")
            generated_style = style_path.read_text(encoding="utf-8")
            generated_script = script_path.read_text(encoding="utf-8")
            template_style = template_style_path.read_text(encoding="utf-8")
            template_script = template_script_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise StoryGenerationError(
                f"생성된 동화 파일을 검증할 수 없습니다: {error}"
            ) from error

        verify_generated_html(generated_html, page_count)
        mismatches = []
        if generated_html != rendered_html:
            mismatches.append("index.html")
        if generated_style != template_style:
            mismatches.append("style.css")
        if generated_script != template_script:
            mismatches.append("script.js")
        if mismatches:
            raise StoryGenerationError(
                "story.json 또는 현재 템플릿과 다른 생성 파일이 있습니다: "
                + ", ".join(mismatches)
            )
        return story_dir.name, page_count

    created_paths = []
    try:
        index_path, style_path, script_path = output_paths
        with index_path.open("x", encoding="utf-8", newline="\n") as file:
            created_paths.append(index_path)
            file.write(rendered_html)
        created_paths.append(style_path)
        shutil.copy2(template_style_path, style_path)
        created_paths.append(script_path)
        shutil.copy2(template_script_path, script_path)

        generated_html = index_path.read_text(encoding="utf-8")
        verify_generated_html(generated_html, page_count)
    except (OSError, StoryGenerationError) as error:
        for path in reversed(created_paths):
            try:
                path.unlink()
            except OSError:
                pass
        if isinstance(error, StoryGenerationError):
            raise
        raise StoryGenerationError(
            f"동화 파일을 생성할 수 없습니다: {error}"
        ) from error

    return story_dir.name, page_count


def main():
    validate_only = len(sys.argv) == 3 and sys.argv[1] == "--validate-only"
    if not (len(sys.argv) == 2 or validate_only):
        print(
            "사용법: python generate_story.py "
            "bible-storybook-<slug>/story.json"
        )
        print(
            "검증: python generate_story.py --validate-only "
            "bible-storybook-<slug>/story.json"
        )
        return 2

    story_json_argument = sys.argv[2] if validate_only else sys.argv[1]

    try:
        folder_name, page_count = generate_story(
            story_json_argument, validate_only=validate_only
        )
    except StoryGenerationError as error:
        print(f"오류: {error}")
        return 1
    except OSError as error:
        print(f"오류: 파일이나 폴더를 확인할 수 없습니다: {error}")
        return 1

    if validate_only:
        print(
            f"검증 성공: '{folder_name}' 생성 파일이 story.json 및 템플릿과 "
            f"일치합니다. 총 페이지 수: {page_count}"
        )
    else:
        print(
            f"성공: '{folder_name}' 동화 폴더를 생성했습니다. "
            f"총 페이지 수: {page_count}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
