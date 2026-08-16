"""Gioco: Testa o croce."""

import random

import streamlit as st

SESSION_KEY = "testa_o_croce"


def render():
    """Interfaccia Streamlit per 'Testa o croce'."""
    st.subheader("Testa o croce")
    st.write("Scegli testa o croce e lancia la moneta!")

    col1, col2 = st.columns(2)
    scelta = None

    with col1:
        if st.button("🪙 Testa", use_container_width=True, key="toc_testa"):
            scelta = "testa"
    with col2:
        if st.button("🪙 Croce", use_container_width=True, key="toc_croce"):
            scelta = "croce"

    if scelta:
        risultato = "testa" if random.randint(1, 2) == 1 else "croce"
        st.session_state[SESSION_KEY] = {
            "scelta": scelta,
            "risultato": risultato,
            "vinto": scelta == risultato,
        }

    if SESSION_KEY in st.session_state:
        partita = st.session_state[SESSION_KEY]
        st.write(f"La moneta ha fatto: **{partita['risultato'].title()}**")
        if partita["vinto"]:
            st.success("Hai vinto!")
        else:
            st.error("Hai perso!")
