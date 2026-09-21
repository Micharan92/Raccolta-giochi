"""Tavolo Tris cliccabile (Streamlit Custom Component v2)."""

import streamlit as st

_TRIS_CSS = """
#tris-root {
    width: 100%;
    min-height: 0;
    overflow: visible;
    display: flex;
    justify-content: center;
}
.tris-felt {
    box-sizing: border-box;
    width: min(400px, 96vw);
    margin: 0 auto;
    padding: clamp(0.85rem, 3vw, 1.1rem) clamp(0.8rem, 3vw, 1rem)
        clamp(1rem, 3vw, 1.25rem);
    background: linear-gradient(145deg, #0d5c2e 0%, #1a7a3e 48%, #0d5c2e 100%);
    border: 4px solid #8b6914;
    border-radius: 16px;
    box-shadow: inset 0 0 32px rgba(0, 0, 0, 0.35), 0 4px 14px rgba(0, 0, 0, 0.25);
}
.tris-title {
    color: #f5e6c8;
    font-size: clamp(0.85rem, 2.5vw, 0.95rem);
    font-weight: 600;
    text-align: center;
    margin: 0 0 0.55rem;
}
.tris-legend {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 0.75rem 1.35rem;
    margin-bottom: 0.65rem;
    font-size: 0.82rem;
    color: #f5e6c8;
}
.tris-legend span { display: inline-flex; align-items: center; gap: 0.35rem; }
.tris-sym {
    font-size: 1rem;
    font-weight: 800;
    width: 26px;
    height: 26px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    background: #fffef8;
    border: 2px solid #ccc;
    box-shadow: 1px 2px 4px rgba(0, 0, 0, 0.22);
}
.tris-sym.x { color: #2563eb; border-color: #93c5fd; }
.tris-sym.o { color: #dc2626; border-color: #fca5a5; }
.tris-status {
    color: #f5e6c8;
    font-style: italic;
    text-align: center;
    margin: 0 0 0.85rem;
    font-size: clamp(0.78rem, 2.2vw, 0.88rem);
    line-height: 1.35;
    min-height: 2.5em;
}
.tris-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: clamp(0.3rem, 2.5vw, 0.45rem);
    width: 100%;
}
.tris-cell {
    aspect-ratio: 1;
    width: 100%;
    min-height: 64px;
    box-sizing: border-box;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: clamp(1.85rem, 14vw, 2.65rem);
    font-weight: 800;
    line-height: 1;
    margin: 0;
    padding: 0;
    font-family: inherit;
}
.tris-cell.x {
    color: #2563eb;
    background: #fffef8;
    border: 2px solid #93c5fd;
    box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.28);
}
.tris-cell.o {
    color: #dc2626;
    background: #fffef8;
    border: 2px solid #fca5a5;
    box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.28);
}
.tris-cell.tris-play {
    cursor: pointer;
    background: rgba(255, 254, 248, 0.14);
    border: 2px dashed rgba(245, 230, 200, 0.55);
    color: #d4af37;
    font-size: clamp(1.45rem, 11vw, 2rem);
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.15);
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
}
.tris-cell.tris-play:active {
    background: rgba(255, 254, 248, 0.32);
    border-color: #d4af37;
    color: #ffd700;
}
.tris-cell.tris-empty-end {
    background: rgba(255, 254, 248, 0.08);
    border: 2px dashed rgba(245, 230, 200, 0.25);
    box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.1);
}
.tris-cell.win {
    box-shadow: 0 0 16px rgba(255, 215, 0, 0.85);
    border-color: #ffd700 !important;
}
"""

_TRIS_JS = """
export default function (component) {
  const { parentElement, data, setTriggerValue } = component;
  const root = parentElement.querySelector("#tris-root");
  if (!root || !data) return;

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function winClass(idx, vincenti) {
    if (!vincenti || !vincenti.length) return "";
    return vincenti.indexOf(idx) >= 0 ? " win" : "";
  }

  function cellHtml(idx, val, fine, vincenti) {
    const win = winClass(idx, vincenti);
    const v = (val || " ").trim();
    if (v === "X") return '<div class="tris-cell x' + win + '">X</div>';
    if (v === "O") return '<div class="tris-cell o' + win + '">O</div>';
    if (fine) return '<div class="tris-cell tris-empty-end' + win + '"></div>';
    return '<button type="button" class="tris-cell tris-play' + win + '" data-idx="' + idx + '">＋</button>';
  }

  const griglia = data.griglia || [];
  const status = data.status || "";
  const fine = !!data.fine;
  const vincenti = data.vincenti || [];
  let cells = "";
  for (let i = 0; i < 9; i++) {
    cells += cellHtml(i, griglia[i], fine, vincenti);
  }

  root.innerHTML =
    '<div class="tris-felt">' +
    '<p class="tris-title">Tris</p>' +
    '<div class="tris-legend">' +
    '<span><span class="tris-sym x">X</span> Tu</span>' +
    '<span><span class="tris-sym o">O</span> Computer</span>' +
    '</div>' +
    '<p class="tris-status">' + esc(status) + '</p>' +
    '<div class="tris-grid" role="grid">' + cells + '</div>' +
    '</div>';

  root.querySelectorAll("button[data-idx]").forEach(function (btn) {
    btn.onclick = function () {
      setTriggerValue("cell_click", parseInt(btn.getAttribute("data-idx"), 10));
    };
  });
}
"""

_TRIS_BOARD = st.components.v2.component(
    "tris_board",
    html='<div id="tris-root"></div>',
    css=_TRIS_CSS,
    js=_TRIS_JS,
)


def tris_board_component(griglia, status: str, vincenti, fine: bool, key=None):
    """Renderizza il tavolo; al click imposta il trigger cell_click (indice 0–8)."""
    return _TRIS_BOARD(
        key=key,
        data={
            "griglia": list(griglia),
            "status": status,
            "vincenti": list(vincenti) if vincenti else [],
            "fine": bool(fine),
        },
        width="stretch",
        height=620,
        on_cell_click_change=lambda: None,
    )
