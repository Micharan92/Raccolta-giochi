"""Gioco: Tris con tavolo grafico stile casino."""

import random

import streamlit as st

from giochi.tris_component import tris_board_component
from giochi.tris_ui import VUOTO, css_tris_wrap

GIOCATORE = "X"
COMPUTER = "O"
SESSION_KEY = "tris"
CLICK_KEY = "tris_ultimo_click"
CENTRO = 4
ANGOLI = (0, 2, 6, 8)

DIFFICOLTA_OPZIONI = ("Facile", "Medio", "Difficile")
_DIFFICOLTA_DESC = {
    "Facile": "Il PC spesso non vede le minacce: basta un po' di tattica per vincere.",
    "Medio": "Blocca le file, controlla il centro e reagisce ai trucchi più comuni.",
    "Difficile": "Difesa solida e pochi errori: resta battibile, ma non regala nulla.",
}
_PROFILI_AI = {
    "Facile": {"prob_vince": 0.4, "prob_blocca": 0.5, "prob_strategia": 0.3, "prob_blocca_fork": 0.2},
    "Medio": {"prob_vince": 0.9, "prob_blocca": 0.86, "prob_strategia": 0.78, "prob_blocca_fork": 0.55, "rumore": 0.18},
    "Difficile": {"rumore": 0.1},
}

COMBINAZIONI = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


def _nuova_griglia():
    return [VUOTO] * 9


def _ha_vinto(griglia, simbolo):
    return any(all(griglia[i] == simbolo for i in combo) for combo in COMBINAZIONI)


def _linea_vincente(griglia, simbolo):
    for combo in COMBINAZIONI:
        if all(griglia[i] == simbolo for i in combo):
            return combo
    return None


def _pareggio(griglia):
    return VUOTO not in griglia


def _mosse_disponibili(griglia):
    return [i for i, cella in enumerate(griglia) if cella == VUOTO]


def _simula_mossa(griglia, indice, simbolo):
    nuova = list(griglia)
    nuova[indice] = simbolo
    return nuova


def _trova_mossa_vincita(griglia, simbolo):
    for indice in _mosse_disponibili(griglia):
        if _ha_vinto(_simula_mossa(griglia, indice, simbolo), simbolo):
            return indice
    return None


def _conteggio_minacce_vittoria(griglia, simbolo):
    return sum(
        1
        for indice in _mosse_disponibili(griglia)
        if _ha_vinto(_simula_mossa(griglia, indice, simbolo), simbolo)
    )


def _miglior_mossa_fork(griglia, simbolo):
    miglior = None
    max_minacce = 1
    for indice in _mosse_disponibili(griglia):
        minacce = _conteggio_minacce_vittoria(_simula_mossa(griglia, indice, simbolo), simbolo)
        if minacce >= 2 and minacce >= max_minacce:
            max_minacce = minacce
            miglior = indice
    return miglior


def _mossa_blocco_fork(griglia):
    miglior = None
    min_minacce = 10
    for indice in _mosse_disponibili(griglia):
        dopo = _simula_mossa(griglia, indice, COMPUTER)
        minacce = _conteggio_minacce_vittoria(dopo, GIOCATORE)
        if minacce < min_minacce:
            min_minacce = minacce
            miglior = indice
    return miglior if min_minacce >= 2 else None


def _mossa_strategica(griglia):
    if griglia[CENTRO] == VUOTO:
        return CENTRO

    for angolo in ANGOLI:
        if griglia[angolo] == VUOTO:
            opposto = 8 - angolo
            if griglia[opposto] == GIOCATORE:
                return angolo

    for angolo in ANGOLI:
        if griglia[angolo] == VUOTO:
            return angolo

    liberi = _mosse_disponibili(griglia)
    return random.choice(liberi) if liberi else None


def _valuta_minimax(griglia, turno):
    if _ha_vinto(griglia, COMPUTER):
        return 10
    if _ha_vinto(griglia, GIOCATORE):
        return -10
    if _pareggio(griglia):
        return 0

    if turno == COMPUTER:
        punteggio = -11
        for indice in _mosse_disponibili(griglia):
            punteggio = max(punteggio, _valuta_minimax(_simula_mossa(griglia, indice, COMPUTER), GIOCATORE))
        return punteggio

    punteggio = 11
    for indice in _mosse_disponibili(griglia):
        punteggio = min(punteggio, _valuta_minimax(_simula_mossa(griglia, indice, GIOCATORE), COMPUTER))
    return punteggio


def _mossa_minimax(griglia):
    miglior_punteggio = -11
    candidate = []
    for indice in _mosse_disponibili(griglia):
        punteggio = _valuta_minimax(_simula_mossa(griglia, indice, COMPUTER), GIOCATORE)
        if punteggio > miglior_punteggio:
            miglior_punteggio = punteggio
            candidate = [indice]
        elif punteggio == miglior_punteggio:
            candidate.append(indice)
    return random.choice(candidate)


def _mosse_sicure(griglia):
    sicure = []
    for indice in _mosse_disponibili(griglia):
        dopo = _simula_mossa(griglia, indice, COMPUTER)
        if _trova_mossa_vincita(dopo, GIOCATORE) is None:
            sicure.append(indice)
    return sicure or _mosse_disponibili(griglia)


def _mossa_euristica(griglia, profilo):
    if random.random() < profilo["prob_vince"]:
        mossa = _trova_mossa_vincita(griglia, COMPUTER)
        if mossa is not None:
            return mossa

    if random.random() < profilo["prob_blocca"]:
        mossa = _trova_mossa_vincita(griglia, GIOCATORE)
        if mossa is not None:
            return mossa

    mossa = _miglior_mossa_fork(griglia, COMPUTER)
    if mossa is not None:
        return mossa

    if random.random() < profilo["prob_blocca_fork"]:
        mossa = _mossa_blocco_fork(griglia)
        if mossa is not None:
            return mossa

    if random.random() < profilo["prob_strategia"]:
        mossa = _mossa_strategica(griglia)
        if mossa is not None:
            return mossa

    return random.choice(_mosse_disponibili(griglia))


def _mossa_computer(griglia, difficolta="Medio"):
    profilo = _PROFILI_AI.get(difficolta, _PROFILI_AI["Medio"])

    if difficolta == "Difficile":
        mossa = _mossa_minimax(griglia)
    else:
        mossa = _mossa_euristica(griglia, profilo)

    if random.random() < profilo.get("rumore", 0.0):
        alternative = [m for m in _mosse_sicure(griglia) if m != mossa]
        if alternative:
            return random.choice(alternative)
    return mossa


def _inizializza():
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = {
            "griglia": _nuova_griglia(),
            "fine": False,
            "messaggio": None,
            "vincitore": None,
            "started": False,
            "difficolta": "Medio",
        }
    else:
        st.session_state[SESSION_KEY].setdefault("started", False)
        st.session_state[SESSION_KEY].setdefault("difficolta", "Medio")


def _reset():
    difficolta = st.session_state[SESSION_KEY].get("difficolta", "Medio")
    st.session_state[SESSION_KEY] = {
        "griglia": _nuova_griglia(),
        "fine": False,
        "messaggio": None,
        "vincitore": None,
        "started": False,
        "difficolta": difficolta,
    }
    st.session_state.pop(CLICK_KEY, None)


def _avvia_partita(stato):
    stato["griglia"] = _nuova_griglia()
    stato["fine"] = False
    stato["messaggio"] = None
    stato["vincitore"] = None
    stato["started"] = True


def _gioca_mossa(stato, indice):
    if stato["fine"] or stato["griglia"][indice] != VUOTO:
        return

    stato["griglia"][indice] = GIOCATORE

    if _ha_vinto(stato["griglia"], GIOCATORE):
        stato["fine"] = True
        stato["vincitore"] = GIOCATORE
        stato["messaggio"] = "Hai vinto!"
        return

    if _pareggio(stato["griglia"]):
        stato["fine"] = True
        stato["messaggio"] = "Pareggio!"
        return

    mossa_pc = _mossa_computer(stato["griglia"], stato.get("difficolta", "Medio"))
    stato["griglia"][mossa_pc] = COMPUTER

    if _ha_vinto(stato["griglia"], COMPUTER):
        stato["fine"] = True
        stato["vincitore"] = COMPUTER
        stato["messaggio"] = "Il computer ha vinto!"
    elif _pareggio(stato["griglia"]):
        stato["fine"] = True
        stato["messaggio"] = "Pareggio!"


def _status_testo(stato):
    if not stato["started"]:
        return "Premi ▶ Inizia gioco o clicca una casella sul tavolo."
    if stato["messaggio"]:
        return stato["messaggio"]
    return "Clicca una casella libera per giocare."


def _gestisci_click_componente(stato, idx_raw) -> bool:
    if idx_raw is None:
        return False
    try:
        idx = int(idx_raw)
    except (TypeError, ValueError):
        return False
    if idx < 0 or idx > 8:
        return False
    if idx == st.session_state.get(CLICK_KEY):
        return False
    st.session_state[CLICK_KEY] = idx
    if not stato["started"]:
        _avvia_partita(stato)
    if not stato["fine"] and stato["griglia"][idx] == VUOTO:
        _gioca_mossa(stato, idx)
        return True
    return False


def _render_tavolo(stato):
    vincenti = None
    if stato["fine"] and stato.get("vincitore"):
        vincenti = _linea_vincente(stato["griglia"], stato["vincitore"])

    st.markdown(css_tris_wrap(), unsafe_allow_html=True)
    _, col_tavolo, _ = st.columns([0.12, 1.76, 0.12])
    with col_tavolo:
        board = tris_board_component(
            stato["griglia"],
            _status_testo(stato),
            vincenti,
            stato["fine"],
            key="tris_board_component",
        )
        if _gestisci_click_componente(stato, board.cell_click):
            st.rerun()


def render():
    """Interfaccia Streamlit per 'Tris'."""
    _inizializza()
    stato = st.session_state[SESSION_KEY]

    st.subheader("Tris")
    st.write("Sfidare il computer a **tris** su un tavolo verde. Tu giochi **X** (blu), il PC gioca **O** (rosso).")

    if not stato["started"]:
        difficolta = st.selectbox(
            "Difficoltà avversario",
            DIFFICOLTA_OPZIONI,
            index=DIFFICOLTA_OPZIONI.index(stato.get("difficolta", "Medio")),
            key="tris_diff",
        )
        stato["difficolta"] = difficolta
        st.caption(_DIFFICOLTA_DESC[difficolta])
        if st.button("▶ Inizia gioco", key="tris_start_btn", type="primary", use_container_width=True):
            _avvia_partita(stato)
            st.rerun()
        st.caption("Puoi anche cliccare direttamente una casella sul tavolo per iniziare.")
    else:
        st.caption(f"Difficoltà: **{stato.get('difficolta', 'Medio')}**")

    _render_tavolo(stato)

    if stato["messaggio"]:
        msg = stato["messaggio"]
        if stato.get("vincitore") == GIOCATORE:
            st.success(msg)
        elif msg == "Pareggio!":
            st.warning(msg)
        else:
            st.error(msg)

        if st.button("🔄 Nuova partita", key="tris_reset", use_container_width=True):
            _reset()
            st.rerun()
