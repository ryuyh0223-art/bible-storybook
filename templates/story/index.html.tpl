<!DOCTYPE html>
<html lang="ko">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}} - 온라인 성경동화책</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
</head>

<body>
    <header class="header">
        <h1 class="title">{{EMOJI}} {{TITLE}}</h1>
        <button class="btn-music" id="musicToggle" aria-label="찬양" title="찬양 재생/정지">
            ♪
        </button>
    </header>

    <main class="main-content">
        <div class="book-container">
            <div class="image-container">
                <div class="image-slider" id="imageSlider">
{{IMAGE_SLIDES}}
                </div>
            </div>

            <div class="text-container" id="textContainer">
                <div class="text-page active">
                    <h2 class="page-title cover-title">{{TITLE}}</h2>
                    <div class="page-content center-align">
                        <p><strong>가정예배를 위한 준비:</strong> 아이를 무릎에 앉히고 편안한 분위기를 만들어주세요. 오른쪽 위 음악 버튼(♪)을 눌러 찬양을 틀어놓고 이야기 여행을 시작해 봅시다.</p>
                        <br>
                        <p><strong>주제 말씀:</strong> &quot;{{VERSE_TEXT}}&quot; ({{VERSE_REFERENCE}})</p>

                        <div class="prayer-box" style="text-align: left; margin-top: 2rem;">
                            <h3>🙏 성경동화 읽기 전 기도</h3>
{{OPENING_PRAYER}}
                        </div>
                    </div>
                </div>

{{SCENE_TEXT_PAGES}}
            </div>
        </div>

        <div class="navigation">
            <button class="nav-btn nav-prev" id="prevBtn" disabled aria-label="이전 페이지">‹</button>
            <div class="page-indicator" id="pageIndicator">
{{DOTS}}
            </div>
            <button class="nav-btn nav-next" id="nextBtn" aria-label="다음 페이지">›</button>
        </div>
    </main>

    <div id="youtube-player" style="position: fixed; bottom: 0; left: 0; pointer-events: none; opacity: 0;"></div>

    <script src="https://www.youtube.com/iframe_api"></script>
    <script src="script.js"></script>
</body>
</html>
