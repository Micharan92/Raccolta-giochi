"""Disegno SVG della forca — omino progressivo (10 errori max)."""

_FORCA_CSS = """
body {
    margin: 0;
    padding: 0;
    background: transparent;
    overflow: hidden;
    font-family: Arial, sans-serif;
}
.forca-drawing-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    max-width: 42rem;
    margin: 0 auto;
    padding: clamp(0.75rem, 2.5vw, 1.35rem);
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(139, 105, 20, 0.35);
    border-radius: 14px;
    box-sizing: border-box;
}
.forca-svg {
    width: min(360px, 92vw);
    height: auto;
    display: block;
}
.forca-legno {
    stroke: #a67c52;
    stroke-width: 5;
    stroke-linecap: round;
}
.forca-corda {
    stroke: #c9a86c;
    stroke-width: 2.5;
    stroke-linecap: round;
}
.forca-omino {
    stroke: #e8e4dc;
    stroke-linecap: round;
}
.forca-occhio { fill: #e8e4dc; }
.forca-bocca {
    stroke: #e8e4dc;
    stroke-linecap: round;
}
.forca-morto {
    stroke: #ff6b6b;
    stroke-linecap: round;
}
@media (max-width: 768px) {
    .forca-svg { width: min(280px, 88vw); }
    .forca-drawing-wrap {
        padding: 0.65rem 0.5rem;
        border-radius: 12px;
    }
}
"""


def altezza_iframe_forca() -> int:
    return 340


def _svg_parti(errori: int) -> str:
    """Restituisce gli elementi SVG dell'omino in base agli errori."""
    parti = []
    e = max(0, min(errori, 10))

    if e >= 1:
        parti.append(
            '<circle cx="130" cy="68" r="14" class="forca-omino" fill="none" stroke-width="2.5"/>'
        )
    if e >= 2:
        parti.append('<line x1="130" y1="82" x2="130" y2="128" class="forca-omino" stroke-width="2.5"/>')
    if e >= 3:
        parti.append('<line x1="130" y1="98" x2="104" y2="114" class="forca-omino" stroke-width="2.5"/>')
    if e >= 4:
        parti.append('<line x1="130" y1="98" x2="156" y2="114" class="forca-omino" stroke-width="2.5"/>')
    if e >= 5:
        parti.append('<line x1="130" y1="128" x2="110" y2="162" class="forca-omino" stroke-width="2.5"/>')
    if e >= 6:
        parti.append('<line x1="130" y1="128" x2="150" y2="162" class="forca-omino" stroke-width="2.5"/>')
    if e >= 7:
        parti.append('<circle cx="124" cy="65" r="2" class="forca-occhio"/>')
    if e >= 8:
        parti.append('<circle cx="136" cy="65" r="2" class="forca-occhio"/>')
    if e >= 9:
        parti.append(
            '<path d="M 122 76 Q 130 82 138 76" class="forca-bocca" fill="none" stroke-width="2"/>'
        )
    if e >= 10:
        parti.append(
            '<line x1="121" y1="62" x2="127" y2="68" class="forca-morto" stroke-width="2"/>'
            '<line x1="127" y1="62" x2="121" y2="68" class="forca-morto" stroke-width="2"/>'
            '<line x1="133" y1="62" x2="139" y2="68" class="forca-morto" stroke-width="2"/>'
            '<line x1="139" y1="62" x2="133" y2="68" class="forca-morto" stroke-width="2"/>'
            '<line x1="128" y1="76" x2="128" y2="84" class="forca-morto" stroke-width="2"/>'
        )

    return "\n".join(parti)


def html_forca(errori: int, max_errori: int = 10) -> str:
    """HTML completo per iframe Streamlit (SVG non supportato in st.markdown)."""
    omino = _svg_parti(errori)
    return f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{_FORCA_CSS}</style>
</head>
<body>
    <div class="forca-drawing-wrap">
        <svg class="forca-svg" viewBox="0 0 200 230" xmlns="http://www.w3.org/2000/svg"
             role="img" aria-label="Forca: {errori} errori su {max_errori}">
            <line x1="30" y1="210" x2="100" y2="210" class="forca-legno"/>
            <line x1="55" y1="210" x2="55" y2="25" class="forca-legno"/>
            <line x1="55" y1="25" x2="130" y2="25" class="forca-legno"/>
            <line x1="130" y1="25" x2="130" y2="52" class="forca-corda"/>
            {omino}
        </svg>
    </div>
    <script>
    function syncHeight() {{
        const h = Math.ceil(document.body.scrollHeight + 4);
        window.parent.postMessage({{ type: "streamlit:setFrameHeight", height: h }}, "*");
    }}
    window.addEventListener("load", syncHeight);
    window.addEventListener("resize", syncHeight);
    syncHeight();
    </script>
</body>
</html>"""
