"""Gioco: Blackjack con animazione distribuzione carte."""

import random

import streamlit as st

SEMI = ["♠", "♥", "♦", "♣"]
VALORI = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SESSION_KEY = "blackjack"
SEMI_ROSSI = {"♥", "♦"}
FASI_VALIDE = frozenset({"distribuzione", "giocatore", "banco", "fine"})


def _crea_mazzo():
    return [f"{valore}{seme}" for seme in SEMI for valore in VALORI]


def _valore_carta(carta):
    valore = carta[:-1]
    if valore in ("J", "Q", "K"):
        return 10
    if valore == "A":
        return 11
    return int(valore)


def _punteggio_mano(carte):
    totale = sum(_valore_carta(carta) for carta in carte)
    assi = sum(1 for carta in carte if carta.startswith("A"))
    while totale > 21 and assi > 0:
        totale -= 10
        assi -= 1
    return totale


def _seme_carta(carta):
    return carta[-1]


def _valore_visivo(carta):
    return carta[:-1]


def _css_tavolo():
    return """
    <style>
    .bj-table {
        background: linear-gradient(145deg, #0d5c2e 0%, #1a7a3e 50%, #0d5c2e 100%);
        border: 4px solid #8b6914;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: inset 0 0 30px rgba(0,0,0,0.3);
    }
    .bj-zone { margin: 0.75rem 0; }
    .bj-label {
        color: #f5e6c8;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        letter-spacing: 0.05em;
    }
    .bj-score { color: #d4af37; font-size: 0.85rem; margin-top: 0.4rem; }
    .bj-hand {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        min-height: 110px;
        align-items: flex-start;
    }
    .bj-card {
        width: 62px;
        height: 88px;
        border-radius: 8px;
        background: #fffef8;
        border: 2px solid #ccc;
        box-shadow: 2px 4px 8px rgba(0,0,0,0.35);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 6px;
        font-weight: 700;
        line-height: 1;
        animation: bjDeal 0.45s ease-out both;
    }
    .bj-card.red { color: #c0392b; }
    .bj-card.black { color: #1a1a2e; }
    .bj-card.back {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        border-color: #4a7ab0;
        color: #fff;
        justify-content: center;
        align-items: center;
        font-size: 1.6rem;
    }
    .bj-card-val-top { font-size: 1rem; }
    .bj-card-suit-mid {
        font-size: 1.4rem;
        text-align: center;
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .bj-card-val-bot {
        font-size: 1rem;
        text-align: right;
        transform: rotate(180deg);
    }
    .bj-dealer-msg {
        color: #f5e6c8;
        font-style: italic;
        text-align: center;
        margin: 0.5rem 0;
        min-height: 1.2rem;
    }
    @keyframes bjDeal {
        0% { transform: translateY(-50px) scale(0.6) rotate(-8deg); opacity: 0; }
        70% { transform: translateY(4px) scale(1.02) rotate(1deg); opacity: 1; }
        100% { transform: translateY(0) scale(1) rotate(0deg); opacity: 1; }
    }
    </style>
    """


def _html_carta(carta, nascosta=False, delay=0):
    if nascosta:
        return f'<div class="bj-card back" style="animation-delay:{delay}s">🂠</div>'

    seme = _seme_carta(carta)
    valore = _valore_visivo(carta)
    colore = "red" if seme in SEMI_ROSSI else "black"
    return (
        f'<div class="bj-card {colore}" style="animation-delay:{delay}s">'
        f'<div class="bj-card-val-top">{valore}{seme}</div>'
        f'<div class="bj-card-suit-mid">{seme}</div>'
        f'<div class="bj-card-val-bot">{valore}{seme}</div>'
        f"</div>"
    )


def _html_mano(carte, nascoste=None, visibili=None, base_delay=0):
    nascoste = nascoste or set()
    carte_da_mostrare = carte[:visibili] if visibili is not None else carte
    pezzi = [
        _html_carta(carta, nascosta=i in nascoste, delay=base_delay + i * 0.12)
        for i, carta in enumerate(carte_da_mostrare)
    ]
    return f'<div class="bj-hand">{"".join(pezzi)}</div>'


def _visibilita_distribuzione(step):
    """Quante carte mostrare durante l'animazione iniziale (step 1-4)."""
    mappa = {
        0: (0, 0),
        1: (1, 0),
        2: (1, 1),
        3: (2, 1),
        4: (2, 2),
    }
    return mappa.get(step, (2, 2))


def _messaggio_distribuzione(step):
    messaggi = {
        1: "Il banco distribuisce una carta a te...",
        2: "Il banco si dà una carta...",
        3: "Un'altra carta per te...",
        4: "E una coperta per il banco...",
    }
    return messaggi.get(step, "A te la mossa!")


def _html_tavolo(stato):
    mano_g = stato["mano_giocatore"]
    mano_b = stato["mano_banco"]
    fase = stato["fase"]
    messaggio = stato.get("messaggio_dealer", "")

    if fase == "distribuzione":
        step = stato["step_distribuzione"]
        messaggio = _messaggio_distribuzione(step)
        carte_g, carte_b = _visibilita_distribuzione(step)
        nascoste_banco = {1} if carte_b >= 2 else set()
        html_g = _html_mano(mano_g, visibili=carte_g)
        html_b = _html_mano(mano_b, nascoste=nascoste_banco, visibili=carte_b)
        score_g = f"Totale: {_punteggio_mano(mano_g[:carte_g])}" if carte_g else ""
        if carte_b == 1:
            score_b = f"Carta visibile: {_valore_carta(mano_b[0])}"
        elif carte_b >= 2:
            score_b = f"Totale: {_punteggio_mano(mano_b[:carte_b])}"
        else:
            score_b = ""
    else:
        rivela_banco = fase in ("banco", "fine")
        nascoste_banco = set()
        if not rivela_banco and len(mano_b) >= 2:
            nascoste_banco.add(1)
        html_g = _html_mano(mano_g)
        html_b = _html_mano(mano_b, nascoste=nascoste_banco)
        score_g = f"Totale: {_punteggio_mano(mano_g)}" if mano_g else ""
        if rivela_banco:
            score_b = f"Totale: {_punteggio_mano(mano_b)}" if mano_b else ""
        elif mano_b:
            score_b = f"Carta visibile: {_valore_carta(mano_b[0])}"
        else:
            score_b = ""

    return (
        _css_tavolo()
        + '<div class="bj-table">'
        + f'<div class="bj-dealer-msg">{messaggio}</div>'
        + '<div class="bj-zone"><div class="bj-label">🎩 Banco</div>'
        + html_b
        + f'<div class="bj-score">{score_b}</div></div>'
        + '<div class="bj-zone"><div class="bj-label">🃏 Tu</div>'
        + html_g
        + f'<div class="bj-score">{score_g}</div></div>'
        + "</div>"
    )


def _distribuisci_iniziale(stato):
    stato["mano_giocatore"] = [stato["mazzo"].pop(), stato["mazzo"].pop()]
    stato["mano_banco"] = [stato["mazzo"].pop(), stato["mazzo"].pop()]


def _nuova_partita():
    mazzo = _crea_mazzo()
    random.shuffle(mazzo)
    stato = {
        "mazzo": mazzo,
        "mano_giocatore": [],
        "mano_banco": [],
        "fase": "distribuzione",
        "step_distribuzione": 0,
        "messaggio": None,
        "messaggio_dealer": "",
        "banco_rivelato": False,
    }
    _distribuisci_iniziale(stato)
    return stato


def _calcola_esito(stato):
    punteggio_giocatore = _punteggio_mano(stato["mano_giocatore"])
    punteggio_banco = _punteggio_mano(stato["mano_banco"])

    if punteggio_banco > 21:
        return "Il banco ha superato 21! Hai vinto!"
    if punteggio_giocatore > punteggio_banco:
        return "Hai vinto!"
    if punteggio_giocatore < punteggio_banco:
        return "Hai perso!"
    return "Pareggio!"


def _avanza_distribuzione(stato):
    stato["step_distribuzione"] += 1
    if stato["step_distribuzione"] > 4:
        stato["fase"] = "giocatore"
        stato["messaggio_dealer"] = ""


def _avanza_turno_banco(stato):
    if not stato["banco_rivelato"]:
        stato["banco_rivelato"] = True
        stato["messaggio_dealer"] = "Il banco scopre la carta coperta..."
        return False

    if _punteggio_mano(stato["mano_banco"]) < 17:
        if not stato["mazzo"]:
            stato["messaggio"] = _calcola_esito(stato)
            stato["fase"] = "fine"
            stato["messaggio_dealer"] = ""
            return True
        stato["mano_banco"].append(stato["mazzo"].pop())
        stato["messaggio_dealer"] = "Il banco pesca un'altra carta..."
        return False

    stato["messaggio"] = _calcola_esito(stato)
    stato["fase"] = "fine"
    stato["messaggio_dealer"] = ""
    return True


def _normalizza_stato(stato):
    """Ripara stati incoerenti lasciati da versioni precedenti o interruzioni."""
    fase = stato.get("fase")

    if fase not in FASI_VALIDE:
        stato["fase"] = "fine" if stato.get("messaggio") else "giocatore"

    if fase in ("animazione_giocatore", "animazione_banco"):
        stato.pop("animazione_attiva", None)
        if stato.get("messaggio"):
            stato["fase"] = "fine"
        elif fase == "animazione_giocatore":
            stato["fase"] = "giocatore"
        else:
            stato["fase"] = "banco"
            stato["banco_rivelato"] = True

    stato.setdefault("step_distribuzione", 0)
    stato.setdefault("messaggio_dealer", "")
    stato.setdefault("banco_rivelato", False)

    if stato["fase"] == "giocatore" and len(stato.get("mano_giocatore", [])) < 2:
        if stato.get("mazzo"):
            _distribuisci_iniziale(stato)
        stato["fase"] = "distribuzione"
        stato["step_distribuzione"] = 0

    if stato["fase"] == "fine" and not stato.get("messaggio"):
        stato["messaggio"] = _calcola_esito(stato)


def _inizializza():
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = _nuova_partita()
    _normalizza_stato(st.session_state[SESSION_KEY])


def _mostra_esito(messaggio):
    if "Hai perso" in messaggio:
        st.error(messaggio)
    elif messaggio == "Pareggio!":
        st.warning(messaggio)
    else:
        st.success(messaggio)


def render():
    """Interfaccia Streamlit per 'Blackjack'."""
    _inizializza()
    stato = st.session_state[SESSION_KEY]

    st.subheader("Blackjack")
    st.write("Avvicinati a 21 senza superarlo. L'asso vale 11 o 1.")

    tavolo = st.empty()
    tavolo.markdown(_html_tavolo(stato), unsafe_allow_html=True)

    # Distribuzione automatica: una carta per ogni rerun (senza time.sleep)
    if stato["fase"] == "distribuzione":
        if stato["step_distribuzione"] < 4:
            _avanza_distribuzione(stato)
            st.rerun()
        else:
            stato["fase"] = "giocatore"
            stato["messaggio_dealer"] = ""
            st.rerun()
        return

    if stato["fase"] == "giocatore":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Pesca carta", key="bj_carta"):
                if stato["mazzo"]:
                    stato["mano_giocatore"].append(stato["mazzo"].pop())
                stato["messaggio_dealer"] = "Il banco ti dà una carta..."
                if _punteggio_mano(stato["mano_giocatore"]) > 21:
                    stato["messaggio"] = "Hai superato 21! Hai perso."
                    stato["fase"] = "fine"
                    stato["messaggio_dealer"] = ""
                st.rerun()
        with col2:
            if st.button("Fermati", key="bj_ferma"):
                stato["fase"] = "banco"
                stato["banco_rivelato"] = False
                stato["messaggio_dealer"] = "Il banco scopre la carta coperta..."
                st.rerun()
        return

    # Turno banco: un passo per rerun fino alla fine
    if stato["fase"] == "banco":
        finito = _avanza_turno_banco(stato)
        tavolo.markdown(_html_tavolo(stato), unsafe_allow_html=True)
        if not finito:
            st.rerun()
        # Se finito, prosegue verso la sezione "fine"

    if stato["fase"] == "fine":
        if stato.get("messaggio"):
            _mostra_esito(stato["messaggio"])
        if st.button("Nuova partita", key="bj_reset"):
            st.session_state[SESSION_KEY] = _nuova_partita()
            st.rerun()
    elif stato["fase"] == "banco":
        # Pulsante di recupero se il turno del banco si blocca
        if st.button("Nuova partita", key="bj_reset_recupero"):
            st.session_state[SESSION_KEY] = _nuova_partita()
            st.rerun()
