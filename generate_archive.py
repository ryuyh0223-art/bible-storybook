import os
import re
import datetime
import html as html_lib
import json
from pathlib import Path

# Exclude list
EXCLUDE_DIRS = {
    '.git',
    'bible-storybook-epilogue-rest',
    'dramatic-epilogue',
}
SUPPORTED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}

# JSON이 없는 기존 동화의 현재 표시 순서를 유지한다.
RECENT_FOLDERS = [
    'bible-storybook-shining-angel-face',
    'bible-storybook-one-in-gods-hand',
    'bible-storybook-special-telescope',
    'bible-storybook-word-is-best',
    'bible-storybook-real-king-comes',
]


class ArchiveGenerationError(Exception):
    """아카이브 생성을 중단해야 하는 입력 오류."""


def require_json_string(data, field_name, story_json_path):
    value = data.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ArchiveGenerationError(
            f"{story_json_path}: '{field_name}' 항목은 "
            "비어 있지 않은 문자열이어야 합니다."
        )
    return value.strip()


def find_exact_image(images_dir, filename, field_name):
    image_path = Path(filename)
    if image_path.name != filename or filename in {'.', '..'}:
        raise ArchiveGenerationError(
            f"'{field_name}'에는 assets/images 안의 파일명만 입력하세요: {filename}"
        )
    if image_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ArchiveGenerationError(
            f"지원하지 않는 이미지 확장자입니다: {filename}"
        )

    files = [item for item in images_dir.iterdir() if item.is_file()]
    exact_names = {item.name for item in files}
    if filename in exact_names:
        return filename

    case_matches = [
        name for name in exact_names if name.casefold() == filename.casefold()
    ]
    if case_matches:
        raise ArchiveGenerationError(
            f"이미지 파일명의 대소문자가 다릅니다. "
            f"JSON='{filename}', 실제='{case_matches[0]}'"
        )
    raise ArchiveGenerationError(
        f"표지 이미지를 찾을 수 없습니다: {images_dir / filename}"
    )


def find_legacy_thumbnail(images_dir):
    images = sorted(
        (
            item.name
            for item in images_dir.iterdir()
            if item.is_file()
            and item.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
        ),
        key=str.casefold,
    )
    if not images:
        return None

    preferred_stems = (
        'cover',
        'slide_00',
        'slide-00',
        'slide00',
        'slide_01',
        'slide-01',
        'slide01',
        '슬라이드1',
    )
    images_by_stem = {
        Path(filename).stem.casefold(): filename for filename in images
    }
    for stem in preferred_stems:
        match = images_by_stem.get(stem.casefold())
        if match:
            return match
    return images[0]


def read_json_metadata(folder, story_json_path, images_dir):
    try:
        with story_json_path.open('r', encoding='utf-8') as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ArchiveGenerationError(
            f"{story_json_path}: JSON 문법 오류 "
            f"({error.lineno}행 {error.colno}열): {error.msg}"
        ) from error
    except UnicodeDecodeError as error:
        raise ArchiveGenerationError(
            f"{story_json_path}: UTF-8 텍스트로 읽을 수 없습니다."
        ) from error
    except OSError as error:
        raise ArchiveGenerationError(
            f"{story_json_path}을 읽을 수 없습니다: {error}"
        ) from error

    if not isinstance(data, dict):
        raise ArchiveGenerationError(
            f"{story_json_path}: 최상위 JSON은 객체여야 합니다."
        )

    slug = require_json_string(data, 'slug', story_json_path)
    expected_folder = f'bible-storybook-{slug}'
    if folder != expected_folder:
        raise ArchiveGenerationError(
            f"{story_json_path}: slug와 폴더명이 맞지 않습니다. "
            f"예상 폴더명: {expected_folder}"
        )

    title = require_json_string(data, 'title', story_json_path)
    published_text = require_json_string(data, 'published', story_json_path)
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', published_text):
        raise ArchiveGenerationError(
            f"{story_json_path}: 'published'는 YYYY-MM-DD 형식이어야 합니다."
        )
    try:
        published = datetime.date.fromisoformat(published_text)
    except ValueError as error:
        raise ArchiveGenerationError(
            f"{story_json_path}: 'published'에 실제 날짜를 입력하세요."
        ) from error

    cover_image = require_json_string(data, 'cover_image', story_json_path)
    thumbnail = find_exact_image(
        images_dir, cover_image, 'cover_image'
    )
    return title, published, thumbnail

def get_stories():
    stories = []
    for d in os.listdir('.'):
        if os.path.isdir(d) and d.startswith('bible-storybook-') and d not in EXCLUDE_DIRS:
            index_path = os.path.join(d, 'index.html')
            if not os.path.exists(index_path):
                continue

            story_dir = Path(d)
            images_dir = story_dir / 'assets' / 'images'
            if not images_dir.is_dir():
                raise ArchiveGenerationError(
                    f"{d}: assets/images 폴더가 없습니다."
                )

            story_json_path = story_dir / 'story.json'
            published = None
            if story_json_path.is_file():
                title, published, thumbnail = read_json_metadata(
                    d, story_json_path, images_dir
                )
            else:
                with open(index_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                title_match = re.search(
                    r'<title>(.*?)(?: - 온라인 성경동화책)?</title>',
                    content,
                )
                title = (
                    html_lib.unescape(title_match.group(1).strip())
                    if title_match
                    else d
                )
                thumbnail = find_legacy_thumbnail(images_dir)

            if not thumbnail:
                raise ArchiveGenerationError(
                    f"{d}: 아카이브에 사용할 이미지를 찾을 수 없습니다."
                )

            thumbnail_path = f"{d}/assets/images/{thumbnail}"
            stories.append({
                'folder': d,
                'title': title,
                'thumbnail': thumbnail_path,
                'published': published,
            })

    def sort_key(x):
        folder = x['folder']
        if x['published'] is not None:
            return (0, -x['published'].toordinal(), folder)
        if folder in RECENT_FOLDERS:
            return (1, RECENT_FOLDERS.index(folder), '')
        return (2, 0, folder)

    stories.sort(key=sort_key)
    return stories

def generate_html(stories):
    cards_html = ""
    for story in stories:
        folder = html_lib.escape(story['folder'], quote=True)
        title = html_lib.escape(story['title'], quote=True)
        thumbnail = html_lib.escape(story['thumbnail'], quote=True)
        cards_html += f"""
            <a href="{folder}/index.html" class="story-card">
                <div class="card-image-wrapper">
                    <img src="{thumbnail}" alt="{title}" loading="lazy">
                    <div class="card-overlay">
                        <span class="read-btn">동화 읽기 ➔</span>
                    </div>
                </div>
                <div class="card-content">
                    <h3 class="card-title">{title}</h3>
                </div>
            </a>
        """

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>해피팡 성경동화</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="archive-style.css">
</head>
<body>
    <div class="background-decor"></div>
    <div class="background-decor decor-2"></div>
    
    <header class="main-header">
        <div class="header-content">
            <h1 class="main-title">✨ 해피팡 성경동화</h1>
            <p class="subtitle">우리 아이 마음에 쏙! 은혜가 팡팡 터지는 성경 이야기 모음</p>
        </div>
    </header>

    <main class="archive-container">
        <div class="grid-layout">
            {cards_html}
        </div>
    </main>

    <footer class="main-footer">
        <p>© 해피팡 성경동화. 모든 이야기는 하나님이 주신 특별한 선물입니다. 🎁</p>
    </footer>
</body>
</html>
"""
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def generate_css():
    css = """
:root {
    --primary: #6C5CE7;
    --primary-light: #A29BFE;
    --secondary: #FF9F43;
    --secondary-light: #FFC048;
    --text-main: #2D3436;
    --text-muted: #636E72;
    --bg-color: #F8F9FA;
    --card-bg: rgba(255, 255, 255, 0.85);
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: var(--bg-color);
    color: var(--text-main);
    line-height: 1.6;
    overflow-x: hidden;
    position: relative;
    min-height: 100vh;
}

/* Background Decorations (Glassmorphism blobs) */
.background-decor {
    position: fixed;
    top: -10%;
    left: -10%;
    width: 50vw;
    height: 50vw;
    background: radial-gradient(circle, var(--primary-light) 0%, rgba(162, 155, 254, 0) 70%);
    opacity: 0.3;
    z-index: -1;
    border-radius: 50%;
    filter: blur(60px);
}
.decor-2 {
    top: auto;
    bottom: -10%;
    left: auto;
    right: -10%;
    background: radial-gradient(circle, var(--secondary-light) 0%, rgba(255, 192, 72, 0) 70%);
    animation: float 8s ease-in-out infinite alternate;
}

@keyframes float {
    0% { transform: translateY(0px) scale(1); }
    100% { transform: translateY(-50px) scale(1.1); }
}

/* Header */
.main-header {
    text-align: center;
    padding: 4rem 1rem 3rem;
    position: relative;
    z-index: 10;
}

.main-title {
    font-size: 3rem;
    font-weight: 900;
    color: var(--primary);
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    letter-spacing: -1px;
}

.subtitle {
    font-size: 1.2rem;
    color: var(--text-muted);
    font-weight: 500;
}

/* Grid Layout */
.archive-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem 5rem;
    position: relative;
    z-index: 10;
}

.grid-layout {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 2rem;
}

/* Card Design */
.story-card {
    display: flex;
    flex-direction: column;
    background: var(--card-bg);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 20px;
    overflow: hidden;
    text-decoration: none;
    color: inherit;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    border: 1px solid rgba(255,255,255,0.5);
    position: relative;
}

.story-card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 20px 40px rgba(108, 92, 231, 0.15);
    border-color: var(--primary-light);
}

.card-image-wrapper {
    position: relative;
    width: 100%;
    padding-top: 75%; /* 4:3 Aspect Ratio */
    overflow: hidden;
    background: #e9ecef;
}

.card-image-wrapper img {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
}

.story-card:hover .card-image-wrapper img {
    transform: scale(1.08);
}

/* Overlay and Hover Button */
.card-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(108, 92, 231, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.story-card:hover .card-overlay {
    opacity: 1;
}

.read-btn {
    background: white;
    color: var(--primary);
    padding: 0.6rem 1.2rem;
    border-radius: 30px;
    font-weight: 700;
    font-size: 1rem;
    transform: translateY(20px);
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.story-card:hover .read-btn {
    transform: translateY(0);
}

/* Card Content */
.card-content {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    flex-grow: 1;
}

.card-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-main);
    line-height: 1.4;
    word-break: keep-all;
}

.story-card:hover .card-title {
    color: var(--primary);
}

/* Footer */
.main-footer {
    text-align: center;
    padding: 2rem;
    color: var(--text-muted);
    font-size: 0.9rem;
    position: relative;
    z-index: 10;
    background: rgba(255,255,255,0.5);
    backdrop-filter: blur(5px);
    margin-top: auto;
}

/* Responsive */
@media (max-width: 768px) {
    .main-title {
        font-size: 2.2rem;
    }
    .subtitle {
        font-size: 1rem;
    }
    .grid-layout {
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 1.5rem;
    }
    .archive-container {
        padding: 0 1rem 3rem;
    }
}
"""
    with open('archive-style.css', 'w', encoding='utf-8') as f:
        f.write(css)

if __name__ == "__main__":
    try:
        stories = get_stories()
        generate_html(stories)
        generate_css()
    except (ArchiveGenerationError, OSError) as error:
        print(f"오류: 아카이브를 생성할 수 없습니다: {error}")
        raise SystemExit(1)
    print(f"Archive generated with {len(stories)} stories!")
