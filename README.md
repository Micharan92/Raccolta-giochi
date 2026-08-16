# Raccolta di giochi

Applicazione web in Python con [Streamlit](https://streamlit.io): **12 mini-giochi** giocabili dal browser, con menu nella barra laterale.

Autore: **Michael**

---

## Come si usa l’app

1. Avvia l’applicazione (vedi [Installazione](#installazione-in-locale)).
2. Nel browser si apre `https://raccolta-giochi-scwqom39yfytdx5wfbhmnw.streamlit.app/`.
3. Nella **sidebar a sinistra** scegli un gioco.
4. Segui le istruzioni a schermo. Molti giochi hanno il pulsante **Nuova partita** / **Gioca ancora** per ricominciare.

Lo stato della partita (punteggio, griglia, parole, mazzo, ecc.) è salvato in `st.session_state`, così resta tra un clic e l’altro.

---

## Giochi e istruzioni

### 1. Indovina il numero

Il computer pensa a un numero tra **1 e 100**.

- Inserisci un tentativo nel campo numerico e premi **Prova**.
- Ricevi un indizio: il numero è **più alto** o **più basso**.
- Si conta il numero di tentativi. Quando indovini puoi avviare una nuova partita.

### 2. Lancio del dado

Scegli un numero da **1 a 6** e lancia il dado (faccia 2D con i puntini).

- Seleziona il tuo numero nel menu.
- Premi **Lancia il dado**: il dado ruota e si ferma su un risultato da 1 a 6.
- **Vinci** se il numero scelto coincide con i puntini (e con il testo del risultato).

Il gioco gira in un componente HTML/JavaScript dentro la pagina Streamlit.

### 3. Sasso, carta, forbici

Classico contro il computer.

- **Sasso** batte forbici, **carta** batte sasso, **forbici** battono carta.
- Clicca la tua mossa; il PC sceglie a caso. Pareggio se le mosse sono uguali.

### 4. Testa o croce

- Premi **Testa** o **Croce**.
- La moneta esce a caso: vinci se hai indovinato.

### 5. Quiz

Domande a risposta multipla in **italiano** (116 domande nel database).

- Scegli quante domande (5, 10, 15, 20, 25 o 30), la **difficoltà** (Qualsiasi, Facile, Media, Difficile) e la **categoria**.
- Premi **Nuove domande casuali** per generare il set (le opzioni vengono mescolate).
- Per ogni domanda scegli una risposta e premi **Conferma risposta**, poi **Prossima domanda**.
- Alla fine vedi il punteggio (es. 7/10).

Le domande sono in `giochi/domande_quiz.py`.

### 6. Forca

Indovina la parola segreta **lettera per lettera**.

- Hai al massimo **10 errori**.
- Scrivi una lettera e conferma. Le lettere già provate sono elencate.
- Vinci se completi la parola; perdi se superi i 10 errori.

Le parole sono in `giochi/parole_forca.py`.

### 7. Parola mescolata

Vedi le lettere di una parola **in ordine casuale** e ricostruisci la parola originale.

- Scrivi la parola nel campo (maiuscole/minuscole indifferenti) e premi **Conferma**.
- Se sbagli, viene mostrata la soluzione; poi puoi chiedere una nuova parola.

Le parole sono in `giochi/parole_mescolata.py`.

### 8. Serpente, acqua, pistola

Variante di sasso-carta-forbici.

- **Serpente** batte acqua, **acqua** batte pistola, **pistola** batte serpente.
- Clicca la tua mossa; il computer gioca a caso.

### 9. Snake

Classico snake su canvas HTML5 (clicca sul riquadro di gioco per usare la tastiera).

- **Spazio**: inizia o metti in pausa.
- **Frecce** oppure **W A S D**: muovi il serpente.
- Mangia il cibo rosso per allungarti e fare punti.
- Obiettivo: **450 punti**. Non urtare i muri né la tua coda.
- Dopo game over, **Spazio** per ricominciare.

### 10. Tris

Griglia 3×3 contro il computer.

- Sei **X**, il computer è **O**.
- Clicca una casella libera; poi gioca il PC (mossa casuale tra le libere).
- Vinci con tre simboli in riga, colonna o diagonale. Possibile il pareggio.

### 11. Blackjack

Versione semplificata del 21, con tavolo e carte animate.

- Obiettivo: avvicinarti a **21** senza superarlo. Figure = 10; **asso** = 11 oppure 1.
- Il banco distribuisce le carte (una coperta per il banco).
- **Pesca carta**: prendi una carta. Se superi 21, hai perso (sballo).
- **Fermati**: tocca al banco, che pesca finché ha meno di **17**.
- Vince chi è più vicino a 21 senza sballare; se il banco sballa, vinci tu.

### 12. Memoria numerica

Memorizza sequenze di cifre sempre più lunghe.

- Al livello *n* vedi *n* numeri da 1 a 9.
- Premi **Ho memorizzato**: la sequenza sparisce dopo un conto alla rovescia.
- Riscrivi i numeri **separati da spazi** (es. `3 7 1`) e conferma.
- Se è corretto passi al livello successivo; se sbagli la partita finisce e vedi il livello raggiunto.

---

## Struttura del progetto

```
indovina-numero/
├── app.py                      # App Streamlit (menu + routing)
├── main.py                     # Avvio locale: python main.py
├── requirements.txt            # Dipendenze (streamlit)
├── README.md                   # Questo file
└── giochi/
    ├── __init__.py
    ├── indovina_numero.py
    ├── lancio_dado.py          # Dado HTML/JS
    ├── sasso_carta_forbici.py
    ├── testa_o_croce.py
    ├── quiz.py
    ├── domande_quiz.py         # Database domande
    ├── forca.py
    ├── parole_forca.py         # Database parole forca
    ├── parola_mescolata.py
    ├── parole_mescolata.py     # Database parole mescolate
    ├── serpente_acqua_pistola.py
    ├── snake.py                # Snake HTML5
    ├── tris.py
    ├── blackjack.py
    └── memoria_numerica.py
```

Ogni gioco espone una funzione `render()` usata da `app.py`.

---

## Requisiti

- Python **3.10+** (consigliato 3.11+)
- `pip`
- Browser moderno (per Snake e il dado servono anche JavaScript e focus sulla tastiera)

---

## Installazione in locale

```bash
git clone https://github.com/Micharan92/indovina-numero.git
cd indovina-numero
```

Ambiente virtuale (consigliato):

```bash
python -m venv venv
```

- Windows: `venv\Scripts\activate`
- macOS / Linux: `source venv/bin/activate`

```bash
pip install -r requirements.txt
```

Dipendenza: `streamlit>=1.32.0`.

---

## Avvio in locale

```bash
streamlit run app.py
```

oppure:

```bash
python main.py
```

L’app si apre su **http://localhost:8501**.

---

## Deploy su Streamlit Community Cloud

1. Carica il progetto su GitHub.
2. Vai su [share.streamlit.io](https://share.streamlit.io) e accedi con GitHub.
3. **New app** → repository e branch.
4. **Main file path:** `app.py`
5. **Deploy** (le dipendenze arrivano da `requirements.txt`).

---

## Come è fatto il codice

| File | Ruolo |
|------|--------|
| `app.py` | Titolo, sidebar, dizionario `GIOCHI` |
| `giochi/*.py` | Un gioco = una `render()` |
| `giochi/domande_quiz.py` | Testo, opzioni, categoria e difficoltà del quiz |
| `giochi/parole_*.py` | Liste di parole per Forca e Parola mescolata |
| `lancio_dado.py` / `snake.py` | `st.components.v1.html` + canvas JS |

---

## Personalizzazione

**Nuovo gioco**

1. Crea `giochi/mio_gioco.py` con `def render():`.
2. Importalo in `app.py` e aggiungilo al dizionario `GIOCHI`.

**Contenuti**

- Quiz → `giochi/domande_quiz.py`
- Forca → `giochi/parole_forca.py`
- Parola mescolata → `giochi/parole_mescolata.py`

---

## Licenza

Progetto didattico open source: usalo, modificalo e condividilo.
