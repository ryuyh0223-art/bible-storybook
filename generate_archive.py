import os
import re
import datetime

# Exclude list
EXCLUDE_DIRS = ['.git', 'bible-storybook-epilogue-rest']

def get_stories():
    stories = []
    for d in os.listdir('.'):
        if os.path.isdir(d) and d.startswith('bible-storybook-') and d not in EXCLUDE_DIRS:
            index_path = os.path.join(d, 'index.html')
            if not os.path.exists(index_path):
                continue
            
            # Extract title
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            title_match = re.search(r'<title>(.*?)(?: - 온라인 성경동화책)?</title>', content)
            title = title_match.group(1).strip() if title_match else d
            
            # Find thumbnail
            thumbnail = None
            assets_dir = os.path.join(d, 'assets', 'images')
            if os.path.exists(assets_dir):
                images = [f for f in os.listdir(assets_dir) if f.endswith('.png') or f.endswith('.jpg')]
                # Prefer slide_00.png or slide_01.png
                preferred = [f for f in images if '00' in f or '01' in f or '1' in f]
                if preferred:
                    thumbnail = sorted(preferred)[0]
                elif images:
                    thumbnail = sorted(images)[0]
            
            if thumbnail:
                thumbnail_path = f"{d}/assets/images/{thumbnail}"
            else:
                thumbnail_path = "default-thumbnail.png"
                
            # We'll use a hardcoded order or just sort by modification time (or creation time if available on Mac)
            # To get a pseudo reverse-chronological order, let's sort by folder mtime, but actually git clone destroys mtime.
            # So I will hardcode the latest one, and just alphabetical for the rest, or just use the current order.
            
            stories.append({
                'folder': d,
                'title': title,
                'thumbnail': thumbnail_path
            })
            
    # List recent folders in order from newest to oldest
    RECENT_FOLDERS = [
        'bible-storybook-one-in-gods-hand',
        'bible-storybook-special-telescope',
        'bible-storybook-word-is-best',
        'bible-storybook-real-king-comes'
    ]
    
    def sort_key(x):
        folder = x['folder']
        if folder in RECENT_FOLDERS:
            return (0, RECENT_FOLDERS.index(folder))
        else:
            return (1, folder)

    stories.sort(key=sort_key)
    return stories

def generate_html(stories):
    cards_html = ""
    for story in stories:
        cards_html += f"""
            <a href="{story['folder']}/index.html" class="story-card">
                <div class="card-image-wrapper">
                    <img src="{story['thumbnail']}" alt="{story['title']}" loading="lazy">
                    <div class="card-overlay">
                        <span class="read-btn">동화 읽기 ➔</span>
                    </div>
                </div>
                <div class="card-content">
                    <h3 class="card-title">{story['title']}</h3>
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
    stories = get_stories()
    generate_html(stories)
    generate_css()
    print(f"Archive generated with {len(stories)} stories!")
