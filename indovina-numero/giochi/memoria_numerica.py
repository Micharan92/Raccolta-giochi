"""Gioco: Memoria numerica."""

import random
import time

import streamlit as st

SESSION_KEY = "memoria_numerica"


def _genera_sequenza(lunghezza):
    return [random.randint(1, 9) for _ in range(lunghezza)]


def _inizializza():
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = {
            "livello": 1,
            "sequenza": None,
            "mostrata": False,
            "feedback": None,
        }


def _nuovo_livello(livello):
    return {
        "livello": livello,
        "sequenza": _genera_sequenza(livello),
        "mostrata": False,
        "feedback": None,
    }


def render():
    """Interfaccia Streamlit per 'Memoria numerica'."""
    _inizializza()
    stato = st.session_state[SESSION_KEY]

    st.subheader("Memoria numerica")
    st.write("Memorizza la sequenza di numeri e ripetila nell'ordine corretto.")
    st.caption(f"Livello attuale: **{stato['livello']}**")

    if stato["sequenza"] is None:
        stato.update(_nuovo_livello(stato["livello"]))

    sequenza_testo = " ".join(str(n) for n in stato["sequenza"])

    if not stato["mostrata"]:
        st.info(f"Memorizza: **{sequenza_testo}**")
        if st.button("Ho memorizzato", key="memoria_mostra"):
            placeholder = st.empty()
            for secondi in range(stato["livello"] + 1, 0, -1):
                placeholder.warning(f"La sequenza scompare tra {secondi} secondi...")
                time.sleep(1)
            placeholder.empty()
            stato["mostrata"] = True
            st.rerun()
        return

    tentativo = st.text_input(
        "Inserisci la sequenza separata da spazi",
        key="memoria_input",
        placeholder="es. 3 7 1",
    )

    if st.button("Conferma", key="memoria_conferma") and tentativo.strip():
        try:
            numeri_inseriti = [int(n) for n in tentativo.split()]
        except ValueError:
            st.warning("Inserisci solo numeri separati da spazi.")
            return

        if numeri_inseriti == stato["sequenza"]:
            stato["livello"] += 1
            stato.update(_nuovo_livello(stato["livello"]))
            st.success("Corretto! Passi al livello successivo.")
            st.rerun()
        else:
            stato["feedback"] = {
                "sequenza": sequenza_testo,
                "livello": stato["livello"],
            }

    if stato["feedback"]:
        st.error(
            f"Sbagliato! La sequenza era: **{stato['feedback']['sequenza']}**. "
            f"Hai raggiunto il livello {stato['feedback']['livello']}."
        )
        if st.button("Ricomincia", key="memoria_reset"):
            st.session_state[SESSION_KEY] = _nuovo_livello(1)
            st.rerun()
