document.addEventListener('DOMContentLoaded', () => {

    // === Global Framework ===
    let currentSlide = 0; // Starts at 0 (Intro Cover)
    const totalSlides = 16; // 10 interactive scenes + 6 narrations

    // Intro Animation & BGM Start
    const btnStart = document.getElementById('btn-start-experience');
    const bgmPlayer = document.getElementById('bgm-player');
    
    if(btnStart) {
        gsap.from(".main-title .word", {y: 40, opacity: 0, duration: 0.8, stagger: 0.15, delay: 0.2, ease: "back.out(1.5)"});
        gsap.from(".episode-title", {opacity: 0, duration: 0.8, delay: 0.6});

        btnStart.addEventListener('click', () => {
            if(bgmPlayer) bgmPlayer.play().catch(e => console.log("BGM Error:", e));
            const btnMute = document.getElementById('btn-mute');
            if(btnMute) btnMute.classList.add('show');
            
            gsap.to("#slide0", {opacity: 0, duration: 0.8, onComplete: () => {
                document.getElementById('slide0').classList.add('hidden');
                document.getElementById('slide0').classList.remove('active');
                goToSlide(1); // Proceed to first story slide
            }});
        });
    }

    // Global Cursor Effect (Antigravity Style)
    const cursorGlow = document.querySelector('.cursor-glow');
    document.addEventListener('mousemove', (e) => {
        if(cursorGlow) {
            cursorGlow.style.opacity = 1;
            gsap.to(cursorGlow, {x: e.clientX, y: e.clientY, duration: 0.1, ease: 'power2.out'});
        }
    });

    function goToSlide(num) {
        document.querySelectorAll('.slide').forEach(s => {
            s.classList.remove('active');
            s.classList.add('hidden');
        });
        const nextSlide = document.getElementById('slide' + num);
        if(nextSlide) {
            nextSlide.classList.remove('hidden');
            setTimeout(() => nextSlide.classList.add('active'), 50);
            currentSlide = num;
            initSlide(num);
        }
    }

    // Attach Next Buttons globally (Up to 15 moving to 16)
    for(let i=1; i<totalSlides; i++) {
        const btn = document.getElementById(`btn-next-${i}`);
        if(btn) {
            btn.addEventListener('click', () => goToSlide(i+1));
        }
    }

    // Initialize logic that depends on elements being visible
    function initSlide(num) {
        if(num === 10) initTimer(); // Scene 6 -> Slide 10
        if(num === 13) initScene13Delay(); // Slide 13 (Emotional Pause)
        if(num === 14) setTimeout(initScratch, 300); // Slide 14 (Scratch Canvas)
    }

    // =====================================
    // Slide 1: Slider Any Movement
    // =====================================
    const slider = document.getElementById('mentalSlider');
    const btnNext1 = document.getElementById('btn-next-1');
    if(slider) {
        const initialValue = slider.value;
        slider.addEventListener('input', (e) => {
            if(Math.abs(e.target.value - initialValue) > 10) {
                btnNext1.classList.remove('hidden');
            }
        });
    }

    // =====================================
    // Slide 3 (formerly Scene 2): Crossfade
    // =====================================
    const btnAction3 = document.getElementById('btn-action-3');
    const bg3_2 = document.getElementById('s3-bg2');
    const btnNext3 = document.getElementById('btn-next-3');
    if(btnAction3) {
        btnAction3.addEventListener('click', () => {
            btnAction3.classList.add('hidden');
            gsap.to(bg3_2, { opacity: 1, duration: 1 });
            btnNext3.classList.remove('hidden');
        });
    }

    // =====================================
    // Slide 4 (formerly Scene 3): Scale Zoom Out
    // =====================================
    const btnAction4 = document.getElementById('btn-action-4');
    const btnNext4 = document.getElementById('btn-next-4');
    const s4Bg = document.getElementById('s4-bg');
    if(btnAction4) {
        btnAction4.addEventListener('click', () => {
            btnAction4.classList.add('hidden');
            gsap.to(s4Bg, { scale: 1.5, transformOrigin: 'center center', duration: 2, ease: "power2.out" });
            btnNext4.classList.remove('hidden');
        });
    }

    // =====================================
    // Slide 6 (formerly Scene 4): Panic Popup
    // =====================================
    const btnAction6 = document.getElementById('btn-action-6');
    const popup6 = document.getElementById('panic-popup');
    const close6 = document.getElementById('close-panic');
    const btnNext6 = document.getElementById('btn-next-6');
    
    if(btnAction6) {
        btnAction6.addEventListener('click', () => {
            popup6.classList.remove('hidden');
            gsap.fromTo(popup6, {scale: 0.8, opacity: 0}, {scale: 1, opacity: 1, duration: 0.3, ease: 'back.out'});
        });
        close6.addEventListener('click', () => {
            popup6.classList.add('hidden');
            btnAction6.classList.add('hidden');
            btnNext6.classList.remove('hidden');
        });
    }

    // =====================================
    // Slide 8 (formerly Scene 5): Quiz Input
    // =====================================
    const qInput = document.getElementById('quiz-input');
    const qBtn = document.getElementById('btn-action-8');
    const btnNext8 = document.getElementById('btn-next-8');
    
    if(qBtn) {
        qBtn.addEventListener('click', () => {
            if(qInput.value.trim().length >= 1) {
                qInput.disabled = true;
                qBtn.innerText = "훌륭합니다!";
                btnNext8.classList.remove('hidden');
            } else {
                qBtn.innerText = "🙏 글자를 적고 외쳐주세요!";
                setTimeout(() => qBtn.innerText = "외치기", 2000);
            }
        });
    }

    // =====================================
    // Slide 10 (formerly Scene 6): Humor Timer
    // =====================================
    const btnAction10 = document.getElementById('btn-action-10');
    const btnNext10 = document.getElementById('btn-next-10');
    const timerDisplay = document.getElementById('timer-display');
    
    function initTimer() {
        if(btnAction10) {
            btnAction10.addEventListener('click', () => {
                btnAction10.classList.add('hidden');
                let t = { val: 180 };
                gsap.to(t, {
                    val: 0,
                    duration: 3, 
                    ease: "power2.in",
                    onUpdate: () => {
                        let sec = Math.round(t.val);
                        let m = Math.floor(sec/60);
                        let s = sec%60;
                        timerDisplay.innerText = `0${m}:${s<10?'0'+s:s}`;
                        if(sec < 50) timerDisplay.style.color = "#ff4757";
                    },
                    onComplete: () => {
                        timerDisplay.innerText = "00:00";
                        gsap.to(timerDisplay, { y: 200, rotation: 15, opacity: 0, duration: 1, ease: "bounce.out"});
                        btnNext10.classList.remove('hidden');
                    }
                });
            }, {once: true});
        }
    }

    // =====================================
    // Slide 13: Emotional Delay
    // =====================================
    function initScene13Delay() {
        const btnNext13 = document.getElementById('btn-next-13');
        const guide = document.getElementById('s13-guide');
        if(guide) guide.innerText = "나의 연약함을 품으시는 주님의 사랑을 묵상해 보세요.";
        setTimeout(() => {
            if(guide) guide.innerText = "이제 흔들려도 괜찮습니다. 주님이 나의 바위이십니다.";
            btnNext13.classList.remove('hidden');
            gsap.fromTo(btnNext13, {opacity: 0}, {opacity: 1, duration: 1});
        }, 2500); // 2.5 second pause
    }

    // =====================================
    // Slide 14: Canvas Scratch
    // =====================================
    function initScratch() {
        const container = document.getElementById('scratch-container');
        const canvas = document.getElementById('scratch-pad');
        if(!canvas || !container) return;
        
        const ctx = canvas.getContext('2d');
        const btnNext14 = document.getElementById('btn-next-14');
        const guideAnim = document.querySelector('.scratch-guide');
        
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
        
        ctx.fillStyle = "rgba(0,0,0,0.95)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.globalCompositeOperation = 'destination-out';
        ctx.lineWidth = 40;
        ctx.lineJoin = "round";
        ctx.lineCap = "round";

        let isDrawing = false;
        let totalChecked = 0;
        let unlocked = false;

        function getPos(e) {
            const rect = canvas.getBoundingClientRect();
            let x = (e.clientX || (e.touches && e.touches[0].clientX)) - rect.left;
            let y = (e.clientY || (e.touches && e.touches[0].clientY)) - rect.top;
            return {x, y};
        }

        function draw(e) {
            if(!isDrawing || unlocked) return;
            e.preventDefault();
            const pos = getPos(e);
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
            
            totalChecked++;
            if(totalChecked % 15 === 0) checkUnlock();
        }

        canvas.addEventListener('mousedown', (e) => { isDrawing = true; ctx.beginPath(); ctx.moveTo(getPos(e).x, getPos(e).y); if(guideAnim) guideAnim.style.display='none';});
        canvas.addEventListener('mousemove', draw);
        canvas.addEventListener('mouseup', () => { isDrawing = false; checkUnlock(); });
        canvas.addEventListener('mouseleave', () => { isDrawing = false; });
        
        canvas.addEventListener('touchstart', (e) => { isDrawing = true; const p=getPos(e); ctx.beginPath(); ctx.moveTo(p.x, p.y); if(guideAnim) guideAnim.style.display='none';}, {passive: false});
        canvas.addEventListener('touchmove', draw, {passive: false});
        canvas.addEventListener('touchend', () => { isDrawing = false; checkUnlock(); });

        function checkUnlock() {
            if(unlocked) return;
            const pixels = ctx.getImageData(0,0, canvas.width, canvas.height).data;
            let clearCount = 0;
            const stride = 400; 
            for(let i=3; i<pixels.length; i+=stride) {
                if(pixels[i] < 128) clearCount++;
            }
            const percentCleared = clearCount / (pixels.length / stride);
            
            if(percentCleared > 0.35) { // 35% erased to unlock
                unlocked = true;
                gsap.to(canvas, {opacity: 0, duration: 1, onComplete: () => canvas.style.display = 'none'});
                btnNext14.classList.remove('hidden');
                document.getElementById('s14-guide').innerText = "어둠이 걷히고 새로운 길이 열립니다.";
            }
        }
    }

    // =====================================
    // Slide 15: Acrostic Check Logic
    // =====================================
    const inputs = document.querySelectorAll('.acrostic-input');
    const btnNext15 = document.getElementById('btn-next-15');

    if(inputs.length > 0) {
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                let allFilled = true;
                inputs.forEach(i => { if(i.value.trim() === "") allFilled = false; });
                
                if(allFilled) {
                    btnNext15.classList.remove('disabled');
                } else {
                    btnNext15.classList.add('disabled');
                }
            });
        });
    }

    // =====================================
    // Global Polishes: Mute & Restart
    // =====================================
    const btnMute = document.getElementById('btn-mute');
    if(btnMute && bgmPlayer) {
        btnMute.addEventListener('click', () => {
            if(bgmPlayer.muted) {
                bgmPlayer.muted = false;
                btnMute.innerText = "🔊";
            } else {
                bgmPlayer.muted = true;
                btnMute.innerText = "🔇";
            }
        });
    }

    const btnRestart = document.getElementById('btn-restart');
    if(btnRestart) {
        btnRestart.addEventListener('click', () => location.reload());
    }

});
