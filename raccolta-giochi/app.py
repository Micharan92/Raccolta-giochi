"""App Streamlit — Raccolta di giochi."""

import streamlit as st

from giochi import (
    blackjack,
    briscola,
    scopa,
    forca,
    quiz,
    snake,
    texas_holdem,
    tris,
)
from giochi.responsive_ui import inject_responsive_css

GIOCHI = {
    "Quiz": quiz.render,
    "Forca": forca.render,
    "Snake": snake.render,
    "Tris": tris.render,
    "Blackjack": blackjack.render,
    "Briscola": briscola.render,
    "Scopa": scopa.render,
    "Texas Hold'em": texas_holdem.render,
}

MENU_KEY = "gioco_scelto"
_NOMI_GIOCHI = list(GIOCHI.keys())


def _gioco_da_query():
    raw = st.query_params.get("gioco")
    if raw is None:
        return None
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    return raw if raw in GIOCHI else None

st.set_page_config(
    page_title="Raccolta Giochi",
    page_icon="🎮",
    layout="centered",
)

inject_responsive_css()

if MENU_KEY not in st.session_state:
    st.session_state[MENU_KEY] = _NOMI_GIOCHI[0]

gioco_url = _gioco_da_query()
if gioco_url:
    st.session_state[MENU_KEY] = gioco_url
    if "gioco" in st.query_params:
        del st.query_params["gioco"]

st.title("🎮 Raccolta di Giochi")
st.caption("Scegli un gioco dalla barra laterale e divertiti!")

with st.sidebar:
    st.header("Menu")
    st.radio(
        "Giochi disponibili",
        _NOMI_GIOCHI,
        key=MENU_KEY,
        label_visibility="collapsed",
    )

gioco_scelto = st.session_state[MENU_KEY]

st.divider()
GIOCHI[gioco_scelto]()
