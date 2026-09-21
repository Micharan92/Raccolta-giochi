"""Gioco: Quiz in italiano — modalità classica e tabellone a spicchi."""

import copy
import random

import streamlit as st

from giochi.domande_quiz import CATEGORIE, DIFFICOLTA, DOMANDE_ITALIANE
from giochi import quiz_trivial

SESSION_KEY = "quiz"
MODALITA = ("Classico", "Tabellone a spicchi")


def _mescola_opzioni(domanda):
    """Mescola l'ordine delle risposte mantenendo la lettera corretta."""
    domanda = copy.deepcopy(domanda)
    testi = list(domanda["opzioni"].values())
    random.shuffle(testi)
    lettere = ["a", "b", "c", "d"]
    risposta_corretta = domanda["opzioni"][domanda["risposta"]]
    domanda["opzioni"] = {lettere[i]: testi[i] for i in range(4)}
    domanda["risposta"] = lettere[testi.index(risposta_corretta)]
    return domanda


def _filtra_pool(categoria, difficolta):
    pool = DOMANDE_ITALIANE
    if categoria != "Tutte":
        pool = [d for d in pool if d["categoria"] == categoria]
    if difficolta != "Qualsiasi":
        pool = [d for d in pool if d["difficolta"] == difficolta]
    return pool


def _carica_domande(numero=10, difficolta="Qualsiasi", categoria="Tutte"):
    pool = _filtra_pool(categoria, difficolta)
    if len(pool) < numero:
        raise ValueError(
            f"Solo {len(pool)} domande disponibili per questi filtri. "
            f"Riduci il numero o cambia categoria/difficoltà."
        )
    scelte = random.sample(pool, numero)
    return [_mescola_opzioni(d) for d in scelte]


def _stato_config():
    return {
        "avviato": False,
        "domande": [],
        "indice": 0,
        "punteggio": 0,
        "completato": False,
        "feedback": None,
        "numero": 10,
        "difficolta": "Qualsiasi",
        "categoria": "Tutte",
        "partita_id": 0,
    }


def _stato_vuoto(numero, difficolta, categoria):
    return {
        "avviato": True,
        "domande": _carica_domande(numero, difficolta, categoria),
        "indice": 0,
        "punteggio": 0,
        "completato": False,
        "feedback": None,
        "numero": numero,
        "difficolta": difficolta,
        "categoria": categoria,
        "partita_id": random.randint(1, 1_000_000),
    }


def _inizializza_classico():
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = _stato_config()
    elif "avviato" not in st.session_state[SESSION_KEY]:
        st.session_state[SESSION_KEY]["avviato"] = bool(
            st.session_state[SESSION_KEY].get("domande")
        )


def _reset(numero, difficolta, categoria):
    st.session_state[SESSION_KEY] = _stato_vuoto(numero, difficolta, categoria)


def _render_classico():
    _inizializza_classico()
    stato = st.session_state[SESSION_KEY]
    domande = stato["domande"]
    totale = len(domande)

    st.write(
        f"Domande in **italiano** scelte a caso dal database "
        f"({len(DOMANDE_ITALIANE)} domande totali)."
    )

    col1, col2, col3 = st.columns(3)
    opzioni_numero = [5, 10, 15, 20, 25, 30]
    with col1:
        numero = st.selectbox(
            "Domande",
            opzioni_numero,
            index=opzioni_numero.index(stato["numero"]) if stato["numero"] in opzioni_numero else 1,
            key="quiz_class_num",
        )
    with col2:
        difficolta = st.selectbox(
            "Difficoltà",
            DIFFICOLTA,
            index=DIFFICOLTA.index(stato["difficolta"]) if stato["difficolta"] in DIFFICOLTA else 0,
            key="quiz_class_diff",
        )
    with col3:
        categorie = ["Tutte", *CATEGORIE]
        categoria = st.selectbox(
            "Categoria",
            categorie,
            index=categorie.index(stato["categoria"]) if stato["categoria"] in categorie else 0,
            key="quiz_class_cat",
        )

    if not stato["avviato"]:
        st.info("Seleziona **categoria**, **difficoltà** e numero di domande, poi avvia il quiz.")
        if st.button("Inizia quiz", type="primary", key="quiz_inizia", use_container_width=True):
            try:
                _reset(numero, difficolta, categoria)
                st.rerun()
            except ValueError as errore:
                st.error(str(errore))
        return

    if st.button("Nuove domande casuali", type="primary", key="quiz_nuovo", use_container_width=True):
        try:
            _reset(numero, difficolta, categoria)
            st.rerun()
        except ValueError as errore:
            st.error(str(errore))

    if stato["completato"]:
        st.success(f"Hai totalizzato {stato['punteggio']}/{totale} risposte corrette.")
        if st.button("Gioca ancora con domande nuove", key="quiz_reset", use_container_width=True):
            try:
                _reset(numero, difficolta, categoria)
                st.rerun()
            except ValueError as errore:
                st.error(str(errore))
        return

    domanda = domande[stato["indice"]]
    st.progress(stato["indice"] / totale)
    st.markdown(f"**Domanda {stato['indice'] + 1}/{totale}:** {domanda['domanda']}")
    st.caption(f"Categoria: {domanda['categoria']} · Difficoltà: {domanda['difficolta']}")

    opzioni = [f"{k}) {v}" for k, v in domanda["opzioni"].items()]
    lettere = list(domanda["opzioni"].keys())
    risposta = st.radio(
        "La tua risposta",
        opzioni,
        key=f"quiz_q{stato['indice']}_{stato['partita_id']}",
    )

    if stato["feedback"]:
        if stato["feedback"]["corretto"]:
            st.success("Corretto!")
        else:
            st.error(f"Sbagliato! La risposta corretta era: {stato['feedback']['corretta']}")
        if st.button("Prossima domanda", key="quiz_avanti", use_container_width=True):
            if stato["indice"] + 1 >= totale:
                stato["completato"] = True
            else:
                stato["indice"] += 1
            stato["feedback"] = None
            st.rerun()
        return

    if st.button("Conferma risposta", key="quiz_conferma", use_container_width=True):
        lettera_scelta = lettere[opzioni.index(risposta)]
        corretto = lettera_scelta == domanda["risposta"]
        if corretto:
            stato["punteggio"] += 1
        stato["feedback"] = {
            "corretto": corretto,
            "corretta": domanda["opzioni"][domanda["risposta"]],
        }
        st.rerun()


def render():
    """Interfaccia Streamlit per 'Quiz'."""
    st.subheader("Quiz")
    modalita = st.radio("Modalità", MODALITA, horizontal=True, key="quiz_modalita")

    if modalita == "Tabellone a spicchi":
        quiz_trivial.render()
    else:
        _render_classico()
