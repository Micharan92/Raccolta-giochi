"""Gioco: Forca."""

import random

import streamlit as st

from giochi.parole_forca import PAROLE

MAX_ERRORI = 10
SESSION_KEY = "forca"


def _mostra_parola(parola, lettere_indovinate):
    return " ".join(lettera if lettera in lettere_indovinate else "_" for lettera in parola)


def _nuova_partita():
    return {
        "parola": random.choice(PAROLE),
        "lettere_indovinate": set(),
        "errori": 0,
        "vinto": False,
        "perso": False,
    }


def _inizializza():
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = _nuova_partita()


def render():
    """Interfaccia Streamlit per 'Forca'."""
    _inizializza()
    stato = st.session_state[SESSION_KEY]

    st.subheader("Forca")
    st.write(
        f"Indovina la parola segreta lettera per lettera. Hai al massimo **{MAX_ERRORI}** errori. "
        f"({len(PAROLE)} parole disponibili)"
    )

    st.markdown(f"### {_mostra_parola(stato['parola'], stato['lettere_indovinate']).upper()}")
    st.progress(stato["errori"] / MAX_ERRORI, text=f"Errori: {stato['errori']}/{MAX_ERRORI}")

    if stato["lettere_indovinate"]:
        usate = ", ".join(sorted(stato["lettere_indovinate"]))
        st.caption(f"Lettere provate: {usate}")

    if stato["vinto"]:
        st.success(f"Complimenti! Hai indovinato la parola: **{stato['parola']}**")
        if st.button("Nuova partita", key="forca_reset_vinto"):
            st.session_state[SESSION_KEY] = _nuova_partita()
            st.rerun()
        return

    if stato["perso"]:
        st.error(f"Hai perso! La parola era: **{stato['parola']}**")
        if st.button("Nuova partita", key="forca_reset_perso"):
            st.session_state[SESSION_KEY] = _nuova_partita()
            st.rerun()
        return

    lettera = st.text_input("Inserisci una lettera", max_chars=1, key="forca_input").strip().lower()

    if st.button("Prova lettera", key="forca_prova") and lettera:
        if len(lettera) != 1 or not lettera.isalpha():
            st.warning("Inserisci una sola lettera valida.")
            return

        if lettera in stato["lettere_indovinate"]:
            st.warning("Hai già provato questa lettera.")
            return

        stato["lettere_indovinate"].add(lettera)

        if lettera not in stato["parola"]:
            stato["errori"] += 1
            if stato["errori"] >= MAX_ERRORI:
                stato["perso"] = True
        elif all(c in stato["lettere_indovinate"] for c in stato["parola"]):
            stato["vinto"] = True

        st.rerun()
