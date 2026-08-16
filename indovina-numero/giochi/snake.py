"""Gioco: Snake - il classico gioco dei telefoni Nokia."""

import streamlit as st


def render():
    """Interfaccia Streamlit per 'Snake' con canvas HTML5."""
    st.subheader("🐍 Snake")
    st.write("Il classico gioco Snake! Mangia il cibo rosso e raggiungi 450 punti per vincere. "
             "Evita i muri e non colpirti con la coda!")
    st.write("**Controlli:** Premi SPAZIO per iniziare • Frecce direzionali (↑ ↓ ← →) o W/A/S/D")
    
    # Game HTML/JavaScript completo
    game_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { margin: 0; padding: 20px; font-family: Arial, sans-serif; background-color: #0e0e0e; }
            #gameContainer {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 20px;
            }
            canvas {
                border: 3px solid #444;
                background-color: #1a1a1a;
                display: block;
            }
            #stats {
                display: flex;
                gap: 30px;
                font-size: 18px;
                font-weight: bold;
                color: #fff;
            }
            .stat {
                display: flex;
                gap: 10px;
            }
            .stat-label {
                color: #999;
            }
            .stat-value {
                color: #00ff00;
            }
            #message {
                font-size: 20px;
                font-weight: bold;
                min-height: 30px;
                text-align: center;
            }
            .success {
                color: #00ff00;
            }
            .error {
                color: #ff6b6b;
            }
            .controls {
                text-align: center;
                font-size: 14px;
                color: #999;
            }
        </style>
    </head>
    <body>
        <div id="gameContainer">
            <canvas id="gameCanvas" width="400" height="300"></canvas>
            <div id="stats">
                <div class="stat">
                    <span class="stat-label">Punteggio:</span>
                    <span class="stat-value" id="score">0</span>
                    <span class="stat-label">/ 450</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Lunghezza:</span>
                    <span class="stat-value" id="length">3</span>
                </div>
            </div>
            <div id="message"></div>
            <div class="controls">
                Premi SPAZIO per iniziare/pausa • Usa frecce o WASD per muoverti
            </div>
        </div>

        <script>
            const canvas = document.getElementById('gameCanvas');
            const ctx = canvas.getContext('2d');
            
            const GRID_WIDTH = 20;
            const GRID_HEIGHT = 15;
            const CELL_SIZE = canvas.width / GRID_WIDTH;
            const MAX_SCORE = 450;
            const GAME_SPEED = 150; // ms

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

                // Griglia
                ctx.strokeStyle = '#222';
                ctx.lineWidth = 1;
                for (let i = 0; i <= GRID_WIDTH; i++) {
                    ctx.beginPath();
                    ctx.moveTo(i * CELL_SIZE, 0);
                    ctx.lineTo(i * CELL_SIZE, canvas.height);
                    ctx.stroke();
                }
                for (let i = 0; i <= GRID_HEIGHT; i++) {
                    ctx.beginPath();
                    ctx.moveTo(0, i * CELL_SIZE);
                    ctx.lineTo(canvas.width, i * CELL_SIZE);
                    ctx.stroke();
                }

                // Serpente
                snake.forEach((segment, index) => {
                    if (index === 0) {
                        // Testa
                        ctx.fillStyle = '#00ff00';
                        ctx.shadowColor = '#00ff00';
                        ctx.shadowBlur = 10;
                    } else {
                        // Corpo
                        ctx.fillStyle = '#00cc00';
                        ctx.shadowColor = 'transparent';
                    }
                    ctx.fillRect(segment.x * CELL_SIZE + 1, segment.y * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2);
                });
                ctx.shadowColor = 'transparent';

                // Cibo
                ctx.fillStyle = '#ff6b6b';
                ctx.shadowColor = '#ff6b6b';
                ctx.shadowBlur = 10;
                ctx.fillRect(food.x * CELL_SIZE + 1, food.y * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2);
                ctx.shadowColor = 'transparent';

                // Stats
                document.getElementById('score').textContent = score;
                document.getElementById('length').textContent = snake.length;

                // Messaggio
                const msgDiv = document.getElementById('message');
                if (gameWon) {
                    msgDiv.textContent = '🎉 HAI VINTO! Hai raggiunto 450 punti!';
                    msgDiv.className = 'success';
                } else if (gameOver) {
                    msgDiv.textContent = `💀 GAME OVER! Punteggio: ${score}`;
                    msgDiv.className = 'error';
                } else if (!running) {
                    msgDiv.textContent = 'Premi SPAZIO per iniziare';
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

            // Input tastiera
            document.addEventListener('keydown', (e) => {
                if (e.key === ' ') {
                    e.preventDefault();
                    if (!gameOver && !gameWon) {
                        running = !running;
                    } else {
                        // Reset
                        snake = [{x: Math.floor(GRID_WIDTH/2), y: Math.floor(GRID_HEIGHT/2)}];
                        direction = {x: 1, y: 0};
                        nextDirection = {x: 1, y: 0};
                        food = generateFood();
                        score = 0;
                        gameOver = false;
                        gameWon = false;
                        running = true;
                        growthPending = 0;
                        lastMoveTime = Date.now();
                    }
                    return;
                }

                const keyMap = {
                    'ArrowUp': {x: 0, y: -1},
                    'ArrowDown': {x: 0, y: 1},
                    'ArrowLeft': {x: -1, y: 0},
                    'ArrowRight': {x: 1, y: 0},
                    'w': {x: 0, y: -1}, 'W': {x: 0, y: -1},
                    'a': {x: -1, y: 0}, 'A': {x: -1, y: 0},
                    's': {x: 0, y: 1}, 'S': {x: 0, y: 1},
                    'd': {x: 1, y: 0}, 'D': {x: 1, y: 0}
                };

                if (keyMap[e.key]) {
                    const newDir = keyMap[e.key];
                    // Previeni inversione completa
                    if (!(direction.x === -newDir.x && direction.y === -newDir.y)) {
                        nextDirection = newDir;
                    }
                    e.preventDefault(); // Previeni lo scroll della pagina
                }
            });

            // Avvia il loop
            gameLoop();
        </script>
    </body>
    </html>
    """
    
    st.components.v1.html(game_html, height=600)
    
    st.divider()
    st.info("💡 **Come giocare:** Premi SPAZIO per iniziare, usa Frecce direzionali o WASD per muoverti")
