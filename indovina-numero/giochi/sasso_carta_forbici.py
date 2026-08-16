"""Gioco: Sasso, carta, forbici."""

import random

import streamlit as st

REGOLE = {
    "sasso": "forbici",
    "carta": "sasso",
    "forbici": "carta",
}

EMOJI = {
    "sasso": "✊",
    "carta": "✋",
    "forbici": "✌️",
}

SESSION_KEY = "sasso_carta_forbici"


def _esito(scelta_giocatore, scelta_pc):
    if scelta_giocatore == scelta_pc:
        return "Pareggio!"
    if REGOLE[scelta_giocatore] == scelta_pc:
        return "Hai vinto!"
    return "Hai perso!"


def render():
    """Interfaccia Streamlit per 'Sasso, carta, forbici'."""
    st.subheader("Sasso, carta, forbici")
    st.write("Scegli la tua mossa:")

    col1, col2, col3 = st.columns(3)
    scelta = None

    with col1:
        if st.button(f"{EMOJI['sasso']} Sasso", use_container_width=True, key="rps_sasso"):
            scelta = "sasso"
    with col2:
        if st.button(f"{EMOJI['carta']} Carta", use_container_width=True, key="rps_carta"):
            scelta = "carta"
    with col3:
        if st.button(f"{EMOJI['forbici']} Forbici", use_container_width=True, key="rps_forbici"):
            scelta = "forbici"

    if scelta:
        scelta_pc = random.choice(list(REGOLE.keys()))
        st.session_state[SESSION_KEY] = {"giocatore": scelta, "computer": scelta_pc}

    if SESSION_KEY in st.session_state:
        partita = st.session_state[SESSION_KEY]
        st.write(
            f"Tu: {EMOJI[partita['giocatore']]} **{partita['giocatore'].title()}**  |  "
            f"Computer: {EMOJI[partita['computer']]} **{partita['computer'].title()}**"
        )
        esito = _esito(partita["giocatore"], partita["computer"])
        if esito == "Pareggio!":
            st.warning(esito)
        elif esito == "Hai vinto!":
            st.success(esito)
        else:
            st.error(esito)
