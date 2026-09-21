"""Componente HTML condiviso per il dado 3D (canvas)."""

import json

_DADO_STYLES = """
    * { box-sizing: border-box; }
    body {
        margin: 0;
        padding: 8px 12px 18px;
        font-family: Arial, sans-serif;
        background-color: transparent;
        overflow: visible;
    }
    #gameContainer {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        max-width: 420px;
        margin: 0 auto;
        padding-bottom: 6px;
    }
    #canvasContainer {
        position: relative;
        width: 100%;
        max-width: 220px;
        aspect-ratio: 1;
    }
    canvas {
        width: 100%;
        height: 100%;
        display: block;
    }
    .label {
        color: #666;
        font-size: 13px;
        text-align: center;
        margin-bottom: 4px;
    }
    #numberPicker { width: 100%; }
    .num-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        width: 100%;
    }
    .num-btn {
        min-height: 44px;
        font-size: 1.05rem;
        font-weight: bold;
        border-radius: 8px;
        border: 2px solid #444;
        background-color: #222;
        color: #ccc;
        cursor: pointer;
        touch-action: manipulation;
        transition: all 0.15s;
    }
    .num-btn.active {
        border-color: #00ff00;
        background-color: #1a3d1a;
        color: #00ff00;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.25);
    }
    .num-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    #rollBtn {
        width: 100%;
        min-height: 48px;
        padding: 10px 20px;
        font-size: 1rem;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        background-color: #00ff00;
        color: #000;
        cursor: pointer;
        touch-action: manipulation;
    }
    #rollBtn:disabled {
        background-color: #666;
        cursor: not-allowed;
        color: #999;
    }
    #result {
        font-size: 0.95rem;
        font-weight: bold;
        min-height: 56px;
        width: 100%;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        background-color: #1a1a1a;
        border: 2px solid #444;
        color: #ddd;
        line-height: 1.4;
    }
    #result.success { color: #00ff00; border-color: #00ff00; }
    #result.error { color: #ff6b6b; border-color: #ff6b6b; }
    #result.neutral { color: #f5e6c8; border-color: #8b6914; }
    @media (max-width: 768px) {
        body { padding: 6px 8px 10px; }
        #gameContainer { gap: 8px; max-width: 100%; }
        #canvasContainer { max-width: 200px; }
        .num-btn { min-height: 52px; font-size: 1.15rem; }
        #rollBtn { min-height: 54px; font-size: 1.05rem; }
        #result { min-height: 48px; font-size: 0.92rem; padding: 8px; }
    }
    @media (min-width: 769px) {
        #canvasContainer { max-width: 240px; }
        .num-btn { min-height: 46px; }
        #rollBtn { min-height: 50px; }
    }
"""


def altezza_iframe_dado(mode: str = "guess") -> int:
    """Altezza iframe adattata al modo del dado."""
    return 620 if mode == "guess" else 310


def _dado_script(mode: str, risultato: int | None) -> str:
    cfg = json.dumps({"mode": mode, "result": risultato})
    return f"""
    <script>
    (function() {{
        const cfg = {cfg};
        const canvas = document.getElementById('diceCanvas');
        const ctx = canvas.getContext('2d');
        const numGrid = document.getElementById('numGrid');
        const rollBtn = document.getElementById('rollBtn');
        const resultDiv = document.getElementById('result');
        const picker = document.getElementById('numberPicker');

        let selectedNumber = 1;
        let shownFace = 1;
        let spinAngle = 0;
        let animId = null;

        function resizeCanvas() {{
            const container = document.getElementById('canvasContainer');
            const size = Math.min(container.clientWidth, 260);
            canvas.width = size;
            canvas.height = size;
            drawDie(shownFace, spinAngle);
        }}

        const PIP_LAYOUT = {{
            1: [[0, 0]],
            2: [[-1, -1], [1, 1]],
            3: [[-1, -1], [0, 0], [1, 1]],
            4: [[-1, -1], [1, -1], [-1, 1], [1, 1]],
            5: [[-1, -1], [1, -1], [0, 0], [-1, 1], [1, 1]],
            6: [[-1, -1], [-1, 0], [-1, 1], [1, -1], [1, 0], [1, 1]]
        }};

        function roundedRect(x, y, w, h, r) {{
            ctx.beginPath();
            ctx.moveTo(x + r, y);
            ctx.arcTo(x + w, y, x + w, y + h, r);
            ctx.arcTo(x + w, y + h, x, y + h, r);
            ctx.arcTo(x, y + h, x, y, r);
            ctx.arcTo(x, y, x + w, y, r);
            ctx.closePath();
        }}

        function drawDie(face, angle) {{
            ctx.fillStyle = '#0e0e0e';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            const size = canvas.width * 0.53;
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angle);
            ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
            ctx.shadowBlur = 18;
            ctx.shadowOffsetY = 8;
            const gradient = ctx.createLinearGradient(-size / 2, -size / 2, size / 2, size / 2);
            gradient.addColorStop(0, '#fff7f0');
            gradient.addColorStop(1, '#d8cfc6');
            roundedRect(-size / 2, -size / 2, size, size, size * 0.17);
            ctx.fillStyle = gradient;
            ctx.fill();
            ctx.shadowColor = 'transparent';
            ctx.lineWidth = Math.max(2, size * 0.025);
            ctx.strokeStyle = '#2a2a2a';
            ctx.stroke();
            const pips = PIP_LAYOUT[face] || PIP_LAYOUT[1];
            const pipR = size * 0.075;
            const spread = size * 0.26;
            ctx.fillStyle = '#1a1a1a';
            pips.forEach(([dx, dy]) => {{
                ctx.beginPath();
                ctx.arc(dx * spread, dy * spread, pipR, 0, Math.PI * 2);
                ctx.fill();
            }});
            ctx.restore();
        }}

        function setSelected(n) {{
            selectedNumber = n;
            document.querySelectorAll('.num-btn').forEach((btn) => {{
                btn.classList.toggle('active', parseInt(btn.dataset.n, 10) === n);
            }});
        }}

        function buildNumberGrid() {{
            for (let n = 1; n <= 6; n++) {{
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'num-btn' + (n === 1 ? ' active' : '');
                btn.dataset.n = String(n);
                btn.textContent = String(n);
                btn.addEventListener('click', () => {{
                    if (animId !== null) return;
                    setSelected(n);
                }});
                numGrid.appendChild(btn);
            }}
        }}

        function setControlsEnabled(enabled) {{
            if (rollBtn) rollBtn.disabled = !enabled;
            document.querySelectorAll('.num-btn').forEach((btn) => {{
                btn.disabled = !enabled;
            }});
        }}

        function syncFrameHeight() {{
            const root = document.getElementById('gameContainer');
            const height = Math.ceil(root.getBoundingClientRect().bottom + 18);
            window.parent.postMessage(
                {{ type: 'streamlit:setFrameHeight', height: height }},
                '*'
            );
        }}

        function animateToResult(diceResult, onDone) {{
            if (animId !== null) return;
            setControlsEnabled(false);
            const start = performance.now();
            const duration = 1100;
            function tick(now) {{
                const t = Math.min(1, (now - start) / duration);
                spinAngle += 0.35;
                shownFace = 1 + Math.floor(Math.random() * 6);
                drawDie(shownFace, spinAngle);
                if (t < 1) {{
                    animId = requestAnimationFrame(tick);
                    return;
                }}
                shownFace = diceResult;
                spinAngle = 0;
                drawDie(shownFace, 0);
                animId = null;
                syncFrameHeight();
                if (onDone) onDone();
            }}
            animId = requestAnimationFrame(tick);
        }}

        function showGuessResult(userChoice, diceResult) {{
            const won = userChoice === diceResult;
            resultDiv.className = won ? 'success' : 'error';
            resultDiv.innerHTML =
                '<strong>Hai scelto: ' + userChoice + '</strong><br>' +
                '<strong>Il dado ha fatto: ' + diceResult + '</strong><br>' +
                (won ? '✅ VINTO!' : '❌ PERSO!');
        }}

        function rollGuessMode() {{
            if (animId !== null) return;
            resultDiv.className = '';
            resultDiv.innerHTML = '';
            const userChoice = selectedNumber;
            const diceResult = 1 + Math.floor(Math.random() * 6);
            animateToResult(diceResult, () => {{
                showGuessResult(userChoice, diceResult);
                setControlsEnabled(true);
            }});
        }}

        if (cfg.mode === 'guess') {{
            buildNumberGrid();
            rollBtn.addEventListener('click', rollGuessMode);
        }} else {{
            if (picker) picker.style.display = 'none';
            if (rollBtn) rollBtn.style.display = 'none';
            const val = cfg.result || 1;
            resultDiv.className = 'neutral';
            resultDiv.innerHTML = '<strong>Risultato: ' + val + '</strong>';
            animateToResult(val, () => {{}});
        }}

        window.addEventListener('resize', () => {{
            resizeCanvas();
            syncFrameHeight();
        }});
        window.addEventListener('load', syncFrameHeight);
        resizeCanvas();
        syncFrameHeight();
    }})();
    </script>
    """


def html_dado(mode: str = "guess", risultato: int | None = None) -> str:
    """Genera HTML del dado. mode: 'guess' (lancio dado) | 'show' (mostra risultato)."""
    body_bg = "#0e0e0e" if mode == "guess" else "transparent"
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <style>
        {_DADO_STYLES}
        body {{ background-color: {body_bg}; }}
        </style>
    </head>
    <body>
        <div id="gameContainer">
            <div id="canvasContainer">
                <canvas id="diceCanvas"></canvas>
            </div>
            <div id="numberPicker">
                <div class="label">Il tuo numero:</div>
                <div class="num-grid" id="numGrid"></div>
            </div>
            <button id="rollBtn" type="button">🎲 Lancia il dado</button>
            <div id="result"></div>
        </div>
        {_dado_script(mode, risultato)}
    </body>
    </html>
    """
