# Raccolta di Giochi

Web app multi-gioco in **Python** — 9 mini-giochi giocabili dal browser, menu laterale, stato di partita persistente. Progetto personale di portfolio.

**Autore:** Michael

---

## Demo live

🔗 **[Gioca online](INSERISCI_QUI_IL_LINK_STREAMLIT)**

> Esempio: `https://tuo-app.streamlit.app`

---

## Stack

| Layer | Tecnologie |
|-------|------------|
| **Backend / UI** | Python 3.10+, [Streamlit](https://streamlit.io) |
| **Stato applicazione** | `st.session_state` (partite, punteggi, fasi di gioco) |
| **Grafica interattiva** | HTML5 Canvas + JavaScript (`st.components.v1.html`) |
| **Logica di gioco** | Python standard library (`random`, `itertools`, `collections`) |
| **Deploy** | Streamlit Community Cloud |

**Dipendenza esterna:** `streamlit>=1.32.0` — tutto il resto è stdlib Python o moduli locali del progetto.

---

## Cosa include

9 giochi in un’unica app: Lancio del dado, Quiz (116 domande IT), Forca, **Snake**, Tris, **Blackjack**, **Briscola**, **Scopa**, **Texas Hold'em**.

**Highlight tecnici:**
- Architettura modulare — ogni gioco espone `render()`, registrato in `app.py`
- Texas Hold'em con valutazione mani (coppia → scala reale), puntate, all-in e AI avversaria
- Snake e dado con componenti HTML/JS custom; layout responsive per mobile
- Database locali per quiz e parole (`domande_quiz.py`, `parole_forca.py`, …)

---

## Struttura

```
app.py              → entry point, menu sidebar
giochi/*.py         → un file = un gioco (render())
giochi/*_quiz.py    → dati quiz / parole
requirements.txt    → streamlit
```

---

## Licenza

Progetto didattico open source — libero uso e modifica.
