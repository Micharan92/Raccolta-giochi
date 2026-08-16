"""Gioco: Indovina il numero."""

import random

import streamlit as st

MINIMO = 1
MASSIMO = 100
SESSION_KEY = "indovina_numero"


def _inizializza():
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = {
            "numero_segreto": random.randint(MINIMO, MASSIMO),
            "tentativi": 0,
            "vinto": False,
        }


def _reset():
    st.session_state[SESSION_KEY] = {
        "numero_segreto": random.randint(MINIMO, MASSIMO),
        "tentativi": 0,
        "vinto": False,
    }


def render():
    """Interfaccia Streamlit per 'Indovina il numero'."""
    _inizializza()
    stato = st.session_state[SESSION_KEY]

    st.subheader("Indovina il numero")
    st.write(f"Ho pensato a un numero tra **{MINIMO}** e **{MASSIMO}**. Riesci a indovinarlo?")

    if stato["vinto"]:
        st.success(
            f"Complimenti! Hai indovinato in {stato['tentativi']} "
            f"tentativ{'o' if stato['tentativi'] == 1 else 'i'}!"
        )
        if st.button("Gioca ancora", key="indovina_reset"):
            _reset()
            st.rerun()
        return

    guess = st.number_input(
        "Inserisci un numero",
        min_value=MINIMO,
        max_value=MASSIMO,
        step=1,
        key="indovina_input",
    )

    if st.button("Prova", key="indovina_prova"):
        stato["tentativi"] += 1
        if guess < stato["numero_segreto"]:
            st.info("Il numero è più alto!")
        elif guess > stato["numero_segreto"]:
            st.info("Il numero è più basso!")
        else:
            stato["vinto"] = True
            st.rerun()

    st.caption(f"Tentativi: {stato['tentativi']}")
