"""Gioco: Parola mescolata."""

import random

import streamlit as st

from giochi.parole_mescolata import PAROLE

SESSION_KEY = "parola_mescolata"


def _mescola_parola(parola):
    lettere = list(parola)
    random.shuffle(lettere)
    return "".join(lettere)


def _nuova_parola():
    parola = random.choice(PAROLE)
    mescolata = _mescola_parola(parola)
    while mescolata == parola:
        mescolata = _mescola_parola(parola)
    return parola, mescolata


def _inizializza():
    if SESSION_KEY not in st.session_state:
        parola, mescolata = _nuova_parola()
        st.session_state[SESSION_KEY] = {
            "parola": parola,
            "mescolata": mescolata,
            "feedback": None,
        }


def render():
    """Interfaccia Streamlit per 'Parola mescolata'."""
    _inizializza()
    stato = st.session_state[SESSION_KEY]

    st.subheader("Parola mescolata")
    st.write(f"Indovina la parola originale dalle lettere mescolate. ({len(PAROLE)} parole disponibili)")

    st.markdown(f"### {stato['mescolata'].upper()}")

    tentativo = st.text_input("Qual è la parola?", key="parola_input").strip().lower()

    if st.button("Conferma", key="parola_conferma") and tentativo:
        if tentativo == stato["parola"]:
            stato["feedback"] = {"corretto": True}
        else:
            stato["feedback"] = {"corretto": False, "parola": stato["parola"]}
        st.rerun()

    if stato["feedback"]:
        if stato["feedback"]["corretto"]:
            st.success("Corretto!")
        else:
            st.error(f"Sbagliato! La parola era: **{stato['feedback']['parola']}**")

        if st.button("Nuova parola", key="parola_nuova"):
            parola, mescolata = _nuova_parola()
            st.session_state[SESSION_KEY] = {
                "parola": parola,
                "mescolata": mescolata,
                "feedback": None,
            }
            st.rerun()
