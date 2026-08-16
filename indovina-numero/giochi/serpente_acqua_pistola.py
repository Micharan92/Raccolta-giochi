"""Gioco: Serpente, acqua, pistola."""

import random

import streamlit as st

REGOLE = {
    "serpente": "acqua",
    "acqua": "pistola",
    "pistola": "serpente",
}

EMOJI = {
    "serpente": "🐍",
    "acqua": "💧",
    "pistola": "🔫",
}

SESSION_KEY = "serpente_acqua_pistola"


def _esito(scelta_giocatore, scelta_pc):
    if scelta_giocatore == scelta_pc:
        return "Pareggio!"
    if REGOLE[scelta_giocatore] == scelta_pc:
        return "Hai vinto!"
    return "Hai perso!"


def render():
    """Interfaccia Streamlit per 'Serpente, acqua, pistola'."""
    st.subheader("Serpente, acqua, pistola")
    st.write("Serpente batte acqua, acqua batte pistola, pistola batte serpente.")

    col1, col2, col3 = st.columns(3)
    scelta = None

    with col1:
        if st.button(f"{EMOJI['serpente']} Serpente", use_container_width=True, key="sap_serpente"):
            scelta = "serpente"
    with col2:
        if st.button(f"{EMOJI['acqua']} Acqua", use_container_width=True, key="sap_acqua"):
            scelta = "acqua"
    with col3:
        if st.button(f"{EMOJI['pistola']} Pistola", use_container_width=True, key="sap_pistola"):
            scelta = "pistola"

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
