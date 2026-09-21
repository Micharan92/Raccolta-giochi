"""Gioco: Snake - il classico gioco dei telefoni Nokia."""

import streamlit as st


def render():
    """Interfaccia Streamlit per 'Snake' con canvas HTML5."""
    st.subheader("🐍 Snake")
    st.caption(
        "Mangia il cibo rosso e raggiungi **450 punti**. "
        "**PC:** SPAZIO + frecce/WASD · **Mobile:** ▶ e D-pad sotto il campo."
    )

    # Game HTML/JavaScript — colonna verticale (frecce sotto), altezza iframe adattiva
    game_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <style>
            * { box-sizing: border-box; }
            html, body {
                margin: 0;
                padding: 0;
                overflow: visible;
                font-family: Arial, sans-serif;
                background-color: #0e0e0e;
            }
            #gameContainer {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
                width: 100%;
                max-width: min(580px, 100%);
                margin: 0 auto;
                padding: 6px 8px 18px;
            }
            canvas {
                border: 3px solid #444;
                background-color: #1a1a1a;
                display: block;
                width: min(560px, calc(100vw - 24px));
                max-width: 100%;
                aspect-ratio: 4 / 3;
                height: auto;
                touch-action: none;
            }
            #controlsBlock {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 6px;
                width: 100%;
            }
            #stats {
                display: flex;
                gap: 20px;
                font-size: 16px;
                font-weight: bold;
                color: #fff;
                flex-wrap: wrap;
                justify-content: center;
            }
            .stat { display: flex; gap: 6px; }
            .stat-label { color: #999; }
            .stat-value { color: #00ff00; }
            #message {
                font-size: 16px;
                font-weight: bold;
                min-height: 24px;
                line-height: 1.35;
                text-align: center;
                color: #fff;
                width: 100%;
            }
            .success { color: #00ff00; }
            .error { color: #ff6b6b; }
            #startBtn {
                background: #1a7a3e;
                color: #fff;
                border: 2px solid #00ff00;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 15px;
                font-weight: bold;
                cursor: pointer;
                touch-action: manipulation;
                user-select: none;
                width: 100%;
                max-width: 240px;
            }
            #startBtn:active { background: #145f30; }
            #dpad {
                display: grid;
                grid-template-columns: repeat(3, 44px);
                grid-template-rows: repeat(3, 44px);
                gap: 4px;
            }
            .dpad-btn {
                background: #222;
                color: #fff;
                border: 2px solid #444;
                border-radius: 7px;
                font-size: 18px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                touch-action: manipulation;
                user-select: none;
                -webkit-tap-highlight-color: transparent;
            }
            .dpad-btn:active { background: #1a7a3e; border-color: #00ff00; }
            .dpad-empty { visibility: hidden; pointer-events: none; }
            #controls-hint {
                font-size: 12px;
                line-height: 1.4;
                color: #666;
                text-align: center;
            }

            @media (min-width: 769px) {
                canvas { width: 560px; }
                #gameContainer { gap: 9px; padding-bottom: 12px; }
            }

            @media (max-width: 768px) {
                #gameContainer {
                    gap: 8px;
                    padding: 4px 6px 12px;
                }
                canvas {
                    width: min(560px, calc(100vw - 16px));
                }
                #startBtn {
                    min-height: 44px;
                    max-width: min(280px, 100%);
                    font-size: 1rem;
                }
                #dpad {
                    grid-template-columns: repeat(3, min(48px, 13vw));
                    grid-template-rows: repeat(3, min(48px, 13vw));
                    gap: 5px;
                }
                .dpad-btn { font-size: 1.15rem; border-radius: 8px; }
                #message { font-size: 0.92rem; min-height: 1.75rem; }
            }
        </style>
    </head>
    <body>
        <div id="gameContainer">
            <canvas id="gameCanvas" width="560" height="420"></canvas>
            <div id="stats">
                <div class="stat">
                    <span class="stat-label">Punteggio:</span>
                    <span class="stat-value" id="score">0</span>
                    <span class="stat-label">/ 450</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Lunghezza:</span>
                    <span class="stat-value" id="length">1</span>
                </div>
            </div>
            <div id="controlsBlock">
                <div id="message">Premi ▶ o SPAZIO per iniziare</div>
                <button id="startBtn">▶ Inizia</button>
                <div id="dpad">
                    <div class="dpad-empty"></div>
                    <div class="dpad-btn" id="btn-up">↑</div>
                    <div class="dpad-empty"></div>
                    <div class="dpad-btn" id="btn-left">←</div>
                    <div class="dpad-empty"></div>
                    <div class="dpad-btn" id="btn-right">→</div>
                    <div class="dpad-empty"></div>
                    <div class="dpad-btn" id="btn-down">↓</div>
                    <div class="dpad-empty"></div>
                </div>
                <div id="controls-hint">PC: Frecce / WASD + SPAZIO &nbsp;|&nbsp; Mobile: D-pad o swipe</div>
            </div>
        </div>

        <script>
            const canvas = document.getElementById('gameCanvas');
            const ctx = canvas.getContext('2d');

            const GRID_WIDTH = 25;
            const GRID_HEIGHT = 18; // 25 × 18 = 450 caselle
            const MAX_SCORE = 450;
            const GAME_SPEED = 150;

            canvas.width = 560;
            canvas.height = 420;
            const CELL_W = canvas.width / GRID_WIDTH;
            const CELL_H = canvas.height / GRID_HEIGHT;

            function cellPx(x, y) {
                return {
                    x: x * CELL_W + 1,
                    y: y * CELL_H + 1,
                    w: CELL_W - 2,
                    h: CELL_H - 2,
                };
            }

            let snake = [{x: Math.floor(GRID_WIDTH/2), y: Math.floor(GRID_HEIGHT/2)}];
            let direction = {x: 1, y: 0};
            let nextDirection = {x: 1, y: 0};
            let food = generateFood();
            let score = 0;
            let gameOver = false;
            let gameWon = false;
            let running = false;
            let lastMoveTime = Date.now();
            let growthPending = 0;

            function generateFood() {
                let x, y, valid;
                do {
                    valid = true;
                    x = Math.floor(Math.random() * GRID_WIDTH);
                    y = Math.floor(Math.random() * GRID_HEIGHT);
                    for (let segment of snake) {
                        if (segment.x === x && segment.y === y) {
                            valid = false;
                            break;
                        }
                    }
                } while (!valid);
                return {x: x, y: y};
            }

            function updateGame() {
                if (!running || gameOver || gameWon) return;

                const now = Date.now();
                if (now - lastMoveTime < GAME_SPEED) return;

                direction = nextDirection;
                
                const head = snake[0];
                const newHead = {
                    x: head.x + direction.x,
                    y: head.y + direction.y
                };

                // Collisione muri
                if (newHead.x < 0 || newHead.x >= GRID_WIDTH || newHead.y < 0 || newHead.y >= GRID_HEIGHT) {
                    gameOver = true;
                    return;
                }

                // Collisione corpo
                for (let segment of snake) {
                    if (newHead.x === segment.x && newHead.y === segment.y) {
                        gameOver = true;
                        return;
                    }
                }

                snake.unshift(newHead);

                // Mangia cibo
                if (newHead.x === food.x && newHead.y === food.y) {
                    score += 2;
                    if (score >= MAX_SCORE) {
                        gameWon = true;
                        return;
                    }
                    food = generateFood();
                    growthPending += 1;
                } else {
                    if (growthPending > 0) {
                        growthPending--;
                    } else {
                        snake.pop();
                    }
                }

                lastMoveTime = now;
            }

            function draw() {
                // Sfondo
                ctx.fillStyle = '#1a1a1a';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                // Griglia (450 caselle, a filo con i bordi del canvas)
                ctx.strokeStyle = '#222';
                ctx.lineWidth = 1;
                for (let i = 0; i <= GRID_WIDTH; i++) {
                    const x = i * CELL_W;
                    ctx.beginPath();
                    ctx.moveTo(x, 0);
                    ctx.lineTo(x, canvas.height);
                    ctx.stroke();
                }
                for (let i = 0; i <= GRID_HEIGHT; i++) {
                    const y = i * CELL_H;
                    ctx.beginPath();
                    ctx.moveTo(0, y);
                    ctx.lineTo(canvas.width, y);
                    ctx.stroke();
                }

                // Serpente
                snake.forEach((segment, index) => {
                    if (index === 0) {
                        ctx.fillStyle = '#00ff00';
                        ctx.shadowColor = '#00ff00';
                        ctx.shadowBlur = 10;
                    } else {
                        ctx.fillStyle = '#00cc00';
                        ctx.shadowColor = 'transparent';
                    }
                    const c = cellPx(segment.x, segment.y);
                    ctx.fillRect(c.x, c.y, c.w, c.h);
                });
                ctx.shadowColor = 'transparent';

                // Cibo
                ctx.fillStyle = '#ff6b6b';
                ctx.shadowColor = '#ff6b6b';
                ctx.shadowBlur = 10;
                const f = cellPx(food.x, food.y);
                ctx.fillRect(f.x, f.y, f.w, f.h);
                ctx.shadowColor = 'transparent';

                // Stats
                document.getElementById('score').textContent = score;
                document.getElementById('length').textContent = snake.length;

                // Messaggio + aggiorna pulsante
                const msgDiv = document.getElementById('message');
                if (gameWon) {
                    msgDiv.textContent = '🎉 HAI VINTO! Hai raggiunto 450 punti!';
                    msgDiv.className = 'success';
                    updateStartBtn();
                } else if (gameOver) {
                    msgDiv.textContent = `💀 GAME OVER! Punteggio: ${score}`;
                    msgDiv.className = 'error';
                    updateStartBtn();
                } else if (!running) {
                    msgDiv.textContent = 'Premi ▶ o SPAZIO per iniziare';
                    msgDiv.className = '';
                } else {
                    msgDiv.textContent = '';
                }
            }

            function gameLoop() {
                updateGame();
                draw();
                requestAnimationFrame(gameLoop);
            }

            // ── Funzione reset ──────────────────────────────────────────
            function resetGame(autoStart) {
                snake = [{x: Math.floor(GRID_WIDTH/2), y: Math.floor(GRID_HEIGHT/2)}];
                direction = {x: 1, y: 0};
                nextDirection = {x: 1, y: 0};
                food = generateFood();
                score = 0;
                gameOver = false;
                gameWon = false;
                growthPending = 0;
                lastMoveTime = Date.now();
                running = !!autoStart;
                updateStartBtn();
            }

            function updateStartBtn() {
                const btn = document.getElementById('startBtn');
                if (gameOver || gameWon) {
                    btn.textContent = '🔄 Rigioca';
                } else if (running) {
                    btn.textContent = '⏸ Pausa';
                } else {
                    btn.textContent = '▶ Inizia';
                }
            }

            // ── Pulsante Start/Pausa/Reset ───────────────────────────────
            document.getElementById('startBtn').addEventListener('click', () => {
                if (gameOver || gameWon) {
                    resetGame(true);
                } else {
                    running = !running;
                }
                updateStartBtn();
            });

            // ── Input tastiera (PC) ──────────────────────────────────────
            document.addEventListener('keydown', (e) => {
                if (e.key === ' ') {
                    e.preventDefault();
                    if (gameOver || gameWon) {
                        resetGame(true);
                    } else {
                        running = !running;
                    }
                    updateStartBtn();
                    return;
                }
                const keyMap = {
                    'ArrowUp': {x: 0, y: -1}, 'ArrowDown': {x: 0, y: 1},
                    'ArrowLeft': {x: -1, y: 0}, 'ArrowRight': {x: 1, y: 0},
                    'w': {x: 0, y: -1}, 'W': {x: 0, y: -1},
                    'a': {x: -1, y: 0}, 'A': {x: -1, y: 0},
                    's': {x: 0, y: 1}, 'S': {x: 0, y: 1},
                    'd': {x: 1, y: 0}, 'D': {x: 1, y: 0}
                };
                if (keyMap[e.key]) {
                    const newDir = keyMap[e.key];
                    if (!(direction.x === -newDir.x && direction.y === -newDir.y)) {
                        nextDirection = newDir;
                        if (!running && !gameOver && !gameWon) { running = true; updateStartBtn(); }
                    }
                    e.preventDefault();
                }
            });

            // ── D-pad touch (mobile) ─────────────────────────────────────
            const dpadMap = {
                'btn-up':    {x: 0,  y: -1},
                'btn-down':  {x: 0,  y:  1},
                'btn-left':  {x: -1, y:  0},
                'btn-right': {x: 1,  y:  0},
            };
            Object.keys(dpadMap).forEach(id => {
                const btn = document.getElementById(id);
                function pressDir(e) {
                    e.preventDefault();
                    const newDir = dpadMap[id];
                    if (!(direction.x === -newDir.x && direction.y === -newDir.y)) {
                        nextDirection = newDir;
                        if (!running && !gameOver && !gameWon) { running = true; updateStartBtn(); }
                    }
                }
                btn.addEventListener('touchstart', pressDir, {passive: false});
                btn.addEventListener('mousedown', pressDir);
            });

            // ── Swipe sul canvas (mobile) ────────────────────────────────
            let touchStartX = null, touchStartY = null;
            canvas.addEventListener('touchstart', (e) => {
                touchStartX = e.touches[0].clientX;
                touchStartY = e.touches[0].clientY;
                e.preventDefault();
            }, {passive: false});
            canvas.addEventListener('touchend', (e) => {
                if (touchStartX === null) return;
                const dx = e.changedTouches[0].clientX - touchStartX;
                const dy = e.changedTouches[0].clientY - touchStartY;
                const minSwipe = 20;
                let newDir = null;
                if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > minSwipe) {
                    newDir = dx > 0 ? {x: 1, y: 0} : {x: -1, y: 0};
                } else if (Math.abs(dy) > minSwipe) {
                    newDir = dy > 0 ? {x: 0, y: 1} : {x: 0, y: -1};
                }
                if (newDir && !(direction.x === -newDir.x && direction.y === -newDir.y)) {
                    nextDirection = newDir;
                    if (!running && !gameOver && !gameWon) { running = true; updateStartBtn(); }
                }
                touchStartX = null; touchStartY = null;
                e.preventDefault();
            }, {passive: false});

            // ── Altezza iframe adattiva (Streamlit) ────────────────────
            function syncFrameHeight() {
                const root = document.getElementById("gameContainer");
                const rect = root.getBoundingClientRect();
                const height = Math.ceil(rect.bottom + 20);
                window.parent.postMessage(
                    { type: "streamlit:setFrameHeight", height: height },
                    "*"
                );
            }
            function scheduleHeightSync() {
                syncFrameHeight();
                requestAnimationFrame(syncFrameHeight);
                setTimeout(syncFrameHeight, 80);
                setTimeout(syncFrameHeight, 300);
            }
            window.addEventListener("load", scheduleHeightSync);
            window.addEventListener("resize", syncFrameHeight);
            if (typeof ResizeObserver !== "undefined") {
                new ResizeObserver(syncFrameHeight).observe(
                    document.getElementById("gameContainer")
                );
            }

            // ── Avvia il loop ────────────────────────────────────────────
            gameLoop();
            scheduleHeightSync();
        </script>
    </body>
    </html>
    """
    
    # Altezza generosa: canvas 420px + controlli; JS la affina con setFrameHeight
    st.components.v1.html(game_html, height=820, scrolling=False)
