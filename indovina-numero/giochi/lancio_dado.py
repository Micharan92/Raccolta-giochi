"""Gioco: Lancio del dado con grafica interattiva."""

import streamlit as st


def render():
    """Interfaccia Streamlit per 'Lancio del dado'."""
    st.subheader("🎲 Lancio del dado")
    st.write("Scegli un numero da 1 a 6 e lancia il dado! Vinci se il numero corrisponde al risultato.")

    # Faccia 2D: i puntini e il testo usano sempre lo stesso valore.
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
            #canvasContainer {
                position: relative;
                width: 300px;
                height: 300px;
            }
            canvas {
                width: 100%;
                height: 100%;
                display: block;
            }
            #controls {
                display: flex;
                gap: 15px;
                align-items: center;
                flex-wrap: wrap;
                justify-content: center;
            }
            select {
                padding: 10px 15px;
                font-size: 16px;
                border-radius: 5px;
                border: 2px solid #444;
                background-color: #222;
                color: #00ff00;
                cursor: pointer;
            }
            button {
                padding: 10px 30px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
                background-color: #00ff00;
                color: #000;
                cursor: pointer;
                transition: all 0.3s;
            }
            button:hover {
                background-color: #00cc00;
                transform: scale(1.05);
            }
            button:disabled {
                background-color: #666;
                cursor: not-allowed;
                color: #999;
            }
            #result {
                font-size: 18px;
                font-weight: bold;
                min-height: 60px;
                text-align: center;
                padding: 15px;
                border-radius: 5px;
                background-color: #1a1a1a;
                border: 2px solid #444;
                color: #ddd;
            }
            .success {
                color: #00ff00;
                border-color: #00ff00;
            }
            .error {
                color: #ff6b6b;
                border-color: #ff6b6b;
            }
            .label {
                color: #999;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div id="gameContainer">
            <div id="canvasContainer">
                <canvas id="diceCanvas"></canvas>
            </div>

            <div id="controls">
                <div>
                    <div class="label">Il tuo numero:</div>
                    <select id="numberSelect">
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                        <option value="4">4</option>
                        <option value="5">5</option>
                        <option value="6">6</option>
                    </select>
                </div>
                <button id="rollBtn">🎲 Lancia il dado</button>
            </div>

            <div id="result"></div>
        </div>

        <script>
            const canvas = document.getElementById('diceCanvas');
            const ctx = canvas.getContext('2d');
            canvas.width = 300;
            canvas.height = 300;

            const PIP_LAYOUT = {
                1: [[0, 0]],
                2: [[-1, -1], [1, 1]],
                3: [[-1, -1], [0, 0], [1, 1]],
                4: [[-1, -1], [1, -1], [-1, 1], [1, 1]],
                5: [[-1, -1], [1, -1], [0, 0], [-1, 1], [1, 1]],
                6: [[-1, -1], [-1, 0], [-1, 1], [1, -1], [1, 0], [1, 1]]
            };

            let shownFace = 1;
            let spinAngle = 0;
            let animId = null;

            function roundedRect(x, y, w, h, r) {
                ctx.beginPath();
                ctx.moveTo(x + r, y);
                ctx.arcTo(x + w, y, x + w, y + h, r);
                ctx.arcTo(x + w, y + h, x, y + h, r);
                ctx.arcTo(x, y + h, x, y, r);
                ctx.arcTo(x, y, x + w, y, r);
                ctx.closePath();
            }

            function drawDie(face, angle) {
                ctx.fillStyle = '#0e0e0e';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                const cx = canvas.width / 2;
                const cy = canvas.height / 2;
                const size = 160;

                ctx.save();
                ctx.translate(cx, cy);
                ctx.rotate(angle);

                ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
                ctx.shadowBlur = 18;
                ctx.shadowOffsetY = 8;

                const gradient = ctx.createLinearGradient(-size / 2, -size / 2, size / 2, size / 2);
                gradient.addColorStop(0, '#fff7f0');
                gradient.addColorStop(1, '#d8cfc6');
                roundedRect(-size / 2, -size / 2, size, size, 28);
                ctx.fillStyle = gradient;
                ctx.fill();

                ctx.shadowColor = 'transparent';
                ctx.lineWidth = 4;
                ctx.strokeStyle = '#2a2a2a';
                ctx.stroke();

                const pips = PIP_LAYOUT[face] || PIP_LAYOUT[1];
                const pipR = 12;
                const spread = 42;
                ctx.fillStyle = '#1a1a1a';
                pips.forEach(([dx, dy]) => {
                    ctx.beginPath();
                    ctx.arc(dx * spread, dy * spread, pipR, 0, Math.PI * 2);
                    ctx.fill();
                });

                ctx.restore();
            }

            function showResult(userChoice, diceResult) {
                const won = userChoice === diceResult;
                const resultDiv = document.getElementById('result');
                resultDiv.className = won ? 'success' : 'error';
                resultDiv.innerHTML =
                    '<strong>Hai scelto: ' + userChoice + '</strong><br>' +
                    '<strong>Il dado ha fatto: ' + diceResult + '</strong><br>' +
                    (won ? '✅ VINTO!' : '❌ PERSO!');
            }

            function rollDice() {
                if (animId !== null) return;

                const rollBtn = document.getElementById('rollBtn');
                const numberSelect = document.getElementById('numberSelect');
                const resultDiv = document.getElementById('result');
                rollBtn.disabled = true;
                numberSelect.disabled = true;
                resultDiv.className = '';
                resultDiv.innerHTML = '';

                const userChoice = parseInt(numberSelect.value, 10);
                const diceResult = 1 + Math.floor(Math.random() * 6);

                const start = performance.now();
                const duration = 1200;

                function tick(now) {
                    const t = Math.min(1, (now - start) / duration);
                    spinAngle += 0.35;
                    shownFace = 1 + Math.floor(Math.random() * 6);
                    drawDie(shownFace, spinAngle);

                    if (t < 1) {
                        animId = requestAnimationFrame(tick);
                        return;
                    }

                    shownFace = diceResult;
                    spinAngle = 0;
                    drawDie(shownFace, 0);
                    showResult(userChoice, diceResult);
                    rollBtn.disabled = false;
                    numberSelect.disabled = false;
                    animId = null;
                }

                animId = requestAnimationFrame(tick);
            }

            document.getElementById('rollBtn').addEventListener('click', rollDice);
            drawDie(shownFace, 0);
        </script>
    </body>
    </html>
    """

    st.components.v1.html(game_html, height=652)
