"""App Streamlit — Raccolta di giochi."""

import streamlit as st

from giochi import (
    blackjack,
    forca,
    indovina_numero,
    lancio_dado,
    memoria_numerica,
    parola_mescolata,
    quiz,
    sasso_carta_forbici,
    serpente_acqua_pistola,
    snake,
    testa_o_croce,
    tris,
)

GIOCHI = {
    "Indovina il numero": indovina_numero.render,
    "Lancio del dado": lancio_dado.render,
    "Sasso, carta, forbici": sasso_carta_forbici.render,
    "Testa o croce": testa_o_croce.render,
    "Quiz": quiz.render,
    "Forca": forca.render,
    "Parola mescolata": parola_mescolata.render,
    "Serpente, acqua, pistola": serpente_acqua_pistola.render,
    "Snake": snake.render,
    "Tris": tris.render,
    "Blackjack": blackjack.render,
    "Memoria numerica": memoria_numerica.render,
}

st.set_page_config(
    page_title="Raccolta Giochi",
    page_icon="🎮",
    layout="centered",
)

st.title("🎮 Raccolta di Giochi")
st.caption("Scegli un gioco dalla barra laterale e divertiti!")

with st.sidebar:
    st.header("Menu")
    gioco_scelto = st.radio("Giochi disponibili", list(GIOCHI.keys()), label_visibility="collapsed")

st.divider()
GIOCHI[gioco_scelto]()
