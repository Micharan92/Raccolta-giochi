"""CSS e helper condivisi per layout mobile + desktop."""

import streamlit as st

CSS_RESPONSIVE = """
<style>
/* ── Layout generale ───────────────────────────────────────── */
section.main .block-container {
    padding-top: 1.25rem;
    padding-bottom: 2.5rem;
    max-width: 46rem;
}
section.main .block-container p,
section.main .block-container li {
    overflow-wrap: anywhere;
}

/* ── Colonne: impila su mobile ─────────────────────────────── */
@media (max-width: 768px) {
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.35rem !important;
    }
    div[data-testid="column"] {
        flex: 1 1 100% !important;
        width: 100% !important;
        min-width: 0 !important;
    }
    /* Metriche a 2 colonne su mobile (4 metriche → griglia 2×2) */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) {
        display: grid !important;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem !important;
    }
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) > div[data-testid="column"] {
        flex: none !important;
        width: auto !important;
    }
}

/* ── Pulsanti e touch target ───────────────────────────────── */
div.stButton > button {
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
}
@media (max-width: 768px) {
    div.stButton > button {
        min-height: 48px;
        font-size: 0.95rem;
        padding: 0.45rem 0.75rem;
    }
    div.stRadio > div,
    div.stRadio label {
        min-height: 44px;
        align-items: center;
    }
    div.stRadio label span {
        font-size: 0.95rem;
        line-height: 1.35;
    }
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stNumberInput"] input {
        min-height: 44px;
        font-size: 1rem;
    }
    /* Radio orizzontale → verticale su mobile */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 0.25rem !important;
    }
}

@media (min-width: 769px) {
    div.stButton > button {
        min-height: 42px;
    }
}

/* ── Sidebar mobile ────────────────────────────────────────── */
@media (max-width: 768px) {
    section[data-testid="stSidebar"] {
        min-width: min(85vw, 280px) !important;
    }
}

/* ── iframe componenti HTML ────────────────────────────────── */
div[data-testid="stIFrame"],
div[data-testid="stIFrame"] iframe {
    max-width: 100% !important;
}

/* ── Forca: tastiera lettere ─────────────────────────────────── */
.forca-word {
    font-size: clamp(1.75rem, 6.5vw, 2.75rem);
    letter-spacing: 0.14em;
    text-align: center;
    margin: 0.75rem 0;
    word-break: break-word;
}

/* ── Quiz tabellone ─────────────────────────────────────────── */
@media (max-width: 768px) {
    .tq-board-wrap { padding: 0.5rem !important; }
    .tq-board { max-width: min(92vw, 320px) !important; }
    .tq-center { font-size: 0.62rem !important; }
    .tq-board .cell { width: 11% !important; height: 11% !important; font-size: 0.75rem !important; }
    .tq-scores { flex-direction: column !important; }
    .tq-spicchi-grid { display: grid !important; grid-template-columns: 1fr 1fr !important; gap: 0.35rem !important; }
}
@media (min-width: 769px) {
    .tq-spicchi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.35rem; }
}

/* ── Texas Hold'em: azioni compatte ─────────────────────────── */
@media (max-width: 768px) {
    .th-actions-hint { font-size: 0.82rem !important; }
}
</style>
"""


def inject_responsive_css():
    """Inietta CSS responsive globale (ogni rerun Streamlit)."""
    st.markdown(CSS_RESPONSIVE, unsafe_allow_html=True)
