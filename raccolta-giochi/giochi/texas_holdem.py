"""Gioco: Texas Hold'em — 1 vs 1 o tavolo da 5 giocatori."""

import random
from collections import Counter
from itertools import combinations

import streamlit as st

from giochi.guida_ui import render_guida_expander

SEMI = ["♠", "♥", "♦", "♣"]
VALORI = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SEMI_ROSSI = {"♥", "♦"}
SESSION_KEY = "texas_holdem"
HUMAN_IDX = 0

CHIPS_INIZIALI = 1000
SMALL_BLIND = 10
BIG_BLIND = 20
RAISE_STEP = 20

MODALITA_OPZIONI = ("1 vs 1", "Tavolo 5 giocatori")
DIFFICOLTA_OPZIONI = ("Facile", "Medio", "Difficile")
NOMI_CPU_TAVOLO = ("Marco", "Luca", "Sara", "Alex")

NOMI_MANO = {
    9: "Scala reale",
    8: "Scala colore",
    7: "Poker",
    6: "Full",
    5: "Colore",
    4: "Scala",
    3: "Tris",
    2: "Doppia coppia",
    1: "Coppia",
    0: "Carta alta",
}
RANK_LABEL = {
    14: "A", 13: "K", 12: "Q", 11: "J", 10: "10",
    9: "9", 8: "8", 7: "7", 6: "6", 5: "5", 4: "4", 3: "3", 2: "2",
}

# ── Mazzo e valutazione ────────────────────────────────────────────────────────

def _crea_mazzo():
    return [f"{v}{s}" for s in SEMI for v in VALORI]


def _rank_carta(carta):
    v = carta[:-1]
    speciali = {"J": 11, "Q": 12, "K": 13, "A": 14}
    return speciali[v] if v in speciali else int(v)


def _seme_carta(carta):
    return carta[-1]


def _valore_visivo(carta):
    return carta[:-1]


def _is_straight(ranks):
    unique = sorted(set(ranks), reverse=True)
    if len(unique) < 5:
        return 0
    for i in range(len(unique) - 4):
        if unique[i] - unique[i + 4] == 4:
            return unique[i]
    if {14, 5, 4, 3, 2}.issubset(set(ranks)):
        return 5
    return 0


def _valuta_cinque(carte):
    ranks = sorted([_rank_carta(c) for c in carte], reverse=True)
    suits = [_seme_carta(c) for c in carte]
    counts = Counter(ranks)
    by_freq = sorted(counts.items(), key=lambda x: (x[1], x[0]), reverse=True)
    is_flush = len(set(suits)) == 1
    sh = _is_straight(ranks)

    if sh and is_flush:
        if sh == 14 and all(r in ranks for r in (14, 13, 12, 11, 10)):
            return (9, sh)
        return (8, sh)
    if by_freq[0][1] == 4:
        return (7, by_freq[0][0], by_freq[1][0])
    if by_freq[0][1] == 3 and len(by_freq) > 1 and by_freq[1][1] >= 2:
        return (6, by_freq[0][0], by_freq[1][0])
    if is_flush:
        return (5, tuple(ranks))
    if sh:
        return (4, sh)
    if by_freq[0][1] == 3:
        kickers = sorted([r for r in ranks if r != by_freq[0][0]], reverse=True)
        return (3, by_freq[0][0], kickers[0], kickers[1])
    if by_freq[0][1] == 2 and len(by_freq) > 1 and by_freq[1][1] == 2:
        pairs = sorted([by_freq[0][0], by_freq[1][0]], reverse=True)
        kicker = next(r for r in ranks if r not in pairs)
        return (2, pairs[0], pairs[1], kicker)
    if by_freq[0][1] == 2:
        pair = by_freq[0][0]
        kickers = sorted([r for r in ranks if r != pair], reverse=True)
        return (1, pair, kickers[0], kickers[1], kickers[2])
    return (0, tuple(ranks))


def _miglior_mano(carte):
    if len(carte) < 5:
        return None
    best = None
    for cinque in combinations(carte, 5):
        score = _valuta_cinque(list(cinque))
        if best is None or score > best:
            best = score
    return best


def _nome_mano(score):
    return NOMI_MANO.get(score[0], "Carta alta")


def _label_rank(r):
    return RANK_LABEL.get(r, str(r))


def _descrizione_mano(score):
    cat = score[0]
    if cat == 0:
        high = score[1][0] if isinstance(score[1], tuple) else score[1]
        return f"Carta alta {_label_rank(high)}"
    if cat == 1:
        return f"Coppia di {_label_rank(score[1])}"
    if cat == 2:
        return f"Doppia coppia ({_label_rank(score[1])} e {_label_rank(score[2])})"
    if cat == 3:
        return f"Tris di {_label_rank(score[1])}"
    if cat == 4:
        return f"Scala al {_label_rank(score[1])}"
    if cat == 6:
        return f"Full ({_label_rank(score[1])} su {_label_rank(score[2])})"
    if cat == 7:
        return f"Poker di {_label_rank(score[1])}"
    return _nome_mano(score)


def _kicker_bonus(score):
    if len(score) <= 1:
        return 0.0
    valori = []
    for parte in score[1:]:
        if isinstance(parte, tuple):
            valori.extend(parte)
        else:
            valori.append(parte)
    return min(0.15, max(valori) / 140) if valori else 0.0


def _draw_bonus(hole, community):
    if len(community) >= 5:
        return 0.0
    carte = hole + community
    ranks = sorted(set(_rank_carta(c) for c in carte))
    suits = [_seme_carta(c) for c in carte]
    bonus = 0.0
    if Counter(suits).most_common(1)[0][1] >= 4:
        bonus += 0.10
    elif len(community) == 3 and Counter(suits).most_common(1)[0][1] >= 3:
        bonus += 0.04
    for i in range(len(ranks) - 3):
        span = ranks[i + 3] - ranks[i]
        if span <= 4:
            bonus += 0.08 if span == 4 else 0.05
            break
    if {14, 5, 4, 3, 2}.issubset(set(_rank_carta(c) for c in carte)):
        bonus = max(bonus, 0.05)
    return min(0.12, bonus)


def _forza_da_mano_valutata(score):
    cat = score[0]
    basi = {
        0: 0.20, 1: 0.40, 2: 0.56, 3: 0.66, 4: 0.74,
        5: 0.78, 6: 0.84, 7: 0.90, 8: 0.93, 9: 0.95,
    }
    base = basi.get(cat, 0.20)
    if cat == 0:
        high = score[1][0] if isinstance(score[1], tuple) else score[1]
        return min(0.38, base + max(0, high - 7) / 45)
    if cat == 1:
        return min(0.62, base + max(0, score[1] - 7) / 35)
    if cat == 2:
        top = max(score[1], score[2])
        return min(0.72, base + max(0, top - 7) / 50)
    if cat == 3:
        return min(0.80, base + max(0, score[1] - 7) / 40)
    return min(0.95, base + _kicker_bonus(score))


def _stima_forza(hole, community):
    if len(community) == 0:
        r1, r2 = sorted([_rank_carta(c) for c in hole], reverse=True)
        if r1 == r2:
            return min(0.95, 0.55 + r1 / 28)
        if r1 >= 13:
            return min(0.95, 0.45 + r1 / 30)
        return r1 / 20
    carte = hole + community
    if len(carte) < 5:
        return 0.5
    score = _miglior_mano(carte)
    if score is None:
        return 0.5
    forza = _forza_da_mano_valutata(score)
    if len(community) < 5:
        forza = min(0.95, forza + _draw_bonus(hole, community))
    return forza

# ── HTML del tavolo ────────────────────────────────────────────────────────────

def _css_tavolo(ring=False):
    ring_css = ""
    if ring:
        ring_css = """
    .th-ring-wrap { max-width: 560px; margin: 0 auto; }
    .th-ring {
        position: relative;
        width: 100%;
        aspect-ratio: 1 / 0.95;
        min-height: 340px;
        margin: 0.5rem 0 1rem;
    }
    .th-ring .th-center {
        position: absolute;
        left: 50%; top: 44%;
        transform: translate(-50%, -50%);
        z-index: 3;
        text-align: center;
        width: 72%;
        max-width: 280px;
    }
    .th-ring .th-center .th-pot {
        margin: 0 0 0.35rem;
        font-size: 1rem;
        background: rgba(0,0,0,0.25);
        border-radius: 8px;
        padding: 0.25rem 0.5rem;
        display: inline-block;
    }
    .th-ring .th-community {
        min-height: auto;
        padding: 0.25rem 0;
        gap: 4px;
    }
    .th-ring .th-community .th-card,
    .th-ring .th-seat .th-card {
        width: 36px; height: 50px;
        padding: 3px; border-radius: 5px;
        font-size: 0.65rem;
    }
    .th-ring .th-card-val-top, .th-ring .th-card-val-bot { font-size: 0.62rem; }
    .th-ring .th-card-suit-mid { font-size: 0.85rem; }
    .th-ring .th-card.back { font-size: 0.95rem; }
    .th-ring .th-seat {
        position: absolute;
        transform: translate(-50%, -50%);
        text-align: center;
        z-index: 2;
        width: 88px;
    }
    .th-ring .th-seat .th-label { font-size: 0.78rem; margin-bottom: 0.15rem; }
    .th-ring .th-seat .th-meta { font-size: 0.65rem; line-height: 1.2; margin-bottom: 0.15rem; }
    .th-ring .th-seat .th-hand {
        min-height: 50px;
        gap: 3px;
        justify-content: center;
    }
    .th-ring .th-seat.active {
        background: rgba(255,215,0,0.12);
        border-radius: 10px;
        padding: 0.2rem;
        box-shadow: 0 0 12px rgba(255,215,0,0.35);
    }
    .th-ring .th-seat.pos-0 { left: 50%;  top: 93%; }  /* Tu — basso centro */
    .th-ring .th-seat.pos-1 { left: 8%;   top: 82%; }  /* Marco — angolo basso sx */
    .th-ring .th-seat.pos-2 { left: 8%;   top: 10%; }  /* Luca — angolo alto sx */
    .th-ring .th-seat.pos-3 { left: 92%;  top: 10%; }  /* Sara — angolo alto dx */
    .th-ring .th-seat.pos-4 { left: 92%;  top: 82%; }  /* Alex — angolo basso dx */
    .th-dealer-btn {
        display: inline-block;
        background: #ffd700;
        color: #1a1a1a;
        font-size: 0.6rem;
        font-weight: 800;
        border-radius: 50%;
        width: 16px; height: 16px;
        line-height: 16px;
        margin-left: 2px;
        vertical-align: middle;
    }
    @media (max-width: 768px) {
        .th-ring-wrap { max-width: 100%; }
        .th-ring { min-height: 280px; aspect-ratio: 1 / 1.08; margin: 0.25rem 0 0.75rem; }
        .th-ring .th-seat { width: 72px; }
        .th-ring .th-seat .th-label { font-size: 0.68rem; }
        .th-ring .th-seat .th-meta { font-size: 0.58rem; }
        .th-ring .th-center { width: 78%; max-width: 240px; }
        .th-ring .th-center .th-pot { font-size: 0.85rem; }
        .th-ring .th-community .th-card,
        .th-ring .th-seat .th-card { width: 28px; height: 40px; padding: 2px; }
        .th-ring .th-card-val-top, .th-ring .th-card-val-bot { font-size: 0.55rem; }
        .th-ring .th-card-suit-mid { font-size: 0.72rem; }
        .th-ring .th-seat .th-hand { min-height: 40px; gap: 2px; }
        .th-ring .th-seat.pos-1 { left: 6%; top: 84%; }
        .th-ring .th-seat.pos-2 { left: 6%; top: 8%; }
        .th-ring .th-seat.pos-3 { left: 94%; top: 8%; }
        .th-ring .th-seat.pos-4 { left: 94%; top: 84%; }
    }
        """
    return f"""
    <style>
    .th-table {{
        background: linear-gradient(145deg, #0d5c2e 0%, #1a7a3e 50%, #0d5c2e 100%);
        border: 4px solid #8b6914; border-radius: 16px;
        padding: 1.25rem; margin: 0.75rem 0;
        box-shadow: inset 0 0 30px rgba(0,0,0,0.3);
    }}
    .th-table.th-table-ring {{
        background: radial-gradient(ellipse 85% 70% at 50% 45%, #1a8a45 0%, #0d5c2e 55%, #064020 100%);
        padding: 0.75rem 0.5rem 1rem;
    }}
    .th-zone {{ margin: 0.5rem 0; }}
    .th-label {{ color: #f5e6c8; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.35rem; }}
    .th-label.active {{ color: #ffd700; }}
    .th-meta {{ color: #c9b896; font-size: 0.75rem; margin-bottom: 0.25rem; }}
    .th-meta.folded {{ color: #888; text-decoration: line-through; }}
    .th-pot {{ color: #d4af37; font-size: 1.1rem; font-weight: 700; text-align: center; margin: 0.5rem 0; }}
    .th-hand {{ display: flex; gap: 8px; flex-wrap: wrap; min-height: 82px; align-items: flex-start; }}
    .th-card {{
        width: 58px; height: 82px; border-radius: 7px;
        background: #fffef8; border: 2px solid #ccc;
        box-shadow: 2px 4px 8px rgba(0,0,0,0.35);
        display: flex; flex-direction: column; justify-content: space-between;
        padding: 5px; font-weight: 700; line-height: 1;
    }}
    .th-card.red {{ color: #c0392b; }}
    .th-card.black {{ color: #1a1a2e; }}
    .th-card.back {{
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        border-color: #4a7ab0; color: #fff;
        justify-content: center; align-items: center; font-size: 1.4rem;
    }}
    .th-card-val-top {{ font-size: 0.9rem; }}
    .th-card-suit-mid {{ font-size: 1.2rem; text-align: center; flex: 1; display: flex; align-items: center; justify-content: center; }}
    .th-card-val-bot {{ font-size: 0.9rem; text-align: right; transform: rotate(180deg); }}
    .th-community {{ display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; min-height: 90px; padding: 0.5rem 0; }}
    .th-msg {{ color: #f5e6c8; font-style: italic; text-align: center; font-size: 0.85rem; margin-bottom: 0.25rem; }}
    .th-hand-hint {{
        color: #7ec8ff; font-size: 0.9rem; font-weight: 600; text-align: center;
        margin: 0.35rem 0 0.5rem; padding: 0.35rem 0.75rem;
        background: rgba(0,40,80,0.4); border-radius: 8px;
        border: 1px solid rgba(126,200,255,0.4);
    }}
    {ring_css}
    @media (max-width: 768px) {{
        .th-table {{ padding: 0.75rem; margin: 0.35rem 0; border-width: 3px; }}
        .th-card {{ width: 44px; height: 64px; padding: 3px; }}
        .th-card-val-top, .th-card-val-bot {{ font-size: 0.72rem; }}
        .th-card-suit-mid {{ font-size: 0.95rem; }}
        .th-hand {{ min-height: 68px; gap: 4px; }}
        .th-msg, .th-hand-hint {{ font-size: 0.8rem; }}
        .th-pot {{ font-size: 0.95rem; }}
    }}
    </style>
    """


def _html_carta(carta, nascosta=False):
    if nascosta:
        return '<div class="th-card back">🂠</div>'
    seme = _seme_carta(carta)
    valore = _valore_visivo(carta)
    colore = "red" if seme in SEMI_ROSSI else "black"
    return (
        f'<div class="th-card {colore}">'
        f'<div class="th-card-val-top">{valore}{seme}</div>'
        f'<div class="th-card-suit-mid">{seme}</div>'
        f'<div class="th-card-val-bot">{valore}{seme}</div>'
        f"</div>"
    )


def _html_mano(carte, nascoste=None, mostra_min=2):
    nascoste = nascoste or set()
    pezzi = [_html_carta(c, nascosta=i in nascoste) for i, c in enumerate(carte)]
    placeholder = '<div class="th-card back" style="opacity:0.3;border-style:dashed">?</div>'
    while len(pezzi) < mostra_min:
        pezzi.append(placeholder)
    return f'<div class="th-hand">{"".join(pezzi)}</div>'


def _html_community(carte, compatto=False):
    if not carte:
        txt = "Flop · Turn · River" if compatto else "Carte comuni (flop, turn, river)"
        return f'<div class="th-community"><span style="color:#f5e6c8;font-size:0.75rem">{txt}</span></div>'
    pezzi = [_html_carta(c) for c in carte]
    while len(pezzi) < 5:
        pezzi.append('<div class="th-card" style="opacity:0.2;border-style:dashed;background:transparent"></div>')
    return f'<div class="th-community">{"".join(pezzi)}</div>'


def _info_mano_umano(mano):
    if len(mano["community"]) < 3:
        return None
    score = _miglior_mano(mano["holes"][HUMAN_IDX] + mano["community"])
    if score is None:
        return None
    return _descrizione_mano(score)


def _posizione_sede(idx, n_players):
    """Tu (0) in basso al centro; i 4 CPU agli angoli del tavolo."""
    if n_players <= 2:
        return idx
    # 0=Tu, 1=Marco(basso sx), 2=Luca(alto sx), 3=Sara(alto dx), 4=Alex(basso dx)
    return idx


def _html_giocatore(stato, mano, idx, sede=False):
    nome = stato["players"][idx]["nome"]
    chips = stato["players"][idx]["chips"]
    attivo = idx == mano["turno_idx"] and not mano["hand_over"]
    cls_label = "th-label active" if attivo else "th-label"
    meta_cls = "th-meta folded" if mano["folded"][idx] else "th-meta"
    extra = []
    if mano["folded"][idx]:
        extra.append("Fold")
    elif mano["all_in"][idx]:
        extra.append("All-in")
    if mano["street_bets"][idx] > 0:
        extra.append(f"Bet {mano['street_bets'][idx]}")
    extra_txt = " · ".join(extra)
    dealer = '<span class="th-dealer-btn">D</span>' if idx == mano["dealer_idx"] else ""
    meta_line = f"{chips}"
    if extra_txt:
        meta_line += f" · {extra_txt}"

    rivela = mano["hand_over"] or mano["fase"] in ("showdown", "fine")
    if idx == HUMAN_IDX or (rivela and not mano["folded"][idx]):
        hole_html = _html_mano(mano["holes"][idx])
    else:
        hole_html = _html_mano(mano["holes"][idx], nascoste={0, 1})

    icon = "🃏" if idx == HUMAN_IDX else "🎩"
    if sede:
        seat_cls = f"th-seat pos-{_posizione_sede(idx, mano['n_players'])}"
        if attivo:
            seat_cls += " active"
        return (
            f'<div class="{seat_cls}">'
            f'<div class="{cls_label}">{icon} {nome}{dealer}</div>'
            f'<div class="{meta_cls}">{meta_line}</div>'
            f"{hole_html}</div>"
        )

    return (
        f'<div class="th-zone">'
        f'<div class="{cls_label}">{icon} {nome}{dealer}</div>'
        f'<div class="{meta_cls}">{meta_line}</div>'
        f"{hole_html}</div>"
    )


def _html_tavolo(stato, mano):
    fase_label = {
        "preflop": "Pre-flop", "flop": "Flop", "turn": "Turn",
        "river": "River", "showdown": "Showdown", "fine": "Fine mano",
    }.get(mano["fase"], mano["fase"])
    info = _info_mano_umano(mano)
    hint = f'<div class="th-hand-hint">🃏 La tua mano: {info}</div>' if info and not mano["hand_over"] else ""
    n = mano["n_players"]

    if n > 2:
        sedi = "".join(_html_giocatore(stato, mano, i, sede=True) for i in range(n))
        centro = (
            f'<div class="th-center">'
            f'<div class="th-pot">🪙 {mano["pot"]}</div>'
            f'{_html_community(mano["community"], compatto=True)}'
            f"</div>"
        )
        return (
            _css_tavolo(ring=True)
            + '<div class="th-table th-table-ring">'
            + f'<div class="th-msg">{fase_label} · {mano.get("messaggio", "")}</div>'
            + hint
            + '<div class="th-ring-wrap"><div class="th-ring">'
            + centro
            + sedi
            + "</div></div></div>"
        )

    avversario = _html_giocatore(stato, mano, 1)
    umano = _html_giocatore(stato, mano, HUMAN_IDX)
    return (
        _css_tavolo(ring=False)
        + '<div class="th-table">'
        + f'<div class="th-msg">{fase_label} · {mano.get("messaggio", "")}</div>'
        + f'<div class="th-pot">🪙 Piatto: {mano["pot"]}</div>'
        + hint
        + avversario
        + _html_community(mano["community"])
        + umano
        + "</div>"
    )

# ── Logica di gioco (N giocatori) ──────────────────────────────────────────────

def _crea_giocatori(modalita):
    if modalita == "1 vs 1":
        return [
            {"nome": "Tu", "umano": True, "chips": CHIPS_INIZIALI},
            {"nome": "Computer", "umano": False, "chips": CHIPS_INIZIALI},
        ]
    return [{"nome": "Tu", "umano": True, "chips": CHIPS_INIZIALI}] + [
        {"nome": n, "umano": False, "chips": CHIPS_INIZIALI} for n in NOMI_CPU_TAVOLO
    ]


def _giocatori_in_mano(stato):
    return [i for i, p in enumerate(stato["players"]) if p["chips"] > 0]


def _ordine_attivi(mano):
    """Giocatori attivi in ordine partendo dal dealer."""
    attivi = [i for i in range(mano["n_players"]) if not mano["folded"][i]]
    if not attivi:
        return []
    if mano["dealer_idx"] in attivi:
        pos = attivi.index(mano["dealer_idx"])
        return attivi[pos:] + attivi[:pos]
    return attivi


def _sb_idx(mano):
    ordine = _ordine_attivi(mano)
    if len(ordine) <= 1:
        return ordine[0]
    return ordine[0] if len(ordine) == 2 else ordine[1]


def _bb_idx(mano):
    ordine = _ordine_attivi(mano)
    if len(ordine) == 1:
        return ordine[0]
    return ordine[1] if len(ordine) == 2 else ordine[2]


def _primo_preflop(mano):
    ordine = _ordine_attivi(mano)
    if len(ordine) == 2:
        return ordine[0]
    return ordine[3 % len(ordine)]


def _primo_postflop(mano):
    ordine = _ordine_attivi(mano)
    if len(ordine) == 2:
        return ordine[0]
    return ordine[1]


def _in_mano(mano):
    return [i for i in range(mano["n_players"]) if not mano["folded"][i]]


def _puo_agire(stato, mano, idx):
    if mano["folded"][idx] or mano["all_in"][idx]:
        return False
    return stato["players"][idx]["chips"] > 0


def _prossimo_attivo(mano, da_idx):
    n = mano["n_players"]
    idx = da_idx
    for _ in range(n):
        idx = (idx + 1) % n
        if not mano["folded"][idx] and not mano["all_in"][idx]:
            return idx
    return da_idx


def _to_call(mano, idx):
    return max(0, mano["level"] - mano["street_bets"][idx])


def _max_raise_extra(stato, mano, idx=HUMAN_IDX):
    chips = stato["players"][idx]["chips"]
    to_call = _to_call(mano, idx)
    return max(0, chips - to_call)


def _applica_puntata(stato, mano, idx, importo):
    effettivo = min(importo, stato["players"][idx]["chips"])
    stato["players"][idx]["chips"] -= effettivo
    mano["street_bets"][idx] += effettivo
    mano["pot"] += effettivo
    if stato["players"][idx]["chips"] == 0 and effettivo > 0:
        mano["all_in"][idx] = True
    return effettivo


def _puntate_pareggiate(mano):
    attivi = _in_mano(mano)
    if len(attivi) <= 1:
        return True
    target = max(mano["street_bets"][i] for i in attivi)
    for i in attivi:
        if not mano["all_in"][i] and mano["street_bets"][i] < target:
            return False
    return True


def _street_completa(stato, mano):
    if not _puntate_pareggiate(mano):
        return False
    for i in range(mano["n_players"]):
        if _puo_agire(stato, mano, i) and not mano["acted"][i]:
            return False
    return True


def _conta_in_mano(mano):
    return len(_in_mano(mano))


def _vincitore_unico_fold(mano):
    attivi = _in_mano(mano)
    return attivi[0] if len(attivi) == 1 else None


def _assegna_piatto(stato, mano, vincitori, messaggio):
    pot = mano["pot"]
    quota = pot // len(vincitori)
    resto = pot - quota * len(vincitori)
    nomi = []
    for j, w in enumerate(vincitori):
        stato["players"][w]["chips"] += quota + (1 if j < resto else 0)
        nomi.append(stato["players"][w]["nome"])
    mano["result"] = messaggio.format(pot=pot, nomi=", ".join(nomi))
    mano["hand_over"] = True
    mano["fase"] = "fine"


def _fine_mano_fold(stato, mano, vincitore_idx):
    nome = stato["players"][vincitore_idx]["nome"]
    if vincitore_idx == HUMAN_IDX:
        msg = "Tutti hanno foldato! Vinci il piatto ({pot} fiches)."
    elif mano["folded"][HUMAN_IDX]:
        msg = f"Hai foldato. {nome} vince il piatto ({{pot}} fiches)."
    else:
        msg = f"{nome} vince il piatto ({{pot}} fiches) — gli altri hanno foldato."
    _assegna_piatto(stato, mano, [vincitore_idx], msg)


def _showdown(stato, mano):
    attivi = _in_mano(mano)
    valutazioni = []
    for i in attivi:
        score = _miglior_mano(mano["holes"][i] + mano["community"])
        if score is None:
            mano["result"] = "Errore nella valutazione delle mani."
            mano["hand_over"] = True
            mano["fase"] = "fine"
            return
        valutazioni.append((i, score, _nome_mano(score)))
    best_score = max(v[1] for v in valutazioni)
    vincitori = [v[0] for v in valutazioni if v[1] == best_score]
    mano["showdown_info"] = {i: nome for i, _, nome in valutazioni}
    dettagli = " · ".join(
        f"{stato['players'][i]['nome']}: {nome}" for i, _, nome in valutazioni
    )
    if len(vincitori) == 1:
        w = vincitori[0]
        nome = stato["players"][w]["nome"]
        if w == HUMAN_IDX:
            msg = f"Hai vinto il piatto ({{pot}})! La tua mano: {mano['showdown_info'][w]}."
        else:
            msg = f"Hai perso ({{pot}}). Vincitore: {nome} ({mano['showdown_info'][w]})."
    else:
        msg = f"Piatto diviso ({{pot}}) tra {{nomi}}. Mani: {dettagli}."
    _assegna_piatto(stato, mano, vincitori, msg)


def _avanza_fase(stato, mano):
    n = mano["n_players"]
    mano["street_bets"] = [0] * n
    mano["level"] = 0
    mano["acted"] = [False] * n
    fase = mano["fase"]
    if fase == "preflop":
        mano["community"].extend([mano["mazzo"].pop() for _ in range(3)])
        mano["fase"] = "flop"
        mano["turno_idx"] = _primo_postflop(mano)
        mano["messaggio"] = "Flop: 3 carte comuni."
    elif fase == "flop":
        mano["community"].append(mano["mazzo"].pop())
        mano["fase"] = "turn"
        mano["turno_idx"] = _primo_postflop(mano)
        mano["messaggio"] = "Turn: 4ª carta comune."
    elif fase == "turn":
        mano["community"].append(mano["mazzo"].pop())
        mano["fase"] = "river"
        mano["turno_idx"] = _primo_postflop(mano)
        mano["messaggio"] = "River: 5ª carta comune."
    elif fase == "river":
        mano["fase"] = "showdown"
        _showdown(stato, mano)


def _auto_runout(stato, mano):
    mano["messaggio"] = "All-in! Carte sul tavolo..."
    while mano["fase"] not in ("showdown", "fine") and not mano["hand_over"]:
        fase = mano["fase"]
        if fase == "preflop":
            mano["community"].extend([mano["mazzo"].pop() for _ in range(3)])
            mano["fase"] = "flop"
        elif fase == "flop":
            mano["community"].append(mano["mazzo"].pop())
            mano["fase"] = "turn"
        elif fase == "turn":
            mano["community"].append(mano["mazzo"].pop())
            mano["fase"] = "river"
        elif fase == "river":
            mano["fase"] = "showdown"
            _showdown(stato, mano)
            return
    if mano["fase"] == "showdown" and not mano["hand_over"]:
        _showdown(stato, mano)


def _serve_runout(stato, mano):
    if mano["hand_over"] or not _puntate_pareggiate(mano):
        return False
    return any(stato["players"][i]["chips"] == 0 for i in _in_mano(mano))


def _dopo_azione(stato, mano):
    if mano["hand_over"]:
        return
    vinc = _vincitore_unico_fold(mano)
    if vinc is not None:
        _fine_mano_fold(stato, mano, vinc)
        return
    if _serve_runout(stato, mano):
        _auto_runout(stato, mano)
    elif _street_completa(stato, mano):
        _avanza_fase(stato, mano)
        if _serve_runout(stato, mano) and not mano["hand_over"]:
            _auto_runout(stato, mano)
    else:
        mano["turno_idx"] = _prossimo_attivo(mano, mano["turno_idx"])


def _applica_azione(stato, mano, idx, azione, raise_extra=None):
    if mano["hand_over"]:
        return

    if azione == "fold":
        mano["folded"][idx] = True
        vinc = _vincitore_unico_fold(mano)
        if vinc is not None:
            _fine_mano_fold(stato, mano, vinc)
        else:
            mano["turno_idx"] = _prossimo_attivo(mano, idx)
        return

    if azione == "check":
        mano["acted"][idx] = True
    elif azione == "call":
        _applica_puntata(stato, mano, idx, _to_call(mano, idx))
        mano["acted"][idx] = True
    elif azione == "raise":
        extra = max(raise_extra or RAISE_STEP, BIG_BLIND)
        nuovo_level = max(mano["level"], mano["street_bets"][idx]) + extra
        da_aggiungere = nuovo_level - mano["street_bets"][idx]
        _applica_puntata(stato, mano, idx, da_aggiungere)
        mano["level"] = max(mano["street_bets"])
        mano["acted"][idx] = True
        for i in range(mano["n_players"]):
            if i != idx and _puo_agire(stato, mano, i):
                mano["acted"][i] = False
    elif azione == "all_in":
        chips = stato["players"][idx]["chips"]
        if chips <= 0:
            return
        _applica_puntata(stato, mano, idx, chips)
        mano["level"] = max(mano["street_bets"])
        mano["all_in"][idx] = True
        mano["acted"][idx] = True
        for i in range(mano["n_players"]):
            if i != idx and _puo_agire(stato, mano, i):
                mano["acted"][i] = False
        mano["messaggio"] = f"{stato['players'][idx]['nome']} va all-in!"

    _dopo_azione(stato, mano)

# ── AI del computer ────────────────────────────────────────────────────────────

_PROFILI_AI = {
    "Facile": {
        "allin_min_call": 0.58, "allin_margine_forza": 0.42, "allin_margine_odds": 0.32,
        "allin_pot_odds": 0.22, "allin_pot_odds_p": 0.22, "allin_hero_p": 0.04,
        "forte_raise_p": 0.38, "buona_reraise_p": 0.28, "buona_open_p": 0.20,
        "media_bluff_p": 0.08, "media_pot_odds": 0.30, "media_pot_ratio": 0.45, "media_call_p": 0.32,
        "mw_bluff_p": 0.04, "mw_pot_odds": 0.24, "mw_small_raise_p": 0.28,
        "mw_bluff_call_p": 0.10, "mw_fold_p": 0.58, "mw_pot_odds2": 0.18,
        "weak_bluff_p": 0.02, "weak_pot_odds": 0.10, "weak_pot_call_p": 0.08, "raise_mult": 0.75,
    },
    "Medio": {
        "allin_min_call": 0.52, "allin_margine_forza": 0.35, "allin_margine_odds": 0.42,
        "allin_pot_odds": 0.30, "allin_pot_odds_p": 0.40, "allin_hero_p": 0.10,
        "forte_raise_p": 0.55, "buona_reraise_p": 0.45, "buona_open_p": 0.35,
        "media_bluff_p": 0.22, "media_pot_odds": 0.40, "media_pot_ratio": 0.60, "media_call_p": 0.50,
        "mw_bluff_p": 0.12, "mw_pot_odds": 0.32, "mw_small_raise_p": 0.48,
        "mw_bluff_call_p": 0.22, "mw_fold_p": 0.40, "mw_pot_odds2": 0.25,
        "weak_bluff_p": 0.07, "weak_pot_odds": 0.15, "weak_pot_call_p": 0.20, "raise_mult": 1.0,
    },
    "Difficile": {
        "allin_min_call": 0.48, "allin_margine_forza": 0.30, "allin_margine_odds": 0.48,
        "allin_pot_odds": 0.38, "allin_pot_odds_p": 0.52, "allin_hero_p": 0.16,
        "forte_raise_p": 0.68, "buona_reraise_p": 0.58, "buona_open_p": 0.48,
        "media_bluff_p": 0.32, "media_pot_odds": 0.48, "media_pot_ratio": 0.72, "media_call_p": 0.62,
        "mw_bluff_p": 0.18, "mw_pot_odds": 0.38, "mw_small_raise_p": 0.58,
        "mw_bluff_call_p": 0.30, "mw_fold_p": 0.28, "mw_pot_odds2": 0.32,
        "weak_bluff_p": 0.12, "weak_pot_odds": 0.22, "weak_pot_call_p": 0.28, "raise_mult": 1.35,
    },
}


def _profilo_ai(stato):
    return _PROFILI_AI.get(stato.get("difficolta", "Medio"), _PROFILI_AI["Medio"])


def _pot_odds(mano, to_call):
    if to_call <= 0:
        return 0.0
    return to_call / (mano["pot"] + to_call)


def _facing_raise(mano, idx, to_call):
    if to_call <= 0:
        return False
    return any(
        mano["street_bets"][j] > mano["street_bets"][idx]
        for j in range(mano["n_players"])
        if j != idx and not mano["folded"][j]
    )


def _avversario_all_in(mano, idx):
    return any(mano["all_in"][j] and not mano["folded"][j] for j in range(mano["n_players"]) if j != idx)


def _raise_amount_cpu(stato, mano, idx, forza):
    p = _profilo_ai(stato)
    mult = p["raise_mult"]
    pot = max(mano["pot"], BIG_BLIND)
    if forza >= 0.75:
        base = min(BIG_BLIND * 3, max(RAISE_STEP * 2, pot // 3))
    elif forza >= 0.55:
        base = max(RAISE_STEP, BIG_BLIND * 2)
    elif forza >= 0.40:
        base = RAISE_STEP
    else:
        base = BIG_BLIND
    return max(BIG_BLIND, int(base * mult))


def _decide_cpu(stato, mano, idx):
    p = _profilo_ai(stato)
    forza = _stima_forza(mano["holes"][idx], mano["community"])
    to_call = _to_call(mano, idx)
    chips = stato["players"][idx]["chips"]
    can_check = to_call == 0
    can_raise = chips > to_call
    pot_odds = _pot_odds(mano, to_call)
    facing_raise = _facing_raise(mano, idx, to_call)
    pot = mano["pot"]
    r = random.random()

    if _avversario_all_in(mano, idx) and to_call > 0:
        if forza >= p["allin_min_call"]:
            return "all_in" if to_call >= chips else "call"
        if forza >= p["allin_margine_forza"] and pot_odds <= p["allin_margine_odds"]:
            return "call"
        if pot_odds <= p["allin_pot_odds"] and r < p["allin_pot_odds_p"]:
            return "call"
        if r < p["allin_hero_p"]:
            return "call"
        return "fold"

    if forza >= 0.78:
        if can_raise and (not facing_raise or r < p["forte_raise_p"]):
            return "raise"
        if to_call > 0:
            return "all_in" if to_call >= chips else "call"
        return "check"

    if forza >= 0.62:
        if facing_raise and can_raise and r < p["buona_reraise_p"]:
            return "raise"
        if to_call > 0:
            return "call"
        if can_raise and r < p["buona_open_p"]:
            return "raise"
        return "check"

    if forza >= 0.45:
        if can_check:
            if can_raise and r < p["media_bluff_p"]:
                return "raise"
            return "check"
        if facing_raise:
            if pot_odds <= p["media_pot_odds"] or to_call <= pot * p["media_pot_ratio"]:
                return "call"
            if r < p["media_call_p"]:
                return "call"
            return "fold"
        return "call"

    if forza >= 0.28:
        if can_check:
            if can_raise and r < p["mw_bluff_p"]:
                return "raise"
            return "check"
        if facing_raise:
            if pot_odds <= p["mw_pot_odds"]:
                return "call"
            if to_call <= BIG_BLIND * 3 and r < p["mw_small_raise_p"]:
                return "call"
            if r < p["mw_bluff_call_p"]:
                return "call"
            return "fold"
        if to_call <= BIG_BLIND * 2:
            return "call"
        if pot_odds <= p["mw_pot_odds2"]:
            return "call"
        return "fold" if r < p["mw_fold_p"] else "call"

    if can_check and can_raise and r < p["weak_bluff_p"]:
        return "raise"
    if to_call > 0:
        if not facing_raise and to_call <= BIG_BLIND:
            return "call"
        if pot_odds <= p["weak_pot_odds"] and r < p["weak_pot_call_p"]:
            return "call"
        return "fold"
    return "check"


def _normalizza_azione_cpu(stato, mano, idx, azione):
    to_call = _to_call(mano, idx)
    chips = stato["players"][idx]["chips"]
    if azione == "raise" and chips <= to_call:
        azione = "all_in" if chips > 0 else "call"
    if azione == "call" and to_call >= chips > 0:
        azione = "all_in"
    if azione == "call" and to_call == 0:
        azione = "check"
    if azione == "all_in" and chips == 0:
        azione = "check"
    return azione


def _processa_turni_cpu(stato, mano):
    for _ in range(40):
        if mano["hand_over"] or mano["turno_idx"] == HUMAN_IDX:
            break
        idx = mano["turno_idx"]
        if not _puo_agire(stato, mano, idx):
            mano["turno_idx"] = _prossimo_attivo(mano, idx)
            if mano["turno_idx"] == idx:
                break
            continue
        forza = _stima_forza(mano["holes"][idx], mano["community"])
        azione = _normalizza_azione_cpu(stato, mano, idx, _decide_cpu(stato, mano, idx))
        raise_amt = _raise_amount_cpu(stato, mano, idx, forza) if azione == "raise" else RAISE_STEP
        _applica_azione(stato, mano, idx, azione, raise_amt)
        if mano["hand_over"]:
            break

# ── Stato di gioco ─────────────────────────────────────────────────────────────

def _nuova_mano(stato):
    in_mano = _giocatori_in_mano(stato)
    if len(in_mano) < 2:
        return False

    mazzo = _crea_mazzo()
    random.shuffle(mazzo)
    n = len(stato["players"])
    dealer_idx = stato["hand_num"] % n

    while stato["players"][dealer_idx]["chips"] == 0:
        dealer_idx = (dealer_idx + 1) % n

    holes = [[] for _ in range(n)]
    for i in in_mano:
        holes[i] = [mazzo.pop(), mazzo.pop()]

    street_bets = [0] * n
    acted = [False] * n
    folded = [i not in in_mano for i in range(n)]
    all_in = [False] * n

    mano = {
        "mazzo": mazzo,
        "holes": holes,
        "community": [],
        "fase": "preflop",
        "pot": 0,
        "street_bets": street_bets,
        "level": BIG_BLIND,
        "dealer_idx": dealer_idx,
        "n_players": n,
        "turno_idx": 0,
        "messaggio": "Blind postate. Pre-flop.",
        "hand_over": False,
        "result": None,
        "showdown_info": {},
        "acted": acted,
        "folded": folded,
        "all_in": all_in,
    }

    sb_i = _sb_idx(mano)
    bb_i = _bb_idx(mano)
    _applica_puntata(stato, mano, sb_i, min(SMALL_BLIND, stato["players"][sb_i]["chips"]))
    _applica_puntata(stato, mano, bb_i, min(BIG_BLIND, stato["players"][bb_i]["chips"]))
    mano["level"] = max(mano["street_bets"])
    mano["acted"][bb_i] = True

    sb_n = stato["players"][sb_i]["nome"]
    bb_n = stato["players"][bb_i]["nome"]
    mano["messaggio"] = f"SB: {sb_n} ({mano['street_bets'][sb_i]}) · BB: {bb_n} ({mano['street_bets'][bb_i]}). Pre-flop."
    mano["turno_idx"] = _primo_preflop(mano)
    while not _puo_agire(stato, mano, mano["turno_idx"]) and _conta_in_mano(mano) > 1:
        mano["turno_idx"] = _prossimo_attivo(mano, mano["turno_idx"])

    stato["mano"] = mano
    stato["hand_num"] += 1
    return True


def _stato_iniziale():
    return {
        "modalita": "1 vs 1",
        "difficolta": "Medio",
        "hand_num": 0,
        "mano": None,
        "players": None,
        "setup_done": False,
    }


def _inizializza():
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = _stato_iniziale()
        return
    stato = st.session_state[SESSION_KEY]
    if "players" not in stato:
        st.session_state[SESSION_KEY] = _stato_iniziale()


def _avvia_sessione(stato, modalita, difficolta):
    stato["modalita"] = modalita
    stato["difficolta"] = difficolta
    stato["players"] = _crea_giocatori(modalita)
    stato["hand_num"] = 0
    stato["setup_done"] = True
    _nuova_mano(stato)


def _sessione_finita(stato):
    return len(_giocatori_in_mano(stato)) <= 1


def _render_setup(stato):
    st.subheader("Texas Hold'em ♠")
    st.write("Scegli modalità e difficoltà, poi inizia la partita.")
    diff_desc = {
        "Facile": "passivo — folda spesso, bluff rari, raise piccoli",
        "Medio": "bilanciato — difesa e bluff moderati",
        "Difficile": "aggressivo — difende ampio, bluff frequenti, raise grandi",
    }
    c1, c2 = st.columns(2)
    with c1:
        modalita = st.radio("Modalità", MODALITA_OPZIONI, key="th_setup_modalita")
    with c2:
        difficolta = st.selectbox("Difficoltà avversari", DIFFICOLTA_OPZIONI, key="th_setup_diff")
    st.caption(f"**{difficolta}:** {diff_desc[difficolta]}")
    if modalita == "1 vs 1":
        st.info("Partita testa a testa contro un avversario CPU.")
    else:
        st.info(f"Tavolo da 5: tu + {', '.join(NOMI_CPU_TAVOLO)}. Blind e turni ruotano.")
    if st.button("▶ Inizia partita", type="primary", key="th_start", use_container_width=True):
        _avvia_sessione(stato, modalita, difficolta)
        st.rerun()

def _html_tabella_guida():
    azioni = (
        ("Check", "Passi senza puntare, se nessuno ha rilanciato"),
        ("Call", "Pari la puntata da chiamare"),
        ("Raise", "Aumenti la puntata"),
        ("Fold", "Scarti la mano"),
        ("All-in", "Punti tutte le fiches rimaste"),
    )
    corpo_azioni = "".join(
        f"<tr><td><strong>{a}</strong></td><td>{d}</td></tr>" for a, d in azioni
    )
    mani = "".join(
        f"<tr><td colspan=\"2\">{i + 1}. {NOMI_MANO[k]}</td></tr>"
        for i, k in enumerate(sorted(NOMI_MANO.keys(), reverse=True))
    )
    return (
        '<div class="br-score-wrap">'
        + '<div class="br-score-title">Regole e punteggi Texas Hold\'em</div>'
        + '<table class="br-score-table">'
        + '<thead><tr><th>Azione</th><th>Descrizione</th></tr></thead>'
        + f"<tbody>{corpo_azioni}</tbody>"
        + "</table>"
        + '<table class="br-score-table" style="border-top:1px solid #d4af37">'
        + '<thead><tr><th colspan="2">Mani (dalla più forte)</th></tr></thead>'
        + f"<tbody>{mani}</tbody>"
        + "</table>"
        + '<div class="br-score-note">'
        + "<strong>Obiettivo:</strong> restare l'unico con fiches. "
        + "Combini le tue 2 carte coperte con le 5 comuni (flop, turn, river). "
        + f"Blind {SMALL_BLIND}/{BIG_BLIND}. Al showdown vince la mano migliore; "
        + "in caso di pareggio il piatto si divide."
        + "</div></div>"
    )


def _render_guida():
    render_guida_expander(_html_tabella_guida())


# ── Render ─────────────────────────────────────────────────────────────────────

def render():
    """Interfaccia Streamlit per Texas Hold'em."""
    _inizializza()
    stato = st.session_state[SESSION_KEY]

    if not stato.get("setup_done"):
        _render_setup(stato)
        return

    mano = stato["mano"]
    modalita = stato.get("modalita", "1 vs 1")

    st.subheader("Texas Hold'em ♠")
    st.caption(
        f"**{modalita}** · Difficoltà **{stato.get('difficolta', 'Medio')}** · "
        f"Blind {SMALL_BLIND}/{BIG_BLIND}"
    )

    tot_altri = sum(stato["players"][i]["chips"] for i in range(1, mano["n_players"]))
    c1, c2, c3 = st.columns(3)
    c1.metric("Le tue fiches", stato["players"][HUMAN_IDX]["chips"])
    c2.metric("Piatto", mano["pot"])
    c3.metric("Avversari" if mano["n_players"] > 2 else "Computer", tot_altri)

    st.markdown(_html_tavolo(stato, mano), unsafe_allow_html=True)

    if mano["hand_over"]:
        risultato = mano["result"] or ""
        if "Hai perso" in risultato or "Hai foldato" in risultato:
            st.error(risultato)
        elif "Pareggio" in risultato or "diviso" in risultato:
            st.warning(risultato)
        else:
            st.success(risultato)
        if mano.get("showdown_info"):
            det = " · ".join(
                f"{stato['players'][i]['nome']}: {n}"
                for i, n in mano["showdown_info"].items()
            )
            st.caption(det)

        if _sessione_finita(stato):
            if stato["players"][HUMAN_IDX]["chips"] <= 0:
                st.error("Fiches esaurite! Hai perso la sessione.")
            else:
                st.success("Sei l'ultimo con fiches! Hai vinto la sessione.")
            if st.button("Nuova sessione", key="th_reset_session", type="primary", use_container_width=True):
                st.session_state[SESSION_KEY] = _stato_iniziale()
                st.rerun()
        else:
            if st.button("Nuova mano", key="th_nuova_mano", type="primary", use_container_width=True):
                if not _nuova_mano(stato):
                    st.rerun()
                else:
                    st.rerun()
        _render_guida()
        return

    if mano["turno_idx"] != HUMAN_IDX:
        _processa_turni_cpu(stato, mano)
        _render_guida()
        st.rerun()

    idx = HUMAN_IDX
    to_call = _to_call(mano, idx)
    can_check = to_call == 0
    chips_p = stato["players"][idx]["chips"]
    max_raise = _max_raise_extra(stato, mano, idx)
    can_raise = max_raise >= BIG_BLIND and not mano["all_in"][idx]

    st.caption(
        f"Puntata street — Tu: {mano['street_bets'][idx]} · Da chiamare: {to_call}"
    )
    if mano["all_in"][idx]:
        st.caption("⚠️ Sei **all-in** — non puoi puntare oltre.")

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        if not mano["all_in"][idx] and chips_p > 0:
            if can_check:
                if st.button("✔ Check", key="th_check", use_container_width=True):
                    _applica_azione(stato, mano, idx, "check")
                    st.rerun()
            else:
                call_amt = min(to_call, chips_p)
                lbl = f"📞 Call ({call_amt})" if call_amt < chips_p else f"📞 Call/All-in ({call_amt})"
                if st.button(lbl, key="th_call", use_container_width=True):
                    _applica_azione(stato, mano, idx, "all_in" if call_amt >= chips_p else "call")
                    st.rerun()
    with r1c2:
        if not mano["all_in"][idx]:
            if st.button("✖ Fold", key="th_fold", use_container_width=True):
                _applica_azione(stato, mano, idx, "fold")
                st.rerun()

    if chips_p > 0 and not mano["all_in"][idx]:
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            if can_raise:
                raise_amt = st.number_input(
                    "Raise +",
                    min_value=BIG_BLIND,
                    max_value=max_raise,
                    value=min(RAISE_STEP, max_raise),
                    step=10,
                    key="th_raise_amt",
                    label_visibility="collapsed",
                    help=f"Importo aggiuntivo — min {BIG_BLIND}, max {max_raise}",
                )
                if st.button(f"↑ Raise (+{int(raise_amt)})", key="th_raise", use_container_width=True):
                    _applica_azione(stato, mano, idx, "raise", int(raise_amt))
                    st.rerun()
        with r2c2:
            if st.button(f"💥 All-in ({chips_p})", key="th_allin", use_container_width=True):
                _applica_azione(stato, mano, idx, "all_in")
                st.rerun()
    if can_raise:
        st.caption(f"Importo raise aggiuntivo · min {BIG_BLIND} · max {max_raise} fiches.")

    _render_guida()
