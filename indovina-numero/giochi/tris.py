"""Gioco: Tris."""

import random

import streamlit as st

GIOCATORE = "X"
COMPUTER = "O"
VUOTO = " "
SESSION_KEY = "tris"


def _nuova_griglia():
    return [VUOTO] * 9


def _ha_vinto(griglia, simbolo):
    combinazioni = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6),
    ]
    return any(all(griglia[i] == simbolo for i in combo) for combo in combinazioni)


def _pareggio(griglia):
    return VUOTO not in griglia


def _mosse_disponibili(griglia):
    return [i for i, cella in enumerate(griglia) if cella == VUOTO]


def _mossa_computer(griglia):
    return random.choice(_mosse_disponibili(griglia))


def _inizializza():
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = {
            "griglia": _nuova_griglia(),
            "fine": False,
            "messaggio": None,
        }


def _reset():
    st.session_state[SESSION_KEY] = {
        "griglia": _nuova_griglia(),
        "fine": False,
        "messaggio": None,
    }


def _simbolo_cella(griglia, indice):
    return griglia[indice] if griglia[indice] != VUOTO else str(indice + 1)


def _gioca_mossa(stato, indice):
    if stato["fine"] or stato["griglia"][indice] != VUOTO:
        return

    stato["griglia"][indice] = GIOCATORE

    if _ha_vinto(stato["griglia"], GIOCATORE):
        stato["fine"] = True
        stato["messaggio"] = "Hai vinto!"
        return

    if _pareggio(stato["griglia"]):
        stato["fine"] = True
        stato["messaggio"] = "Pareggio!"
        return

    mossa_pc = _mossa_computer(stato["griglia"])
    stato["griglia"][mossa_pc] = COMPUTER

    if _ha_vinto(stato["griglia"], COMPUTER):
        stato["fine"] = True
        stato["messaggio"] = "Il computer ha vinto!"
    elif _pareggio(stato["griglia"]):
        stato["fine"] = True
        stato["messaggio"] = "Pareggio!"


def render():
    """Interfaccia Streamlit per 'Tris'."""
    _inizializza()
    stato = st.session_state[SESSION_KEY]

    st.subheader("Tris")
    st.write("Sei **X**, il computer è **O**. Clicca su una casella libera.")

    for riga in range(3):
        cols = st.columns(3)
        for colonna in range(3):
            indice = riga * 3 + colonna
            etichetta = _simbolo_cella(stato["griglia"], indice)
            with cols[colonna]:
                if st.button(
                    etichetta,
                    key=f"tris_{indice}",
                    use_container_width=True,
                    disabled=stato["fine"] or stato["griglia"][indice] != VUOTO,
                ):
                    _gioca_mossa(stato, indice)
                    st.rerun()

    if stato["messaggio"]:
        if "vinto" in stato["messaggio"].lower() and "computer" not in stato["messaggio"].lower():
            st.success(stato["messaggio"])
        elif stato["messaggio"] == "Pareggio!":
            st.warning(stato["messaggio"])
        else:
            st.error(stato["messaggio"])

        if st.button("Nuova partita", key="tris_reset"):
            _reset()
            st.rerun()
