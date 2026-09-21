"""Gioco: Scopa (1 vs 1 contro il computer) — carte napoletane."""

import random
from itertools import combinations

import streamlit as st

from giochi.guida_ui import render_guida_expander
from giochi.briscola import (
    SEMI,
    _crea_mazzo,
    _css_tavolo,
    _html_carta,
    _html_carta_dorso,
    _nome_carta,
    _seme_carta,
    _valore_carta,
)

SESSION_KEY = "scopa"
PUNTI_VITTORIA = 11
SETTEBELLO = "7O"

_VALORE_SCOPA = {"A": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "F": 8, "C": 9, "R": 10}
_PRIMIERA = {"7": 21, "6": 18, "A": 16, "5": 15, "4": 14, "3": 13, "2": 12, "R": 10, "C": 10, "F": 10}


def _valore_gioco(carta):
    return _VALORE_SCOPA[_valore_carta(carta)]


def _conta_denari(carte):
    return sum(1 for c in carte if _seme_carta(c) == "O")


def _primiera_totale(carte):
    tot = 0
    for seme in SEMI:
        del_seme = [c for c in carte if _seme_carta(c) == seme]
        if del_seme:
            tot += max(_PRIMIERA[_valore_carta(c)] for c in del_seme)
    return tot


def _combinazioni_cattura(tavolo, valore):
    if not tavolo:
        return []
    combo = []
    for size in range(1, len(tavolo) + 1):
        for indici in combinations(range(len(tavolo)), size):
            if sum(_valore_gioco(tavolo[i]) for i in indici) == valore:
                combo.append(list(indici))
    return combo


def _desc_combo(tavolo, indici):
    return " + ".join(_nome_carta(tavolo[i]) for i in indici)


def _punteggio_combo(tavolo, indici, lascia_tavolo_vuoto):
    catturate = [tavolo[i] for i in indici]
    score = len(catturate) * 2
    score += _conta_denari(catturate) * 5
    if SETTEBELLO in catturate:
        score += 40
    if lascia_tavolo_vuoto:
        score += 100
    return score


def _scegli_combo_migliore(tavolo, combos):
    if not combos:
        return None
    return max(
        combos,
        key=lambda idx: _punteggio_combo(
            tavolo, idx, len(tavolo) - len(idx) == 0
        ),
    )


def _nuova_mano(stato):
    mazzo = _crea_mazzo()
    random.shuffle(mazzo)
    stato["mazzo"] = mazzo
    stato["mano_giocatore"] = [mazzo.pop(), mazzo.pop(), mazzo.pop()]
    stato["mano_computer"] = [mazzo.pop(), mazzo.pop(), mazzo.pop()]
    stato["tavolo"] = [mazzo.pop(), mazzo.pop(), mazzo.pop(), mazzo.pop()]
    stato["catture_giocatore"] = []
    stato["catture_computer"] = []
    stato["scope_giocatore"] = 0
    stato["scope_computer"] = 0
    stato["turno"] = "giocatore"
    stato["fase"] = "gioco"
    stato["ultimo_catturante"] = None
    stato["pending_carta"] = None
    stato["pending_combo"] = []
    stato["messaggio"] = "Gioca una carta: cattura somme uguali o lascia sul tavolo."
    stato["riepilogo_mano"] = None
    stato["pending_carta"] = None
    stato["pending_combo"] = []


def _nuova_partita():
    stato = {
        "punti_partita_g": 0,
        "punti_partita_c": 0,
        "mano_num": 1,
        "partita_finita": False,
        "vincitore_partita": None,
    }
    _nuova_mano(stato)
    return stato


def _ridistribuisci(stato):
    if stato["mano_giocatore"] or stato["mano_computer"] or not stato["mazzo"]:
        return
    if len(stato["mazzo"]) >= 6:
        for _ in range(3):
            stato["mano_giocatore"].append(stato["mazzo"].pop())
            stato["mano_computer"].append(stato["mazzo"].pop())
        stato["messaggio"] = "Nuove tre carte distribuite."
    elif stato["mazzo"]:
        while stato["mazzo"]:
            if len(stato["mano_giocatore"]) <= len(stato["mano_computer"]):
                stato["mano_giocatore"].append(stato["mazzo"].pop())
            else:
                stato["mano_computer"].append(stato["mazzo"].pop())


def _applica_cattura(stato, chi, carta, indici_tavolo):
    catture = stato["catture_giocatore"] if chi == "giocatore" else stato["catture_computer"]
    prese = [stato["tavolo"][i] for i in sorted(indici_tavolo, reverse=True)]
    for i in sorted(indici_tavolo, reverse=True):
        stato["tavolo"].pop(i)
    catture.extend(prese)
    catture.append(carta)
    stato["ultimo_catturante"] = chi
    scopa = not stato["tavolo"]
    if scopa:
        if chi == "giocatore":
            stato["scope_giocatore"] += 1
        else:
            stato["scope_computer"] += 1
        nome = "Tu" if chi == "giocatore" else "Computer"
        stato["messaggio"] = f"SCOPA! {nome} ha pulito il tavolo."
    elif chi == "giocatore":
        nomi = " + ".join(_nome_carta(c) for c in prese)
        stato["messaggio"] = f"Hai catturato: {nomi}."
    else:
        stato["messaggio"] = "Il computer ha catturato carte dal tavolo."


def _gioca_sul_tavolo(stato, chi, carta):
    stato["tavolo"].append(carta)
    if chi == "giocatore":
        stato["messaggio"] = f"{_nome_carta(carta)} lasciata sul tavolo."
    else:
        stato["messaggio"] = f"Il computer gioca {_nome_carta(carta)} sul tavolo."


def _fine_mano(stato):
    if stato["tavolo"] and stato["ultimo_catturante"]:
        target = (
            stato["catture_giocatore"]
            if stato["ultimo_catturante"] == "giocatore"
            else stato["catture_computer"]
        )
        target.extend(stato["tavolo"])
        stato["tavolo"] = []
        stato["messaggio"] = "Carte rimaste al tavolo assegnate all'ultimo che ha catturato."

    cg, cc = stato["catture_giocatore"], stato["catture_computer"]
    pg = stato["scope_giocatore"]
    pc = stato["scope_computer"]

    if len(cg) > len(cc):
        pg += 1
    elif len(cc) > len(cg):
        pc += 1

    dg, dc = _conta_denari(cg), _conta_denari(cc)
    if dg > dc:
        pg += 1
    elif dc > dg:
        pc += 1

    if SETTEBELLO in cg:
        pg += 1
    elif SETTEBELLO in cc:
        pc += 1

    prim_g, prim_c = _primiera_totale(cg), _primiera_totale(cc)
    if prim_g > prim_c:
        pg += 1
    elif prim_c > prim_g:
        pc += 1

    stato["punti_partita_g"] += pg
    stato["punti_partita_c"] += pc
    stato["riepilogo_mano"] = {
        "pg": pg,
        "pc": pc,
        "carte_g": len(cg),
        "carte_c": len(cc),
        "denari_g": dg,
        "denari_c": dc,
        "settebello_g": SETTEBELLO in cg,
        "settebello_c": SETTEBELLO in cc,
        "primiera_g": prim_g,
        "primiera_c": prim_c,
        "scope_g": stato["scope_giocatore"],
        "scope_c": stato["scope_computer"],
    }

    if stato["punti_partita_g"] >= PUNTI_VITTORIA or stato["punti_partita_c"] >= PUNTI_VITTORIA:
        if stato["punti_partita_g"] > stato["punti_partita_c"]:
            stato["vincitore_partita"] = "giocatore"
            stato["messaggio"] = (
                f"Partita vinta! {stato['punti_partita_g']}–{stato['punti_partita_c']}."
            )
        elif stato["punti_partita_c"] > stato["punti_partita_g"]:
            stato["vincitore_partita"] = "computer"
            stato["messaggio"] = (
                f"Partita persa. {stato['punti_partita_g']}–{stato['punti_partita_c']}."
            )
        else:
            stato["vincitore_partita"] = "pareggio"
            stato["messaggio"] = "Partita in pareggio!"
        stato["partita_finita"] = True
        stato["fase"] = "fine"
    else:
        stato["mano_num"] += 1
        stato["fase"] = "riepilogo_mano"
        stato["messaggio"] = f"Mano {stato['mano_num'] - 1} chiusa: +{pg} a te, +{pc} al computer."


def _avanza_turno(stato):
    stato["turno"] = "computer" if stato["turno"] == "giocatore" else "giocatore"
    _ridistribuisci(stato)
    if not stato["mano_giocatore"] and not stato["mano_computer"] and not stato["mazzo"]:
        _fine_mano(stato)


def _esegui_giocata(stato, chi, carta, indici=None):
    mano = stato["mano_giocatore"] if chi == "giocatore" else stato["mano_computer"]
    if carta not in mano:
        return
    mano.remove(carta)

    combos = _combinazioni_cattura(stato["tavolo"], _valore_gioco(carta))
    if combos:
        scelti = indici if indici is not None else _scegli_combo_migliore(stato["tavolo"], combos)
        _applica_cattura(stato, chi, carta, scelti)
    else:
        _gioca_sul_tavolo(stato, chi, carta)

    stato["pending_carta"] = None
    stato["pending_combo"] = []
    stato["fase"] = "gioco"
    _avanza_turno(stato)


def _valuta_carta_cpu(carta, tavolo):
    combos = _combinazioni_cattura(tavolo, _valore_gioco(carta))
    if combos:
        best = _scegli_combo_migliore(tavolo, combos)
        return _punteggio_combo(tavolo, best, len(tavolo) - len(best) == 0)
    penalty = 0
    nuovo_tavolo = tavolo + [carta]
    for alt in _crea_mazzo():
        if _combinazioni_cattura(nuovo_tavolo, _valore_gioco(alt)):
            penalty += 1
    return -_valore_gioco(carta) - penalty * 3


def _mossa_computer(stato):
    if stato["partita_finita"] or stato["turno"] != "computer" or stato["fase"] != "gioco":
        return
    carte = stato["mano_computer"]
    if not carte:
        _avanza_turno(stato)
        return
    carta = max(carte, key=lambda c: _valuta_carta_cpu(c, stato["tavolo"]))
    _esegui_giocata(stato, "computer", carta)


def _html_tabella_punteggi():
    righe = (
        ("Scope (tavolo pulito)", "1 ciascuna"),
        ("Più carte catturate", "1"),
        ("Più Denari", "1"),
        ("Settebello (7 di Denari)", "1"),
        ("Primiera (miglior carta per seme)", "1"),
    )
    corpo = "".join(
        f'<tr><td>{nome}</td><td class="br-score-pts">{pt}</td></tr>' for nome, pt in righe
    )
    return (
        '<div class="br-score-wrap">'
        + '<div class="br-score-title">Punteggio Scopa</div>'
        + '<table class="br-score-table">'
        + '<thead><tr><th>Premio</th><th style="text-align:center">Punti</th></tr></thead>'
        + f"<tbody>{corpo}</tbody>"
        + "</table>"
        + '<div class="br-score-note">'
        + f"<strong>Obiettivo:</strong> {PUNTI_VITTORIA} punti. "
        + "Cattura dal tavolo per <strong>valore</strong> o <strong>somma</strong>; "
        + "scopa se lo svuoti. A fine mano valgono scope e i premi in tabella. "
        + "Primiera: per seme conta la carta migliore catturata "
        + "(7=21, 6=18, A=16, 5=15, 4=14, 3=13, 2=12, figure=10)."
        + "</div></div>"
    )


def _render_guida_punteggi():
    render_guida_expander(_html_tabella_punteggi())


def _html_tavolo(stato):
    tavolo_html = (
        "".join(_html_carta(c, piccola=True) for c in stato["tavolo"])
        or '<span style="color:#f5e6c8;font-size:0.85rem">Tavolo vuoto</span>'
    )
    mano_pc = "".join(_html_carta_dorso() for _ in stato["mano_computer"]) or (
        '<span style="color:#888;font-size:0.8rem">—</span>'
    )
    mano_g = "".join(_html_carta(c) for c in stato["mano_giocatore"]) or (
        '<span style="color:#888;font-size:0.8rem">—</span>'
    )
    scope_txt = f"Scope mano: Tu {stato['scope_giocatore']} · PC {stato['scope_computer']}"
    return (
        _css_tavolo()
        + '<div class="br-table">'
        + f'<div class="br-msg">{stato.get("messaggio", "")}</div>'
        + f'<div class="br-msg" style="font-style:normal;font-size:0.78rem">{scope_txt}</div>'
        + '<div class="br-label">🎩 Computer</div>'
        + f'<div class="br-hand">{mano_pc}</div>'
        + '<div class="br-label">Tavolo</div>'
        + f'<div class="br-trick" style="flex-wrap:wrap;gap:8px">{tavolo_html}</div>'
        + '<div class="br-label">🃏 Tu</div>'
        + f'<div class="br-hand">{mano_g}</div>'
        + "</div>"
    )


def _inizializza():
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = _nuova_partita()


def render():
    """Interfaccia Streamlit per 'Scopa'."""
    _inizializza()
    stato = st.session_state[SESSION_KEY]

    st.subheader("Scopa")

    pg, pc = stato["punti_partita_g"], stato["punti_partita_c"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tu", pg, delta=f"{'▲' if pg >= PUNTI_VITTORIA else ''}")
    c2.metric("Computer", pc)
    c3.metric("Mano", stato["mano_num"])
    c4.metric("Carte tavolo", len(stato["tavolo"]))

    st.progress(min(max(pg, pc) / PUNTI_VITTORIA, 1.0), text=f"Obiettivo: {PUNTI_VITTORIA} pt")
    st.markdown(_html_tavolo(stato), unsafe_allow_html=True)

    if stato.get("riepilogo_mano") and stato["fase"] == "riepilogo_mano":
        r = stato["riepilogo_mano"]
        st.info(
            f"**Mano {stato['mano_num'] - 1}** — Tu +{r['pg']} · PC +{r['pc']} · "
            f"Carte {r['carte_g']}–{r['carte_c']} · Denari {r['denari_g']}–{r['denari_c']} · "
            f"Primiera {r['primiera_g']}–{r['primiera_c']} · Scope {r['scope_g']}–{r['scope_c']}"
        )
        if st.button("Prossima mano", key="scopa_prossima", type="primary", use_container_width=True):
            _nuova_mano(stato)
            st.rerun()

    if stato["partita_finita"]:
        v = stato["vincitore_partita"]
        if v == "giocatore":
            st.success(stato["messaggio"])
        elif v == "pareggio":
            st.warning(stato["messaggio"])
        else:
            st.error(stato["messaggio"])
        if st.button("Nuova partita", key="scopa_nuova", type="primary", use_container_width=True):
            st.session_state[SESSION_KEY] = _nuova_partita()
            st.rerun()
        _render_guida_punteggi()
        return

    if stato["fase"] == "riepilogo_mano":
        _render_guida_punteggi()
        return

    if stato["turno"] == "computer" and stato["fase"] == "gioco":
        _mossa_computer(stato)
        st.rerun()

    if stato["fase"] == "scegli_cattura" and stato["pending_carta"]:
        st.caption("Scegli **come catturare** (obbligatorio):")

        def _combo_key(indici):
            return "-".join(str(i) for i in indici)

        for idx, combo in enumerate(stato["pending_combo"]):
            desc = _desc_combo(
                [c for c in stato["tavolo"]],
                combo,
            )
            scopa = " · SCOPA!" if len(stato["tavolo"]) - len(combo) == 0 else ""
            if st.button(
                f"Cattura: {desc}{scopa}",
                key=f"scopa_combo_{_combo_key(combo)}_{stato['mano_num']}",
                use_container_width=True,
            ):
                carta = stato["pending_carta"]
                stato["mano_giocatore"].remove(carta)
                _applica_cattura(stato, "giocatore", carta, combo)
                stato["pending_carta"] = None
                stato["pending_combo"] = []
                stato["fase"] = "gioco"
                _avanza_turno(stato)
                if stato["turno"] == "computer" and stato["fase"] == "gioco":
                    _mossa_computer(stato)
                st.rerun()
        _render_guida_punteggi()
        return

    if stato["turno"] == "giocatore" and stato["mano_giocatore"] and stato["fase"] == "gioco":
        st.caption("Scegli una carta da giocare.")
        carte = list(stato["mano_giocatore"])
        cols = st.columns(min(len(carte), 3))
        for i, carta in enumerate(carte):
            val = _valore_gioco(carta)
            label = f"{_nome_carta(carta)} (val. {val})"
            combos = _combinazioni_cattura(stato["tavolo"], val)
            if combos:
                label += " · cattura"
            with cols[i % len(cols)]:
                if st.button(
                    label,
                    key=f"scopa_card_{i}_{carta}_{stato['mano_num']}",
                    use_container_width=True,
                ):
                    if len(combos) > 1:
                        stato["pending_carta"] = carta
                        stato["pending_combo"] = combos
                        stato["fase"] = "scegli_cattura"
                    elif len(combos) == 1:
                        _esegui_giocata(stato, "giocatore", carta, combos[0])
                        if stato["turno"] == "computer" and stato["fase"] == "gioco":
                            _mossa_computer(stato)
                    else:
                        _esegui_giocata(stato, "giocatore", carta, None)
                        if stato["turno"] == "computer" and stato["fase"] == "gioco":
                            _mossa_computer(stato)
                    st.rerun()

    _render_guida_punteggi()
