"""Gioco: Forca."""

import random

import streamlit as st
import streamlit.components.v1 as components

from giochi.forca_ui import altezza_iframe_forca, html_forca
from giochi.parole_forca import (
    base_lettera,
    get_parole,
    parola_completata,
    parola_contiene_base,
)

MAX_ERRORI = 10
SESSION_KEY = "forca"


def _mostra_parola(parola, lettere_indovinate):
    return " ".join(
        lettera if base_lettera(lettera) in lettere_indovinate else "_"
        for lettera in parola
    )


def _nuova_partita():
    return {
        "parola": random.choice(get_parole()),
        "lettere_indovinate": set(),
        "errori": 0,
        "vinto": False,
        "perso": False,
    }


def _inizializza():
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = _nuova_partita()


def _css_forca():
    return """
    <style>
    .forca-panel {
        max-width: 42rem;
        margin: 0.85rem auto 0.65rem;
        padding: clamp(1rem, 2.5vw, 1.45rem) clamp(1rem, 3vw, 1.75rem);
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(139, 105, 20, 0.35);
        border-radius: 14px;
        text-align: center;
    }
    .forca-panel .forca-word {
        margin: 0 !important;
        font-size: clamp(1.75rem, 6.5vw, 2.75rem) !important;
        letter-spacing: 0.14em;
        line-height: 1.35;
    }
    .forca-panel .forca-lettere {
        margin: 0.85rem 0 0;
        font-size: clamp(0.85rem, 2.5vw, 1rem);
        color: #aaa;
    }
    div[data-testid="stVerticalBlock"]:has(
        div[data-testid="stForm"] input[aria-label="Inserisci una lettera"]
    ) div[data-testid="stProgress"] {
        max-width: 42rem;
        margin: 0 auto 0.85rem;
    }
    div[data-testid="stForm"]:has(input[aria-label="Inserisci una lettera"]) {
        max-width: 42rem;
        margin: 0 auto;
        padding: clamp(1rem, 2.5vw, 1.35rem) clamp(1rem, 3vw, 1.65rem);
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(139, 105, 20, 0.35);
        border-radius: 14px;
    }
    div[data-testid="stForm"]:has(input[aria-label="Inserisci una lettera"]) label p {
        font-size: clamp(0.95rem, 2.5vw, 1.1rem) !important;
    }
    div[data-testid="stForm"]:has(input[aria-label="Inserisci una lettera"]) input {
        font-size: clamp(1.65rem, 5vw, 2.15rem) !important;
        font-weight: 700 !important;
        text-align: center !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        min-height: 3.25rem !important;
        padding: 0.65rem 0.85rem !important;
    }
    div[data-testid="stForm"]:has(input[aria-label="Inserisci una lettera"]) button {
        min-height: 3rem !important;
        font-size: clamp(0.95rem, 2.5vw, 1.05rem) !important;
        margin-top: 0.35rem;
    }
    @media (max-width: 768px) {
        .forca-panel {
            max-width: 100%;
            margin-top: 0.65rem;
        }
        div[data-testid="stVerticalBlock"]:has(
            div[data-testid="stForm"] input[aria-label="Inserisci una lettera"]
        ) div[data-testid="stProgress"] {
            max-width: 100%;
        }
        div[data-testid="stForm"]:has(input[aria-label="Inserisci una lettera"]) {
            max-width: 100%;
        }
        div[data-testid="stForm"]:has(input[aria-label="Inserisci una lettera"]) input {
            min-height: 3.5rem !important;
        }
        div[data-testid="stForm"]:has(input[aria-label="Inserisci una lettera"]) button {
            min-height: 3.25rem !important;
        }
    }
    </style>
    """


def _prova_lettera(stato, lettera_raw: str):
    lettera = lettera_raw.strip().lower()
    if len(lettera) != 1 or not lettera.isalpha():
        st.warning("Inserisci una sola lettera valida (A–Z, anche accentate).")
        return

    lettera_base = base_lettera(lettera)
    if lettera_base in stato["lettere_indovinate"]:
        st.warning("Hai già provato questa lettera.")
        return

    stato["lettere_indovinate"].add(lettera_base)
    if not parola_contiene_base(stato["parola"], lettera_base):
        stato["errori"] += 1
        if stato["errori"] >= MAX_ERRORI:
            stato["perso"] = True
    elif parola_completata(stato["parola"], stato["lettere_indovinate"]):
        stato["vinto"] = True
    st.rerun()


def render():
    """Interfaccia Streamlit per 'Forca'."""
    _inizializza()
    stato = st.session_state[SESSION_KEY]

    st.subheader("Forca")
    st.write(
        f"Indovina la parola segreta lettera per lettera. Hai al massimo **{MAX_ERRORI}** errori."
    )

    st.markdown(_css_forca(), unsafe_allow_html=True)

    _, area, _ = st.columns([0.35, 2.3, 0.35])
    with area:
        components.html(
            html_forca(stato["errori"], MAX_ERRORI),
            height=altezza_iframe_forca(),
            scrolling=False,
        )

        parola_vis = _mostra_parola(stato["parola"], stato["lettere_indovinate"]).upper()
        lettere_html = ""
        if stato["lettere_indovinate"]:
            usate = ", ".join(sorted(stato["lettere_indovinate"]))
            lettere_html = f'<p class="forca-lettere">Lettere provate: {usate}</p>'
        st.markdown(
            f'<div class="forca-panel">'
            f'<p class="forca-word"><strong>{parola_vis}</strong></p>'
            f"{lettere_html}"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.progress(stato["errori"] / MAX_ERRORI, text=f"Errori: {stato['errori']}/{MAX_ERRORI}")

        if not stato["vinto"] and not stato["perso"]:
            with st.form("forca_lettera", clear_on_submit=True):
                lettera = st.text_input("Inserisci una lettera", max_chars=1)
                inviato = st.form_submit_button("Prova lettera", use_container_width=True)

            if inviato and lettera:
                _prova_lettera(stato, lettera)

    if stato["vinto"]:
        st.success(f"Complimenti! Hai indovinato la parola: **{stato['parola']}**")
        if st.button("Nuova partita", key="forca_reset_vinto", use_container_width=True):
            st.session_state[SESSION_KEY] = _nuova_partita()
            st.rerun()
        return

    if stato["perso"]:
        st.error(f"Hai perso! La parola era: **{stato['parola']}**")
        if st.button("Nuova partita", key="forca_reset_perso", use_container_width=True):
            st.session_state[SESSION_KEY] = _nuova_partita()
            st.rerun()
        return
