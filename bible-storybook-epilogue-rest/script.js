const pages = [
    {
        image: "KakaoTalk_20260313_182657595.jpg", // Title image
        text: "<span class='title-text'>드라마틱<br>에필로그</span><br><br><span class='title-sub'>이번 주 고등부 설교, 우리 아이들 마음속엔 어떻게 남았을까요?</span>"
    },
    {
        image: "KakaoTalk_20260313_182657595_02.jpg",
        text: "[Scene 1]<br>토요일 새벽 1시 15분.<br>학원 끝나고 스카(스터디 카페)까지 돌다 집에 오면 파김치가 되죠."
    },
    {
        image: "KakaoTalk_20260313_182657595_01.jpg",
        text: "겨우 씻고 나와서 덜 마른 머리로 침대에 툭 눕습니다.<br>그리고 핸드폰 케이블 안 꺾이게 옆으로 누워 유튜브를 켜는 그 시간."
    },
    {
        image: "KakaoTalk_20260313_182657595_03.jpg",
        text: "도파민이 살짝 돌면서 뇌가 녹는 듯한 평온함이 찾아옵니다.<br><br>'아... 살 것 같다. 아무것도 안 하고 싶다. 이미 아무것도 안 하고 있지만, 더 격렬하게 아무것도 안 하고 싶다!'"
    },
    {
        image: "KakaoTalk_20260313_182657595_17.jpg",
        text: "힘들지 않은 사람은 없습니다. 에너지가 바닥나면 세상의 모든 요구가 다 부담스러워지고, 그냥 선을 딱 긋고 싶어지죠."
    },
    {
        image: "KakaoTalk_20260313_182657595_04.jpg",
        text: "[Scene 2]<br>2천 년 전, 예수님의 제자들도 딱 우리 같았습니다. 며칠을 쫄쫄 굶고 발바닥엔 물집이 터졌죠. 마침내 예수님이 '가서 좀 쉬어라!' 하시며 들캉스를 허락하셨습니다."
    },
    {
        image: "KakaoTalk_20260313_182657595_07.jpg",
        text: "그런데 배에서 내리려고 보니… 눈앞에 고척돔 매진 인원보다 많은 2만 명이 몰려와 살려달라고 아우성을 치고 있는 겁니다."
    },
    {
        image: "KakaoTalk_20260313_182657595_10.jpg",
        text: "어스름한 저녁, 참다못한 제자들이 이성적인 팩트로 찌릅니다. '예수님, 퇴근 시간 지났습니다. 이 사람들 다 마을로 보내서 밥 사 먹게 하시죠.'<br>그런데 예수님은 폭탄선언을 날리십니다. '너희가 밥을 줘라.'"
    },
    {
        image: "KakaoTalk_20260313_182657595_11.jpg",
        text: "'우리가요? 지금 여기서요? 이 인원 먹이려면 지금 돈으로 2천만 원(200 데나리온)이 드는데요?'<br>내 능력은 턱없이 부족한데, 2만 명을 먹이라는 요구! 새 학기를 맞은 우리 아이들의 진짜 현실과 똑같습니다."
    },
    {
        image: "KakaoTalk_20260313_182657595_12.jpg",
        text: "학교와 학원, 세상은 끊임없이 완벽한 스펙과 1등급이라는 '200 데나리온'의 청구서를 들이미는데, 내 능력은 못 따라가니 자꾸만 도망치고 싶어집니다. '전 안 돼요. 건드리지 마세요.'"
    },
    {
        image: "KakaoTalk_20260313_182657595_14.jpg",
        text: "[Scene 3]<br>예수님은 아이의 초라한 도시락, 보리떡 5개와 물고기 2마리를 가져오게 하십니다. 요즘으로 치면 편의점 소시지 2개랑 삼각김밥 5개 스케일이죠."
    },
    {
        image: "KakaoTalk_20260313_182657595_15.jpg",
        text: "고척돔 2만 명이 기대하며 쳐다보는데, 겨우 그따위 편의점 간식이라니? 너무 부끄럽습니다.<br>우리가 가진 실력, 스펙, 성적표가 세상의 요구 앞에서는 이 초라한 오병이어 같습니다."
    },
    {
        image: "KakaoTalk_20260313_182657595_19.jpg",
        text: "하지만 예수님은 비웃지 않으십니다. 찌질하고 부끄러운 나의 초라한 모습을 두 손으로 받아 쥐십니다. 그리고 빵을 찌지직! 거칠게 찢어버리십니다!"
    },
    {
        image: "KakaoTalk_20260313_182657595_21.jpg",
        text: "이 파열음은 다가올 십자가에서 당신의 온몸을 찢으시겠다는 외침입니다!<br>'사랑하는 내 아들아, 딸아! 네 능력으로는 세상을 이길 수 없단다. 내가 찢어질게. 내가 피 흘려 세상의 요구를 다 갚아낼게!'"
    },
    {
        image: "KakaoTalk_20260313_182657595_27.jpg",
        text: "[Scene 4]<br>실수하면 안 된다는 강박이 여러분의 숨을 옥죄고 있나요? 이제 내가 내 인생의 에이스가 될 필요가 없습니다. 십자가에서 모든 것을 완성하신 진짜 에이스, 예수님이 등판하셨습니다!"
    },
    {
        image: "KakaoTalk_20260313_182657595_28.jpg",
        text: "예수님이 기적 후 사람들을 눕힌 곳은 바닥이 아니라 '푸른 잔디'였습니다.<br>완벽해야 한다는 강박을 내려놓고, 나를 대신해 피 흘리신 예수님의 평안한 품('푸른 잔디')에 안기는 것. 그것이 진짜 '쉼'입니다."
    },
    {
        image: "KakaoTalk_20260313_182657595_29.jpg",
        text: "오늘 밤, 자녀와 서로 손을 잡고 내일을 응원해 주세요.<br><em>'네가 완벽해야 하나님이 사랑하시는 게 아니야. 우리 고민을 주님께 맡기고, 푸른 잔디 위에서 조금 쉬어가자.'</em>"
    }
];

let currentPage = 0;
const App = {
    container: document.getElementById('story-container'),
    pageIndicator: document.getElementById('page-indicator'),
    prevBtn: document.getElementById('prev-btn'),
    nextBtn: document.getElementById('next-btn'),

    init() {
        this.renderPage(currentPage);
        this.attachEventListeners();
        this.initAudio();
    },

    renderPage(index) {
        const page = pages[index];

        // 페이지 렌더링
        this.container.innerHTML = `
      <div class="page-content fade-in">
        <div class="image-wrapper">
          <img src="${page.image}" alt="이야기 일러스트" class="story-image">
        </div>
        <div class="text-wrapper">
          <p class="story-text">${page.text}</p>
        </div>
      </div>
    `;

        // 네비게이션 및 버튼 상태 업데이트
        this.pageIndicator.innerText = `${index + 1} / ${pages.length}`;
        if (index === pages.length - 1) {
            this.nextBtn.innerText = "처음으로";
        } else {
            this.nextBtn.innerText = "다음";
        }

        this.prevBtn.disabled = index === 0;
    },

    nextPage() {
        if (currentPage < pages.length - 1) {
            currentPage++;
            this.renderPage(currentPage);
        } else {
            // 마지막 페이지에서 '처음으로' 클릭 시
            currentPage = 0;
            this.renderPage(currentPage);
        }
    },

    prevPage() {
        if (currentPage > 0) {
            currentPage--;
            this.renderPage(currentPage);
        }
    },

    attachEventListeners() {
        this.nextBtn.addEventListener('click', () => this.nextPage());
        this.prevBtn.addEventListener('click', () => this.prevPage());

        // 스와이프 이벤트
        let touchStartX = 0;
        let touchEndX = 0;

        this.container.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        this.container.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe(touchStartX, touchEndX);
        }, { passive: true });
    },

    handleSwipe(startX, endX) {
        const swipeThreshold = 50;
        if (startX - endX > swipeThreshold) {
            // Swipe left (next)
            this.nextPage();
        } else if (endX - startX > swipeThreshold) {
            // Swipe right (prev)
            this.prevPage();
        }
    },

    initAudio() {
        const audio = document.getElementById('bg-music');
        const musicBtn = document.getElementById('music-btn');
        let isPlaying = false;

        musicBtn.addEventListener('click', () => {
            if (isPlaying) {
                audio.pause();
                musicBtn.innerText = '🎵 BGM 켜기';
            } else {
                audio.play().catch(e => console.log('Audio play failed:', e));
                musicBtn.innerText = '🔇 BGM 끄기';
            }
            isPlaying = !isPlaying;
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
