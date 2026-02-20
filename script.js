// ===== 전역 변수 =====
let currentPage = 0;
const totalPages = 6;
let isMusicPlaying = false;
let youtubePlayer = null;
let isYouTubeReady = false;

// YouTube 동영상 ID (사용자 요청 찬양)
const YOUTUBE_VIDEO_ID = "HYX5UCfEWMg";

// ===== YouTube API 초기화 =====
function onYouTubeIframeAPIReady() {
    youtubePlayer = new YT.Player('youtube-player', {
        height: '0',
        width: '0',
        videoId: YOUTUBE_VIDEO_ID,
        playerVars: {
            autoplay: 0,
            controls: 0,
            loop: 1,
            playlist: YOUTUBE_VIDEO_ID,
            playsinline: 1
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}

function onPlayerReady(event) {
    isYouTubeReady = true;
    youtubePlayer.setVolume(100);
    youtubePlayer.unMute();
    console.log('YouTube 플레이어 준비 완료');
}

function onPlayerStateChange(event) {
    if (event.data === YT.PlayerState.ENDED) {
        youtubePlayer.playVideo();
    }
}

// DOM 요소
const imageSlides = document.querySelectorAll('.image-slide');
const textPages = document.querySelectorAll('.text-page');
const dots = document.querySelectorAll('.dot');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const musicToggle = document.getElementById('musicToggle');

// ===== 초기화 =====
function init() {
    // 이벤트 리스너 등록
    prevBtn.addEventListener('click', () => changePage(-1));
    nextBtn.addEventListener('click', () => changePage(1));
    musicToggle.addEventListener('click', toggleMusic);

    // 페이지 인디케이터 클릭
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => goToPage(index));
    });

    // 키보드 네비게이션
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') changePage(-1);
        if (e.key === 'ArrowRight') changePage(1);
    });

    // 터치 스와이프 지원
    let touchStartX = 0;
    let touchEndX = 0;

    const imageContainer = document.querySelector('.image-container');
    imageContainer.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    });

    imageContainer.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });

    function handleSwipe() {
        const swipeThreshold = 50;
        if (touchStartX - touchEndX > swipeThreshold) {
            changePage(1); // 왼쪽으로 스와이프 = 다음 페이지
        }
        if (touchEndX - touchStartX > swipeThreshold) {
            changePage(-1); // 오른쪽으로 스와이프 = 이전 페이지
        }
    }

    updateNavigationButtons();
}

// ===== 페이지 전환 함수 =====
function changePage(direction) {
    const newPage = currentPage + direction;

    // 범위 체크
    if (newPage < 0 || newPage >= totalPages) return;

    // 현재 페이지 숨기기
    imageSlides[currentPage].classList.remove('active');
    textPages[currentPage].classList.remove('active');
    dots[currentPage].classList.remove('active');

    // 새 페이지 표시
    currentPage = newPage;

    imageSlides[currentPage].classList.add('active');
    textPages[currentPage].classList.add('active');
    dots[currentPage].classList.add('active');

    updateNavigationButtons();

    // 페이지가 변경되면 맨 위로 스크롤
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ===== 특정 페이지로 이동 =====
function goToPage(pageIndex) {
    if (pageIndex === currentPage) return;

    // 현재 페이지 숨기기
    imageSlides[currentPage].classList.remove('active');
    textPages[currentPage].classList.remove('active');
    dots[currentPage].classList.remove('active');

    // 새 페이지 표시
    currentPage = pageIndex;

    imageSlides[currentPage].classList.add('active');
    textPages[currentPage].classList.add('active');
    dots[currentPage].classList.add('active');

    updateNavigationButtons();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ===== 네비게이션 버튼 업데이트 =====
function updateNavigationButtons() {
    prevBtn.disabled = currentPage === 0;
    nextBtn.disabled = currentPage === totalPages - 1;
}

// ===== 찬양 재생/정지 =====
function toggleMusic() {
    if (!isYouTubeReady || !youtubePlayer) {
        alert('찬양이 준비 중입니다. 잠시 후 다시 시도해주세요.');
        return;
    }

    if (isMusicPlaying) {
        // 찬양 정지
        youtubePlayer.pauseVideo();
        isMusicPlaying = false;
        musicToggle.classList.remove('playing');
    } else {
        // 찬양 재생
        youtubePlayer.unMute();
        youtubePlayer.playVideo();
        isMusicPlaying = true;
        musicToggle.classList.add('playing');
    }
}


// ===== 초기화 실행 =====
document.addEventListener('DOMContentLoaded', init);
