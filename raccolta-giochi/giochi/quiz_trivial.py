"""Quiz a tabellone stile categorie a spicchi (1 vs CPU)."""

import copy
import math
import random
import time
from datetime import timedelta

import streamlit as st
import streamlit.components.v1 as components

from giochi.dado_ui import altezza_iframe_dado, html_dado
from giochi.domande_quiz import DIFFICOLTA, DOMANDE_ITALIANE

SESSION_KEY = "quiz_trivial"
NUM_CASELLE = 24

CATEGORIE_TRIVIAL = [
    {"nome": "Geografia", "colore": "#1a7a3e", "emoji": "🌍"},
    {"nome": "Storia", "colore": "#2563eb", "emoji": "🏛️"},
    {"nome": "Scienza", "colore": "#7c3aed", "emoji": "🔬"},
    {"nome": "Arte e letteratura", "colore": "#dc2626", "emoji": "🎨"},
    {"nome": "Sport", "colore": "#ea580c", "emoji": "⚽"},
    {"nome": "Italia", "colore": "#ca8a04", "emoji": "🇮🇹"},
]

DIFFICOLTA_TRIVIAL = [d for d in DIFFICOLTA if d != "Qualsiasi"]
_PROB_CPU_GIOCO = {"Facile": 0.68, "Media": 0.52, "Difficile": 0.36}
_CPU_DADO_ATTESA_S = 1.35


def _mescola_opzioni(domanda):
    domanda = copy.deepcopy(domanda)
    testi = list(domanda["opzioni"].values())
    random.shuffle(testi)
    lettere = ["a", "b", "c", "d"]
    risposta_corretta = domanda["opzioni"][domanda["risposta"]]
    domanda["opzioni"] = {lettere[i]: testi[i] for i in range(4)}
    domanda["risposta"] = lettere[testi.index(risposta_corretta)]
    return domanda


def _categoria_casella(posizione: int) -> str:
    return CATEGORIE_TRIVIAL[posizione % len(CATEGORIE_TRIVIAL)]["nome"]


def _info_categoria(nome: str) -> dict:
    for cat in CATEGORIE_TRIVIAL:
        if cat["nome"] == nome:
            return cat
    return CATEGORIE_TRIVIAL[0]


def _pesca_domanda(categoria: str, usate: set[str], difficolta: str):
    pool = [
        d
        for d in DOMANDE_ITALIANE
        if d["categoria"] == categoria
        and d["difficolta"] == difficolta
        and d["domanda"] not in usate
    ]
    if not pool:
        pool = [
            d
            for d in DOMANDE_ITALIANE
            if d["categoria"] == categoria and d["difficolta"] == difficolta
        ]
    scelta = random.choice(pool)
    usate.add(scelta["domanda"])
    return _mescola_opzioni(scelta)


def _ha_tutti_spicchi(spicchi: list[str]) -> bool:
    return len(spicchi) >= len(CATEGORIE_TRIVIAL)


def _nuova_partita():
    return {
        "avviato": False,
        "fase": "setup",
        "turno": "giocatore",
        "difficolta_gioco": "Media",
        "pos_giocatore": 0,
        "pos_cpu": 12,
        "spicchi_giocatore": [],
        "spicchi_cpu": [],
        "ultimo_lancio": None,
        "ultimo_mossa": None,
        "categoria_corrente": None,
        "domanda": None,
        "feedback": None,
        "messaggio": "Scegli la difficoltà e inizia la partita.",
        "finale_giocatore": False,
        "finale_cpu": False,
        "vincitore": None,
        "domande_usate": set(),
        "cpu_dado_ts": 0.0,
        "partita_id": random.randint(1, 1_000_000),
    }


def _inizializza():
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = _nuova_partita()
    else:
        stato = st.session_state[SESSION_KEY]
        stato.setdefault("avviato", stato.get("fase") not in ("setup", None))
        stato.setdefault("difficolta_gioco", "Media")
        stato.setdefault("cpu_dado_ts", 0.0)
        stato.setdefault("ultimo_mossa", None)
        if stato.get("fase") == "lancio_cpu":
            stato["fase"] = "cpu_dado"


def _avanza_posizione(pos: int, passi: int) -> int:
    return (pos + passi) % NUM_CASELLE


def _assegna_spicchio(stato, giocatore: str, categoria: str):
    chiave = "spicchi_giocatore" if giocatore == "giocatore" else "spicchi_cpu"
    if categoria not in stato[chiave]:
        stato[chiave].append(categoria)
    if _ha_tutti_spicchi(stato[chiave]):
        if giocatore == "giocatore":
            stato["finale_giocatore"] = True
        else:
            stato["finale_cpu"] = True


def _prepara_domanda(stato, categoria: str, finale: bool = False):
    difficolta = stato.get("difficolta_gioco", "Media")
    if finale:
        pool = [
            d
            for d in DOMANDE_ITALIANE
            if d["difficolta"] == difficolta and d["domanda"] not in stato["domande_usate"]
        ]
        if not pool:
            pool = [d for d in DOMANDE_ITALIANE if d["difficolta"] == difficolta]
        domanda = _mescola_opzioni(random.choice(pool))
        stato["domande_usate"].add(domanda["domanda"])
        stato["categoria_corrente"] = "Finale"
    else:
        domanda = _pesca_domanda(categoria, stato["domande_usate"], difficolta)
        stato["categoria_corrente"] = categoria
    stato["domanda"] = domanda
    stato["fase"] = "domanda"
    stato["feedback"] = None


def _posizione_giocatore(stato, giocatore: str) -> int:
    return stato["pos_giocatore" if giocatore == "giocatore" else "pos_cpu"]


def _lancia_dado(stato, giocatore: str) -> int:
    lancio = random.randint(1, 6)
    stato["ultimo_lancio"] = lancio
    stato["ultimo_mossa"] = giocatore
    pos_key = "pos_giocatore" if giocatore == "giocatore" else "pos_cpu"
    stato[pos_key] = _avanza_posizione(stato[pos_key], lancio)
    return lancio


def _messaggio_lancio(stato, giocatore: str, lancio: int) -> str:
    nome = "Tu" if giocatore == "giocatore" else "CPU"
    if giocatore == "giocatore" and stato["finale_giocatore"]:
        return f"{nome}: dado {lancio}. Domanda finale!"
    if giocatore == "cpu" and stato["finale_cpu"]:
        return f"{nome}: dado {lancio}. Domanda finale..."
    pos = _posizione_giocatore(stato, giocatore)
    categoria = _categoria_casella(pos)
    info = _info_categoria(categoria)
    return (
        f"{nome}: dado **{lancio}** → casella **{pos + 1}** "
        f"{info['emoji']} **{categoria}**"
    )


def _prepara_dopo_lancio(stato, giocatore: str):
    if giocatore == "giocatore" and stato["finale_giocatore"]:
        _prepara_domanda(stato, "", finale=True)
        return
    if giocatore == "cpu" and stato["finale_cpu"]:
        _prepara_domanda(stato, "", finale=True)
        return
    _prepara_domanda(stato, _categoria_casella(_posizione_giocatore(stato, giocatore)))


def _lancia_turno(stato, giocatore: str):
    lancio = _lancia_dado(stato, giocatore)
    stato["messaggio"] = _messaggio_lancio(stato, giocatore, lancio)
    _prepara_dopo_lancio(stato, giocatore)


def _inizia_lancio_cpu(stato):
    lancio = _lancia_dado(stato, "cpu")
    stato["turno"] = "cpu"
    stato["fase"] = "cpu_dado"
    stato["cpu_dado_ts"] = time.time()
    stato["messaggio"] = _messaggio_lancio(stato, "cpu", lancio)


def _cpu_completa_turno(stato):
    if stato.get("fase") != "cpu_dado":
        return
    stato["fase"] = "cpu_risponde"
    _prepara_dopo_lancio(stato, "cpu")
    corretto, lettera, testo = _cpu_scegli_risposta(stato, stato["domanda"])
    _risolvi_risposta(
        stato,
        "cpu",
        corretto,
        risposta_cpu_lettera=lettera,
        risposta_cpu_testo=testo,
    )


def _cpu_scegli_risposta(stato, domanda) -> tuple[bool, str, str]:
    """La CPU risponde correttamente o sceglie una risposta sbagliata a caso."""
    prob = _PROB_CPU_GIOCO.get(stato.get("difficolta_gioco", "Media"), 0.52)
    corretto = random.random() < prob
    lettera_corretta = domanda["risposta"]
    if corretto:
        lettera = lettera_corretta
    else:
        lettere_sbagliate = [k for k in domanda["opzioni"] if k != lettera_corretta]
        lettera = random.choice(lettere_sbagliate)
    return corretto, lettera, domanda["opzioni"][lettera]


def _risolvi_risposta(stato, giocatore: str, corretto: bool, **extra_feedback):
    categoria = stato["categoria_corrente"]
    nome = "Tu" if giocatore == "giocatore" else "CPU"
    spicchi_key = "spicchi_giocatore" if giocatore == "giocatore" else "spicchi_cpu"
    finale = categoria == "Finale"

    if corretto:
        if finale:
            stato["vincitore"] = giocatore
            stato["fase"] = "fine"
            stato["messaggio"] = f"🏆 {nome} vince con la domanda finale!"
            return
        if categoria not in stato[spicchi_key]:
            _assegna_spicchio(stato, giocatore, categoria)
            stato["messaggio"] = f"✅ {nome}: risposta corretta! Spicchio **{categoria}** conquistato."
        else:
            stato["messaggio"] = f"✅ {nome}: corretto (spicchio {categoria} già tuo)."
    else:
        stato["messaggio"] = f"❌ {nome}: risposta sbagliata."

    stato["fase"] = "feedback"
    stato["feedback"] = {"corretto": corretto, "giocatore": giocatore, **extra_feedback}


def _prossimo_turno(stato):
    stato["domanda"] = None
    stato["feedback"] = None
    if stato["turno"] == "giocatore":
        _inizia_lancio_cpu(stato)
    else:
        stato["turno"] = "giocatore"
        stato["fase"] = "lancio"
        stato["ultimo_lancio"] = None
        stato["messaggio"] = "Tocca a te! Lancia il dado."


def _mostra_dado(ultimo_lancio: int):
    components.html(
        html_dado(mode="show", risultato=ultimo_lancio),
        height=altezza_iframe_dado("show"),
    )


@st.fragment(run_every=timedelta(seconds=0.4))
def _cpu_dado_auto():
    stato = st.session_state.get(SESSION_KEY)
    if not stato or stato.get("fase") != "cpu_dado":
        return
    if time.time() - stato.get("cpu_dado_ts", 0) < _CPU_DADO_ATTESA_S:
        return
    _cpu_completa_turno(stato)
    st.rerun()


def _coord_casella(indice: int) -> tuple[float, float]:
    angolo = (indice / NUM_CASELLE) * 360 - 90
    rad = math.radians(angolo)
    r = 42
    return 50 + r * math.cos(rad), 50 + r * math.sin(rad)


def _html_tabellone(stato) -> str:
    pos_g = stato["pos_giocatore"]
    pos_c = stato["pos_cpu"]
    ultimo_mossa = stato.get("ultimo_mossa")
    ultimo_lancio = stato.get("ultimo_lancio")
    stessa_casella = pos_g == pos_c

    celle = []
    for i in range(NUM_CASELLE):
        cat = CATEGORIE_TRIVIAL[i % len(CATEGORIE_TRIVIAL)]
        x, y = _coord_casella(i)
        cls = ["cell"]
        if i == pos_g:
            cls.append("on-player")
        if i == pos_c:
            cls.append("on-cpu")
        if ultimo_lancio and ultimo_mossa == "giocatore" and i == pos_g:
            cls.append("landed-player")
        if ultimo_lancio and ultimo_mossa == "cpu" and i == pos_c:
            cls.append("landed-cpu")
        celle.append(
            f'<div class="{" ".join(cls)}" style="left:{x:.1f}%;top:{y:.1f}%;background:{cat["colore"]};" '
            f'title="{cat["nome"]} · Casella {i + 1}">{cat["emoji"]}</div>'
        )

    segnalini = []
    for giocatore, pos, cls in (("giocatore", pos_g, "player"), ("cpu", pos_c, "cpu")):
        x, y = _coord_casella(pos)
        if stessa_casella:
            if giocatore == "giocatore":
                x -= 2.8
                y -= 1.8
            else:
                x += 2.8
                y += 1.8
        label = "Tu" if giocatore == "giocatore" else "CPU"
        segnalini.append(
            f'<div class="pawn {cls}" style="left:{x:.1f}%;top:{y:.1f}%;" title="{label}"></div>'
        )

    info_dado = ""
    if ultimo_lancio and ultimo_mossa:
        chi = "Tu" if ultimo_mossa == "giocatore" else "CPU"
        casella = pos_g + 1 if ultimo_mossa == "giocatore" else pos_c + 1
        info_dado = (
            f' · Ultimo lancio: <strong>{chi}</strong> ha fatto '
            f'<strong>{ultimo_lancio}</strong> → casella <strong>{casella}</strong>'
        )

    spicchi_g = "".join(
        f'<span class="wedge" style="background:{cat["colore"]}">{cat["nome"][:3]}</span>'
        for cat in CATEGORIE_TRIVIAL
        if cat["nome"] in stato["spicchi_giocatore"]
    ) or '<span class="wedge empty">—</span>'
    spicchi_c = "".join(
        f'<span class="wedge" style="background:{cat["colore"]}">{cat["nome"][:3]}</span>'
        for cat in CATEGORIE_TRIVIAL
        if cat["nome"] in stato["spicchi_cpu"]
    ) or '<span class="wedge empty">—</span>'

    return f"""
    <style>
    .tq-board-wrap {{
        background: linear-gradient(145deg, #0d5c2e, #1a7a3e);
        border: 3px solid #8b6914;
        border-radius: 16px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }}
    .tq-board {{
        position: relative;
        width: 100%;
        max-width: 340px;
        aspect-ratio: 1;
        margin: 0 auto;
        background: radial-gradient(circle, #145a30 35%, #0a3d20 70%);
        border-radius: 50%;
        border: 2px solid #d4af37;
    }}
    .tq-center {{
        position: absolute;
        left: 50%; top: 50%;
        transform: translate(-50%, -50%);
        width: 28%; height: 28%;
        border-radius: 50%;
        background: #fffef8;
        border: 2px dashed #8b6914;
        display: flex; align-items: center; justify-content: center;
        text-align: center;
        font-size: 0.72rem;
        font-weight: 700;
        color: #0d5c2e;
        padding: 4px;
        z-index: 2;
    }}
    .cell {{
        position: absolute;
        width: 9%; height: 9%;
        transform: translate(-50%, -50%);
        border-radius: 50%;
        border: 2px solid rgba(255,255,255,0.85);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.85rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.35);
        z-index: 1;
        transition: box-shadow 0.25s ease;
    }}
    .cell.on-player {{
        box-shadow: 0 0 0 3px #2563eb, 0 0 14px rgba(37, 99, 235, 0.75);
        z-index: 3;
    }}
    .cell.on-cpu {{
        box-shadow: 0 0 0 3px #dc2626, 0 0 14px rgba(220, 38, 38, 0.75);
        z-index: 3;
    }}
    .cell.on-player.on-cpu {{
        box-shadow: 0 0 0 3px #fbbf24, 0 0 16px rgba(251, 191, 36, 0.9);
        z-index: 4;
    }}
    .cell.landed-player {{
        animation: pulse-blue 1.1s ease-in-out infinite;
    }}
    .cell.landed-cpu {{
        animation: pulse-red 1.1s ease-in-out infinite;
    }}
    @keyframes pulse-blue {{
        0%, 100% {{ box-shadow: 0 0 0 4px #2563eb, 0 0 18px rgba(37, 99, 235, 0.9); }}
        50% {{ box-shadow: 0 0 0 6px #60a5fa, 0 0 26px rgba(96, 165, 250, 1); }}
    }}
    @keyframes pulse-red {{
        0%, 100% {{ box-shadow: 0 0 0 4px #dc2626, 0 0 18px rgba(220, 38, 38, 0.9); }}
        50% {{ box-shadow: 0 0 0 6px #f87171, 0 0 26px rgba(248, 113, 113, 1); }}
    }}
    .pawn {{
        position: absolute;
        width: 15px;
        height: 15px;
        border-radius: 50%;
        border: 2.5px solid #fff;
        transform: translate(-50%, -50%);
        z-index: 6;
        pointer-events: none;
    }}
    .pawn.player {{
        background: linear-gradient(145deg, #60a5fa, #2563eb);
        box-shadow: 0 0 10px rgba(37, 99, 235, 0.95);
    }}
    .pawn.cpu {{
        background: linear-gradient(145deg, #f87171, #dc2626);
        box-shadow: 0 0 10px rgba(220, 38, 38, 0.95);
    }}
    .tq-positions {{
        margin-top: 0.45rem;
        text-align: center;
        font-size: 0.76rem;
        color: #e8dcc0;
        line-height: 1.45;
    }}
    .tq-scores {{
        display: flex; justify-content: space-between; gap: 8px;
        margin-top: 0.6rem; font-size: 0.78rem;
    }}
    .tq-score {{
        flex: 1; background: rgba(255,255,255,0.12);
        border-radius: 8px; padding: 0.4rem 0.5rem; color: #f5e6c8;
    }}
    .tq-score strong {{ display: block; margin-bottom: 0.25rem; }}
    .wedge {{
        display: inline-block; font-size: 0.65rem; font-weight: 700;
        color: #fff; padding: 2px 5px; border-radius: 4px; margin: 1px;
    }}
    .wedge.empty {{ background: rgba(255,255,255,0.15); color: #ccc; }}
    @media (max-width: 768px) {{
        .tq-board-wrap {{ padding: 0.5rem; margin: 0.35rem 0; }}
        .tq-board {{ max-width: min(92vw, 320px); }}
        .tq-center {{ font-size: 0.62rem; width: 32%; height: 32%; }}
        .cell {{ width: 11%; height: 11%; font-size: 0.72rem; }}
        .pawn {{ width: 13px; height: 13px; }}
        .tq-positions {{ font-size: 0.8rem; }}
        .tq-scores {{ flex-direction: column; gap: 0.4rem; }}
        .tq-score {{ font-size: 0.82rem; }}
    }}
    @media (min-width: 769px) {{
        .tq-board {{ max-width: 360px; }}
    }}
    </style>
    <div class="tq-board-wrap">
        <div class="tq-board">
            <div class="tq-center">FINALE<br>6 spicchi</div>
            {''.join(celle)}
            {''.join(segnalini)}
        </div>
        <div class="tq-positions">
            🔵 Tu: casella <strong>{pos_g + 1}</strong> ·
            🔴 CPU: casella <strong>{pos_c + 1}</strong>{info_dado}
        </div>
        <div class="tq-scores">
            <div class="tq-score"><strong>🔵 Tu</strong>{spicchi_g}</div>
            <div class="tq-score"><strong>🔴 CPU</strong>{spicchi_c}</div>
        </div>
    </div>
    """


def _render_spicchi_giocatore(stato):
    righe = "".join(
        f'<div class="tq-spicchio-item">'
        f'{cat["emoji"]} {"✅" if cat["nome"] in stato["spicchi_giocatore"] else "⬜"} '
        f'<span>{cat["nome"]}</span></div>'
        for cat in CATEGORIE_TRIVIAL
    )
    st.markdown(
        f'<p style="margin:0.5rem 0 0.35rem;font-weight:700;">I tuoi spicchi</p>'
        f'<div class="tq-spicchi-grid">{righe}</div>'
        + """
        <style>
        .tq-spicchi-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.35rem;
            margin-bottom: 0.5rem;
        }
        .tq-spicchio-item {
            background: rgba(13,92,46,0.08);
            border: 1px solid rgba(139,105,20,0.35);
            border-radius: 8px;
            padding: 0.35rem 0.45rem;
            font-size: 0.78rem;
            line-height: 1.3;
        }
        @media (max-width: 768px) {
            .tq-spicchi-grid { grid-template-columns: repeat(2, 1fr); }
            .tq-spicchio-item { font-size: 0.82rem; padding: 0.45rem 0.5rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render():
    """Interfaccia quiz a tabellone."""
    _inizializza()
    stato = st.session_state[SESSION_KEY]

    st.caption(
        "Raccogli uno **spicchio** per ogni categoria rispondendo correttamente. "
        "Con tutti e 6 affronti la **domanda finale**."
    )

    if stato["fase"] == "setup":
        diff_idx = (
            DIFFICOLTA_TRIVIAL.index(stato["difficolta_gioco"])
            if stato["difficolta_gioco"] in DIFFICOLTA_TRIVIAL
            else 1
        )
        difficolta = st.selectbox(
            "Difficoltà partita",
            DIFFICOLTA_TRIVIAL,
            index=diff_idx,
            key="tq_difficolta",
            help="Tutte le categorie sono incluse; cambia solo la difficoltà delle domande.",
        )
        st.info("Scegli la difficoltà e avvia la partita.")
        if st.button("Inizia partita", type="primary", key="tq_inizia", use_container_width=True):
            stato["avviato"] = True
            stato["fase"] = "lancio"
            stato["turno"] = "giocatore"
            stato["difficolta_gioco"] = difficolta
            stato["messaggio"] = "Tocca a te! Lancia il dado."
            st.rerun()
        return

    st.markdown(_html_tabellone(stato), unsafe_allow_html=True)
    _render_spicchi_giocatore(stato)
    st.caption(f"Difficoltà partita: **{stato['difficolta_gioco']}**")
    st.info(stato["messaggio"])

    if stato["fase"] == "fine":
        if stato["vincitore"] == "giocatore":
            st.success("🏆 Hai vinto la partita!")
        else:
            st.error("La CPU ha vinto. Riprova!")
        if st.button("Nuova partita", type="primary", key="tq_nuova", use_container_width=True):
            st.session_state[SESSION_KEY] = _nuova_partita()
            st.rerun()
        return

    if stato["fase"] == "cpu_dado":
        st.caption("🤖 La CPU sta lanciando il dado...")
        if stato["ultimo_lancio"]:
            _mostra_dado(stato["ultimo_lancio"])
        _cpu_dado_auto()
        return

    if stato["fase"] == "lancio" and stato["turno"] == "giocatore":
        if st.button("🎲 Lancia il dado", type="primary", key="tq_lancia", use_container_width=True):
            _lancia_turno(stato, "giocatore")
            st.rerun()
        return

    if stato["ultimo_lancio"] and stato["fase"] in ("domanda", "feedback"):
        _mostra_dado(stato["ultimo_lancio"])

    if stato["fase"] == "domanda" and stato["domanda"] and stato["turno"] == "giocatore":
        domanda = stato["domanda"]
        cat = stato["categoria_corrente"]
        if cat == "Finale":
            st.warning("⭐ **DOMANDA FINALE** — una risposta corretta e vinci!")
        else:
            info = _info_categoria(cat)
            st.markdown(f"**{info['emoji']} {cat}** · Difficoltà: {domanda['difficolta']}")
        st.markdown(f"**{domanda['domanda']}**")
        opzioni = [f"{k}) {v}" for k, v in domanda["opzioni"].items()]
        lettere = list(domanda["opzioni"].keys())
        scelta = st.radio(
            "Risposta",
            opzioni,
            key=f"tq_q_{stato['partita_id']}_{stato['pos_giocatore']}_{len(stato['domande_usate'])}",
        )
        if st.button("Conferma", type="primary", key="tq_conf", use_container_width=True):
            lettera = lettere[opzioni.index(scelta)]
            _risolvi_risposta(stato, "giocatore", lettera == domanda["risposta"])
            st.rerun()
        return

    if stato["fase"] == "feedback":
        fb = stato["feedback"] or {}
        if fb.get("giocatore") == "giocatore":
            if fb.get("corretto"):
                st.success("Risposta corretta!")
            else:
                domanda = stato.get("domanda") or {}
                risp = domanda.get("opzioni", {}).get(domanda.get("risposta", ""), "")
                st.error(f"Sbagliato. Era: {risp}")
        elif fb.get("giocatore") == "cpu":
            domanda = stato.get("domanda") or {}
            cat = stato.get("categoria_corrente")
            if cat == "Finale":
                st.markdown("**⭐ Domanda finale CPU**")
            elif cat:
                info = _info_categoria(cat)
                st.markdown(f"**{info['emoji']} {cat}** · Difficoltà: {domanda.get('difficolta', '—')}")
            st.markdown(f"**Domanda:** {domanda.get('domanda', '—')}")
            lettera_cpu = fb.get("risposta_cpu_lettera", "?")
            testo_cpu = fb.get("risposta_cpu_testo", "—")
            st.markdown(f"**Risposta CPU:** {lettera_cpu}) {testo_cpu}")
            if fb.get("corretto"):
                st.success("✅ La CPU ha risposto correttamente.")
            else:
                risp_ok = domanda.get("opzioni", {}).get(domanda.get("risposta", ""), "—")
                st.warning(
                    f"❌ Risposta sbagliata. Quella corretta era: "
                    f"{domanda.get('risposta', '?')}) {risp_ok}"
                )
            st.caption(stato["messaggio"])
        if st.button("Continua", type="primary", key="tq_avanti", use_container_width=True):
            if stato["vincitore"]:
                stato["fase"] = "fine"
            else:
                _prossimo_turno(stato)
            st.rerun()
