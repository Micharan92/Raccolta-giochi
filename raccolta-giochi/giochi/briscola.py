"""Gioco: Briscola (1 vs 1 contro il computer) — carte napoletane."""

import random

import streamlit as st

from giochi.guida_ui import render_guida_expander

# Semi napoletani: Denari, Coppe, Bastoni, Spade
SEMI = ["O", "P", "B", "S"]
_SEMI_INFO = {
    "O": {"nome": "Denari", "colore": "#d4a017"},
    "P": {"nome": "Coppe", "colore": "#c41e3a"},
    "B": {"nome": "Bastoni", "colore": "#2d7a3a"},
    "S": {"nome": "Spade", "colore": "#1d4ed8"},
}
VALORI = ["A", "2", "3", "4", "5", "6", "7", "F", "C", "R"]  # F=Fante, C=Cavallo, R=Re
_FIGURE = {"F", "C", "R"}
SESSION_KEY = "briscola"
PUNTI_VITTORIA = 61
_CARD_W, _CARD_H = 56, 88

# Forza delle carte (per vincere la presa)
_RANK_PRESA = {"A": 10, "3": 9, "R": 8, "C": 7, "F": 6, "7": 5, "6": 4, "5": 3, "4": 2, "2": 1}
# Punti in partita
_PUNTI_CARTA = {"A": 11, "3": 10, "R": 4, "C": 3, "F": 2}

# Disposizione pip (carte 2–7) come nelle carte napoletane
_LAYOUT_PIP = {
    "2": [(28, 22), (28, 66)],
    "3": [(28, 16), (28, 44), (28, 72)],
    "4": [(16, 22), (40, 22), (16, 66), (40, 66)],
    "5": [(16, 22), (40, 22), (28, 44), (16, 66), (40, 66)],
    "6": [(16, 18), (16, 44), (16, 70), (40, 18), (40, 44), (40, 70)],
    "7": [(16, 18), (16, 44), (16, 70), (40, 18), (40, 44), (40, 70), (28, 44)],
}


def _crea_mazzo():
    return [f"{v}{s}" for s in SEMI for v in VALORI]


def _valore_carta(carta):
    return carta[:-1]


def _seme_carta(carta):
    return carta[-1]


def _rank_label(valore):
    return {"F": "Fante", "C": "Cavallo", "R": "Re", "A": "Asso"}.get(valore, valore)


def _nome_seme(codice):
    return _SEMI_INFO.get(codice, {}).get("nome", codice)


def _colore_seme(codice):
    return _SEMI_INFO.get(codice, {}).get("colore", "#1a1a2e")


def _nome_carta(carta):
    return f"{_rank_label(_valore_carta(carta))} di {_nome_seme(_seme_carta(carta))}"


def _nap_pip_denaro(scale=1.0):
    s = scale
    return (
        f'<circle cx="0" cy="0" r="{9*s}" fill="#f5c842" stroke="#1a1a1a" stroke-width="{1.1*s}"/>'
        f'<circle cx="0" cy="0" r="{5.5*s}" fill="#e8a800" stroke="#1a1a1a" stroke-width="{0.7*s}"/>'
        f'<path d="M{-3*s},{-1*s} Q0,{-4*s} {3*s},{-1*s} Q0,{2*s} {-3*s},{-1*s}" fill="#1a1a1a"/>'
        f'<circle cx="{-2*s}" cy="{-2*s}" r="{0.9*s}" fill="#1a1a1a"/>'
        f'<circle cx="{2*s}" cy="{-2*s}" r="{0.9*s}" fill="#1a1a1a"/>'
    )


def _nap_pip_coppa(scale=1.0):
    s = scale
    return (
        f'<path d="M{-8*s},{4*s} Q{-8*s},{-8*s} 0,{-10*s} Q{8*s},{-8*s} {8*s},{4*s} Z" '
        f'fill="#dc2626" stroke="#1a1a1a" stroke-width="{1.1*s}"/>'
        f'<rect x="{-3*s}" y="{4*s}" width="{6*s}" height="{4*s}" fill="#d4af37" stroke="#1a1a1a" stroke-width="{0.7*s}"/>'
        f'<rect x="{-5*s}" y="{8*s}" width="{10*s}" height="{2*s}" fill="#d4af37" stroke="#1a1a1a" stroke-width="{0.7*s}"/>'
    )


def _nap_pip_bastone(scale=1.0):
    s = scale
    return (
        f'<rect x="{-2.5*s}" y="{-12*s}" width="{5*s}" height="{22*s}" rx="{1.5*s}" fill="#2d7a3a" stroke="#1a1a1a" stroke-width="{1*s}"/>'
        f'<circle cx="0" cy="{-13*s}" r="{4*s}" fill="#c41e3a" stroke="#1a1a1a" stroke-width="{0.8*s}"/>'
        f'<circle cx="0" cy="{-13*s}" r="{2*s}" fill="#f5c842"/>'
        f'<path d="M{-2*s},{-6*s} Q0,{-2*s} {2*s},{-6*s}" fill="none" stroke="#f5c842" stroke-width="{1*s}"/>'
    )


def _nap_pip_spada(scale=1.0, curved=False):
    s = scale
    if curved:
        return (
            f'<path d="M{-2*s},{10*s} Q{12*s},{-6*s} {2*s},{-14*s} L{4*s},{-12*s} Q{14*s},{-4*s} 0,{12*s} Z" '
            f'fill="#2563eb" stroke="#1a1a1a" stroke-width="{1*s}"/>'
            f'<path d="M{-6*s},{8*s} Q{-2*s},{4*s} {2*s},{8*s}" fill="none" stroke="#c41e3a" stroke-width="{1.2*s}"/>'
            f'<rect x="{-4*s}" y="{10*s}" width="{8*s}" height="{3*s}" fill="#d4af37" stroke="#1a1a1a" stroke-width="{0.7*s}"/>'
        )
    return (
        f'<rect x="{-1.5*s}" y="{-14*s}" width="{3*s}" height="{22*s}" fill="#2563eb" stroke="#1a1a1a" stroke-width="{0.8*s}"/>'
        f'<rect x="{-5*s}" y="{6*s}" width="{10*s}" height="{2.5*s}" fill="#d4af37" stroke="#1a1a1a" stroke-width="{0.7*s}"/>'
        f'<circle cx="0" cy="{6*s}" r="{2*s}" fill="#d4af37" stroke="#1a1a1a" stroke-width="{0.6*s}"/>'
    )


def _nap_pip_gruppo(seme, x, y, scale=1.0, curved=False):
    inner = {
        "O": _nap_pip_denaro(scale),
        "P": _nap_pip_coppa(scale),
        "B": _nap_pip_bastone(scale),
        "S": _nap_pip_spada(scale, curved=curved),
    }[seme]
    return f'<g transform="translate({x},{y})">{inner}</g>'


def _nap_asso(seme):
    if seme == "O":
        return (
            '<g transform="translate(28,46)">'
            '<circle cx="0" cy="0" r="22" fill="#f5c842" stroke="#1a1a1a" stroke-width="1.5"/>'
            '<circle cx="0" cy="0" r="14" fill="#e8a800" stroke="#1a1a1a" stroke-width="1"/>'
            '<path d="M-8,-2 Q0,-10 8,-2 Q0,6 -8,-2" fill="#1a1a1a"/>'
            '<path d="M-12,-14 L12,-14 L10,-18 L-10,-18 Z" fill="#c41e3a" stroke="#1a1a1a" stroke-width="0.8"/>'
            '<path d="M-6,-20 L0,-28 L6,-20 Z" fill="#1a1a1a"/>'
            '<path d="M-18,8 Q0,18 18,8" fill="none" stroke="#c41e3a" stroke-width="2"/>'
            "</g>"
        )
    if seme == "P":
        return (
            '<g transform="translate(28,48)">'
            '<path d="M-18,10 Q-18,-16 0,-20 Q18,-16 18,10 Z" fill="#dc2626" stroke="#1a1a1a" stroke-width="1.5"/>'
            '<ellipse cx="0" cy="2" rx="10" ry="6" fill="#b91c1c"/>'
            '<rect x="-6" y="10" width="12" height="8" fill="#d4af37" stroke="#1a1a1a" stroke-width="1"/>'
            '<rect x="-10" y="18" width="20" height="4" fill="#d4af37" stroke="#1a1a1a" stroke-width="1"/>'
            "</g>"
        )
    if seme == "B":
        return (
            '<g transform="translate(28,46)">'
            '<rect x="-5" y="-24" width="10" height="44" rx="2" fill="#2d7a3a" stroke="#1a1a1a" stroke-width="1.5"/>'
            '<circle cx="0" cy="-26" r="9" fill="#c41e3a" stroke="#1a1a1a" stroke-width="1.2"/>'
            '<circle cx="0" cy="-26" r="5" fill="#f5c842"/>'
            '<path d="M-4,-12 Q0,-4 4,-12 M-4,0 Q0,8 4,0 M-4,12 Q0,20 4,12" fill="none" stroke="#f5c842" stroke-width="1.5"/>'
            "</g>"
        )
    return (
        '<g transform="translate(28,46)">'
        + _nap_pip_spada(2.2, curved=True)
        + "</g>"
    )


def _nap_simbolo_in_mano(seme, hx, hy, scale=0.55):
    return _nap_pip_gruppo(seme, hx, hy, scale=scale, curved=(seme == "S"))


def _nap_fante(seme):
    sym = _nap_simbolo_in_mano(seme, 36, 52, 0.5)
    return (
        '<g stroke="#1a1a1a" stroke-width="1">'
        '<circle cx="28" cy="18" r="7" fill="#f5d0a9"/>'
        '<path d="M18,26 L38,26 L36,58 L20,58 Z" fill="#2d7a3a"/>'
        '<path d="M20,58 L18,72 L24,72 L26,58 M32,58 L34,72 L28,72 L26,58" fill="#c41e3a"/>'
        '<rect x="22" y="28" width="12" height="14" fill="#f5c842" stroke="#1a1a1a" stroke-width="0.8"/>'
        f"{sym}"
        "</g>"
    )


def _nap_cavallo(seme):
    sym = _nap_simbolo_in_mano(seme, 38, 28, 0.45)
    return (
        '<g stroke="#1a1a1a" stroke-width="1">'
        '<ellipse cx="32" cy="58" rx="16" ry="8" fill="#8b4513"/>'
        '<path d="M14,58 L20,38 L28,34 L36,38 L42,58 Z" fill="#a0522d"/>'
        '<path d="M28,34 L26,24 L32,20 L36,28 Z" fill="#8b4513"/>'
        '<circle cx="22" cy="30" r="5" fill="#f5d0a9"/>'
        '<path d="M18,36 L16,52 L22,52 L24,38 Z" fill="#2d7a3a"/>'
        '<path d="M22,52 L20,66 L26,66 L26,52" fill="#c41e3a"/>'
        f"{sym}"
        "</g>"
    )


def _nap_re(seme):
    sym = _nap_simbolo_in_mano(seme, 36, 54, 0.5)
    return (
        '<g stroke="#1a1a1a" stroke-width="1">'
        '<path d="M16,14 L40,14 L38,20 L18,20 Z" fill="#d4af37"/>'
        '<circle cx="28" cy="22" r="8" fill="#f5d0a9"/>'
        '<path d="M22,22 Q28,28 34,22" fill="none" stroke="#1a1a1a" stroke-width="0.8"/>'
        '<path d="M16,30 L40,30 L38,58 L18,58 Z" fill="#1d4ed8"/>'
        '<path d="M14,32 L12,58 L18,58 L20,32 Z" fill="#c41e3a"/>'
        '<path d="M42,32 L44,58 L38,58 L36,32 Z" fill="#c41e3a"/>'
        f"{sym}"
        "</g>"
    )


def _nap_numerata(seme, valore):
    pips = []
    scale = 0.85 if valore in {"6", "7"} else 1.0
    for x, y in _LAYOUT_PIP[valore]:
        pips.append(_nap_pip_gruppo(seme, x, y, scale=scale))
    extra = ""
    if valore == "4" and seme == "O":
        extra = (
            '<rect x="22" y="38" width="12" height="14" rx="1" fill="#c41e3a" '
            'stroke="#1a1a1a" stroke-width="0.8" transform="rotate(45 28 45)"/>'
        )
    if valore == "3" and seme == "B":
        extra = (
            '<circle cx="28" cy="44" r="5" fill="#f5d0a9" stroke="#1a1a1a" stroke-width="0.8"/>'
        )
    return "".join(pips) + extra


def _svg_carta_napoletana(valore, seme):
    if valore == "A":
        contenuto = _nap_asso(seme)
    elif valore == "F":
        contenuto = _nap_fante(seme)
    elif valore == "C":
        contenuto = _nap_cavallo(seme)
    elif valore == "R":
        contenuto = _nap_re(seme)
    else:
        contenuto = _nap_numerata(seme, valore)

    return (
        f'<svg class="br-nap-svg" viewBox="0 0 {_CARD_W} {_CARD_H}" '
        f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        f'<rect x="1" y="1" width="{_CARD_W - 2}" height="{_CARD_H - 2}" '
        f'rx="3" fill="#fffef8" stroke="#1a1a1a" stroke-width="1.2"/>'
        f"{contenuto}</svg>"
    )


def _punti_carta(carta):
    return _PUNTI_CARTA.get(_valore_carta(carta), 0)


def _rank_presa(carta):
    return _RANK_PRESA.get(_valore_carta(carta), 0)


def _is_briscola(carta, seme_briscola):
    return _seme_carta(carta) == seme_briscola


def _vince_presa(carta_lead, carta_follow, seme_briscola):
    """Restituisce 'lead' o 'follow'."""
    br_lead = _is_briscola(carta_lead, seme_briscola)
    br_follow = _is_briscola(carta_follow, seme_briscola)
    if br_lead and not br_follow:
        return "lead"
    if br_follow and not br_lead:
        return "follow"
    if br_lead and br_follow:
        return "lead" if _rank_presa(carta_lead) >= _rank_presa(carta_follow) else "follow"
    return "lead"


def _punti_trick(carta1, carta2):
    return _punti_carta(carta1) + _punti_carta(carta2)


def _css_tavolo():
    return """
    <style>
    .br-table {
        background: linear-gradient(145deg, #0d5c2e 0%, #1a7a3e 50%, #0d5c2e 100%);
        border: 4px solid #8b6914; border-radius: 16px;
        padding: 1rem; margin: 0.5rem 0;
        box-shadow: inset 0 0 30px rgba(0,0,0,0.3);
    }
    .br-label { color: #f5e6c8; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.3rem; }
    .br-msg { color: #f5e6c8; font-style: italic; text-align: center; font-size: 0.85rem; margin: 0.3rem 0; }
    .br-hand { display: flex; gap: 6px; flex-wrap: wrap; min-height: 70px; align-items: flex-start; }
    .br-trick {
        display: flex; gap: 16px; justify-content: center; align-items: center;
        min-height: 90px; padding: 0.5rem 0;
    }
    .br-card {
        width: 64px; height: 100px; border-radius: 6px;
        background: #fffef8; border: 2px solid #1a1a1a;
        box-shadow: 2px 4px 8px rgba(0,0,0,0.35);
        overflow: hidden; flex-shrink: 0;
        display: inline-flex; align-items: stretch; justify-content: stretch;
    }
    .br-card.briscola-highlight {
        border-color: #d4af37; box-shadow: 0 0 14px rgba(212,175,55,0.85);
        outline: 2px solid #ffd700;
    }
    .br-nap-svg { width: 100%; height: 100%; display: block; }
    .br-card.back {
        background: #8b0000; border-color: #d4af37;
        justify-content: center; align-items: center; padding: 4px;
    }
    .br-card-back-pattern {
        width: 100%; height: 100%; border: 2px solid #ffd700; border-radius: 4px;
        background:
            repeating-linear-gradient(45deg, #c41e3a 0 6px, #8b0000 6px 12px),
            radial-gradient(circle at 50% 50%, #ffd700 0%, transparent 55%);
        box-shadow: inset 0 0 12px rgba(0,0,0,0.35);
    }
    @media (max-width: 768px) {
        .br-table { padding: 0.65rem; margin: 0.35rem 0; border-width: 3px; border-radius: 12px; }
        .br-card { width: 52px; height: 82px; }
        .br-hand { gap: 4px; min-height: 60px; }
        .br-trick { gap: 10px; min-height: 76px; }
        .br-label, .br-msg { font-size: 0.8rem; }
    }
    @media (min-width: 769px) {
        .br-card { width: 64px; height: 100px; }
    }
    .br-briscola-box {
        text-align: center; margin: 0.5rem 0;
        padding: 0.4rem; background: rgba(212,175,55,0.15);
        border-radius: 8px; border: 1px dashed #d4af37;
    }
    .br-briscola-label { color: #d4af37; font-size: 0.8rem; font-weight: 700; }
    </style>
    """


def _html_tabella_punteggi():
    righe = (
        ("Asso", 11),
        ("Tre", 10),
        ("Re", 4),
        ("Cavallo", 3),
        ("Fante", 2),
        ("2 · 4 · 5 · 6 · 7", 0),
    )
    corpo = "".join(
        f'<tr><td>{nome}</td><td class="br-score-pts{"" if pt else " zero"}">{pt}</td></tr>'
        for nome, pt in righe
    )
    return (
        '<div class="br-score-wrap">'
        + '<div class="br-score-title">Regole e punteggio Briscola</div>'
        + '<table class="br-score-table">'
        + "<thead><tr><th>Carta</th><th style=\"text-align:center\">Punti</th></tr></thead>"
        + f"<tbody>{corpo}</tbody>"
        + "</table>"
        + '<div class="br-score-note">'
        + f"<strong>Obiettivo:</strong> superare {PUNTI_VITTORIA} punti su 120. "
        + "1 vs 1: giochi una carta per turno; vince la presa la carta più forte. "
        + "La <strong>briscola</strong> (seme in alto) batte gli altri semi; "
        + "fuori briscola vince il seme uscito per primo. "
        + "Ultima presa: punti anche della briscola scoperta."
        + "</div></div>"
    )


def _render_guida_punteggi():
    render_guida_expander(_html_tabella_punteggi())


def _html_carta(carta, highlight=False, piccola=False):
    valore = _valore_carta(carta)
    seme = _seme_carta(carta)
    cls = "br-card"
    if highlight:
        cls += " briscola-highlight"
    style = ' style="width:52px;height:82px"' if piccola else ""
    return (
        f'<div class="{cls}"{style} title="{_nome_carta(carta)}">'
        f"{_svg_carta_napoletana(valore, seme)}</div>"
    )


def _html_carta_dorso():
    return (
        '<div class="br-card back">'
        '<div class="br-card-back-pattern"></div>'
        "</div>"
    )


def _html_tavolo(stato):
    seme_br = stato["seme_briscola"]
    briscola = stato["briscola_carta"]
    trick = stato.get("trick") or {}
    lead = trick.get("lead")
    follow = trick.get("follow")

    trick_html = ""
    if lead or follow:
        pezzi = []
        if lead:
            pezzi.append(_html_carta(lead, _is_briscola(lead, seme_br)))
        if follow:
            pezzi.append(_html_carta(follow, _is_briscola(follow, seme_br)))
        trick_html = f'<div class="br-trick">{"".join(pezzi)}</div>'
    else:
        trick_html = '<div class="br-trick"><span style="color:#f5e6c8;font-size:0.85rem">Nessuna carta in tavola</span></div>'

    mano_pc_html = "".join(_html_carta_dorso() for _ in stato["mano_computer"])
    if not mano_pc_html:
        mano_pc_html = '<span style="color:#888;font-size:0.8rem">Mano vuota</span>'

    return (
        _css_tavolo()
        + '<div class="br-table">'
        + f'<div class="br-msg">{stato.get("messaggio", "")}</div>'
        + '<div class="br-briscola-box">'
        + f'<div class="br-briscola-label">BRISCOLA — {_nome_seme(seme_br)}</div>'
        + _html_carta(briscola, highlight=True)
        + "</div>"
        + '<div class="br-label">🎩 Computer</div>'
        + f'<div class="br-hand">{mano_pc_html}</div>'
        + trick_html
        + '<div class="br-label">🃏 Tu</div>'
        + f'<div class="br-hand">{"".join(_html_carta(c, _is_briscola(c, seme_br)) for c in stato["mano_giocatore"])}</div>'
        + "</div>"
    )


def _deal(stato, n=3):
    for _ in range(n):
        if not stato["mazzo"]:
            break
        stato["mano_giocatore"].append(stato["mazzo"].pop())
        if not stato["mazzo"]:
            break
        stato["mano_computer"].append(stato["mazzo"].pop())


def _nuova_partita():
    mazzo = _crea_mazzo()
    random.shuffle(mazzo)
    briscola = mazzo.pop()
    stato = {
        "mazzo": mazzo,
        "mano_giocatore": [],
        "mano_computer": [],
        "briscola_carta": briscola,
        "seme_briscola": _seme_carta(briscola),
        "punti_giocatore": 0,
        "punti_computer": 0,
        "trick": {"lead": None, "follow": None, "leader": "giocatore"},
        "turno": "giocatore",
        "fase": "gioco",
        "messaggio": "Tu attacchi per primo. Scegli una carta.",
        "presa_num": 0,
        "ultimo_vincitore": None,
        "ultimo_trick_pts": 0,
        "partita_finita": False,
        "vincitore_partita": None,
    }
    _deal(stato, 3)
    return stato


def _ricontrolla_distribuzione(stato):
    if (
        not stato["mano_giocatore"]
        and not stato["mano_computer"]
        and stato["mazzo"]
        and stato["fase"] == "gioco"
    ):
        _deal(stato, 3)
        stato["messaggio"] = "Nuove carte distribuite."


def _assegna_presa(stato, vincitore_trick, punti):
    if vincitore_trick == "giocatore":
        stato["punti_giocatore"] += punti
    else:
        stato["punti_computer"] += punti
    stato["presa_num"] += 1
    stato["ultimo_vincitore"] = vincitore_trick
    stato["ultimo_trick_pts"] = punti


def _fine_partita(stato):
    # L'ultima presa include anche la carta briscola sul tavolo
    if stato["ultimo_vincitore"]:
        pts_br = _punti_carta(stato["briscola_carta"])
        if stato["ultimo_vincitore"] == "giocatore":
            stato["punti_giocatore"] += pts_br
        else:
            stato["punti_computer"] += pts_br
        stato["ultimo_trick_pts"] += pts_br

    pg, pc = stato["punti_giocatore"], stato["punti_computer"]
    if pg > pc:
        stato["vincitore_partita"] = "giocatore"
        stato["messaggio"] = f"Partita finita! Hai vinto {pg}–{pc}."
    elif pc > pg:
        stato["vincitore_partita"] = "computer"
        stato["messaggio"] = f"Partita finita! Hai perso {pg}–{pc}."
    else:
        stato["vincitore_partita"] = "pareggio"
        stato["messaggio"] = f"Partita finita in pareggio! {pg}–{pc}."
    stato["partita_finita"] = True
    stato["fase"] = "fine"


def _partita_terminata(stato):
    mani_vuote = not stato["mano_giocatore"] and not stato["mano_computer"]
    mazzo_vuoto = not stato["mazzo"]
    trick_vuoto = not stato["trick"].get("lead") and not stato["trick"].get("follow")
    return mani_vuote and mazzo_vuoto and trick_vuoto


def _chiudi_trick_solo(stato, vincitore, carta):
    """Presa vinta senza risposta (avversario senza carte)."""
    punti = _punti_carta(carta)
    _assegna_presa(stato, vincitore, punti)
    nome_v = "Tu" if vincitore == "giocatore" else "Computer"
    stato["messaggio"] = f"Presa a {nome_v} (+{punti} pt) — {_nome_carta(carta)}"
    stato["trick"] = {"lead": None, "follow": None, "leader": vincitore}
    stato["turno"] = vincitore
    _ricontrolla_distribuzione(stato)
    if _partita_terminata(stato):
        _fine_partita(stato)


def _assicura_turno_valido(stato):
    """Evita blocchi con mani disallineate a fine mazzo."""
    if stato["partita_finita"]:
        return

    _ricontrolla_distribuzione(stato)
    if _partita_terminata(stato):
        _fine_partita(stato)
        return

    trick = stato["trick"]
    if trick.get("lead") and trick.get("follow") is None:
        leader = trick["leader"]
        avversario = "computer" if leader == "giocatore" else "giocatore"
        mano_avv = stato["mano_computer"] if avversario == "computer" else stato["mano_giocatore"]
        if not mano_avv and not stato["mazzo"]:
            _chiudi_trick_solo(stato, leader, trick["lead"])
            return

    if stato["turno"] == "giocatore" and not stato["mano_giocatore"] and stato["mano_computer"]:
        stato["turno"] = "computer"
    elif stato["turno"] == "computer" and not stato["mano_computer"] and stato["mano_giocatore"]:
        stato["turno"] = "giocatore"
    elif not stato["mano_giocatore"] and not stato["mano_computer"] and not stato["mazzo"]:
        if _partita_terminata(stato):
            _fine_partita(stato)


def _chiudi_trick(stato):
    trick = stato["trick"]
    lead, follow = trick["lead"], trick["follow"]
    seme_br = stato["seme_briscola"]
    risultato = _vince_presa(lead, follow, seme_br)
    vincitore = trick["leader"] if risultato == "lead" else (
        "computer" if trick["leader"] == "giocatore" else "giocatore"
    )
    punti = _punti_trick(lead, follow)
    _assegna_presa(stato, vincitore, punti)

    nome_v = "Tu" if vincitore == "giocatore" else "Computer"
    stato["messaggio"] = f"Presa a {nome_v} (+{punti} pt) — {_nome_carta(lead)} vs {_nome_carta(follow)}"
    stato["trick"] = {"lead": None, "follow": None, "leader": vincitore}
    stato["turno"] = vincitore

    _ricontrolla_distribuzione(stato)
    if _partita_terminata(stato):
        _fine_partita(stato)
    elif vincitore == "giocatore":
        stato["messaggio"] += " · A te la prossima carta."
    else:
        stato["messaggio"] += " · Il computer attacca."


def _gioca_carta(stato, chi, carta):
    trick = stato["trick"]
    if chi == "giocatore":
        stato["mano_giocatore"].remove(carta)
    else:
        stato["mano_computer"].remove(carta)

    if trick["lead"] is None:
        trick["lead"] = carta
        trick["leader"] = chi
        stato["turno"] = "computer" if chi == "giocatore" else "giocatore"
    else:
        trick["follow"] = carta
        _chiudi_trick(stato)


def _carta_migliore_per_vincere(carte, carta_avversario, seme_briscola, must_win):
    """Sceglie la carta migliore per vincere (o perdere con minimo danno)."""
    if not carte:
        return None

    if carta_avversario is None:
        # Attacco: gioca la carta non-briscola più bassa con meno punti
        non_br = [c for c in carte if not _is_briscola(c, seme_briscola)]
        pool = non_br if non_br else carte
        return min(pool, key=lambda c: (_punti_carta(c), _rank_presa(c)))

    # Difesa
    vincenti = []
    for c in carte:
        ruolo = "follow" if True else "lead"
        sim_lead = carta_avversario
        sim_follow = c
        v = _vince_presa(sim_lead, sim_follow, seme_briscola)
        if v == "follow":
            vincenti.append(c)

    punti_avv = _punti_carta(carta_avversario)
    if vincenti:
        if must_win or punti_avv >= 10:
            return min(vincenti, key=lambda c: (_rank_presa(c), _punti_carta(c)))
        # Lascia perdere se pochi punti in palio
        if punti_avv <= 2 and random.random() < 0.6:
            return min(carte, key=lambda c: (_punti_carta(c), _rank_presa(c)))
        return min(vincenti, key=lambda c: (_rank_presa(c), _punti_carta(c)))

    # Non può vincere: scarta la carta con meno valore
    return min(carte, key=lambda c: (_punti_carta(c), _rank_presa(c)))


def _mossa_computer(stato):
    _assicura_turno_valido(stato)
    if stato["partita_finita"]:
        return
    carte = stato["mano_computer"]
    if not carte:
        _assicura_turno_valido(stato)
        return
    trick = stato["trick"]
    seme_br = stato["seme_briscola"]
    carta_avv = trick["lead"] if trick["leader"] == "giocatore" else None
    must_win = _punti_carta(carta_avv) >= 10 if carta_avv else False
    carta = _carta_migliore_per_vincere(carte, carta_avv, seme_br, must_win)
    _gioca_carta(stato, "computer", carta)
    _assicura_turno_valido(stato)


def _carta_valida(carta):
    return (
        isinstance(carta, str)
        and len(carta) == 2
        and carta[0] in VALORI
        and carta[1] in _SEMI_INFO
    )


def _inizializza():
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = _nuova_partita()
        return
    stato = st.session_state[SESSION_KEY]
    carte_campione = [stato.get("briscola_carta"), *stato.get("mano_giocatore", []), *stato.get("mazzo", [])]
    if any(c and not _carta_valida(c) for c in carte_campione):
        st.session_state[SESSION_KEY] = _nuova_partita()


def render():
    """Interfaccia Streamlit per 'Briscola'."""
    _inizializza()
    stato = st.session_state[SESSION_KEY]

    st.subheader("Briscola")

    pg, pc = stato["punti_giocatore"], stato["punti_computer"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tu", pg, delta=f"{'▲' if pg >= PUNTI_VITTORIA else ''}")
    c2.metric("Computer", pc)
    c3.metric("Briscola", _nome_seme(stato["seme_briscola"]))
    c4.metric("Prese", stato["presa_num"])

    st.progress(min(pg / PUNTI_VITTORIA, 1.0), text=f"Obiettivo: {PUNTI_VITTORIA} pt")
    st.markdown(_html_tavolo(stato), unsafe_allow_html=True)

    if stato["partita_finita"]:
        v = stato["vincitore_partita"]
        if v == "giocatore":
            st.success(stato["messaggio"])
        elif v == "pareggio":
            st.warning(stato["messaggio"])
        else:
            st.error(stato["messaggio"])
        st.caption(
            f"Punti carta briscola ({_nome_carta(stato['briscola_carta'])}): "
            f"+{_punti_carta(stato['briscola_carta'])} all'ultima presa."
        )
        if st.button("Nuova partita", key="br_nuova", type="primary", use_container_width=True):
            st.session_state[SESSION_KEY] = _nuova_partita()
            st.rerun()
        _render_guida_punteggi()
        return

    # Turno computer: gioca automaticamente
    if stato["turno"] == "computer" and stato["fase"] == "gioco" and not stato["partita_finita"]:
        _mossa_computer(stato)
        st.rerun()

    # Turno giocatore
    if stato["turno"] == "giocatore" and stato["mano_giocatore"]:
        trick = stato["trick"]
        if trick["lead"] and trick["leader"] == "computer":
            st.caption(f"Il computer ha giocato: **{_nome_carta(trick['lead'])}** — rispondi con una carta.")
        else:
            st.caption("Scegli una carta da giocare (attacco).")

        carte = stato["mano_giocatore"]
        seme_br = stato["seme_briscola"]
        cols = st.columns(min(len(carte), 3))
        for i, carta in enumerate(carte):
            pts = _punti_carta(carta)
            br = _is_briscola(carta, seme_br)
            label = _nome_carta(carta)
            if pts:
                label += f" ({pts} pt)"
            if br:
                label += " ⭐"
            with cols[i % len(cols)]:
                if st.button(label, key=f"br_card_{i}_{carta}_{stato['presa_num']}", use_container_width=True):
                    _gioca_carta(stato, "giocatore", carta)
                    if stato["turno"] == "computer" and not stato["partita_finita"]:
                        _mossa_computer(stato)
                    _assicura_turno_valido(stato)
                    st.rerun()

    _render_guida_punteggi()
