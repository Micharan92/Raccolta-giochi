"""UI condivisa per pannello regole/punteggi (expander, stile tavolo verde/oro)."""

import streamlit as st

CSS_GUIDA = """
<style>
.br-score-wrap {
    margin-top: 0.75rem;
    border: 2px solid #8b6914;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    background: #fffef8 !important;
}
.br-score-title {
    background: linear-gradient(145deg, #0d5c2e, #1a7a3e);
    color: #f5e6c8;
    font-size: 0.88rem;
    font-weight: 700;
    padding: 0.45rem 0.75rem;
    text-align: center;
}
.br-score-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
    background: #fffef8 !important;
    color: #2c2c2c !important;
}
.br-score-table th {
    background: rgba(212,175,55,0.22) !important;
    color: #5c4a1a !important;
    font-weight: 700;
    padding: 0.4rem 0.6rem;
    text-align: left;
    border-bottom: 1px solid #d4af37;
}
.br-score-table td {
    padding: 0.35rem 0.6rem;
    border-bottom: 1px solid #eee8d8;
    color: #2c2c2c !important;
    background: #fffef8 !important;
}
.br-score-table td strong {
    color: #2c2c2c !important;
}
.br-score-table tr:last-child td { border-bottom: none; }
.br-score-table tr:nth-child(even) td { background: #f5f0e6 !important; }
.br-score-pts {
    font-weight: 800;
    color: #0d5c2e !important;
    text-align: center;
    min-width: 3rem;
}
.br-score-pts.zero { color: #888 !important; font-weight: 600; }
.br-score-note {
    background: #f5f0e6 !important;
    color: #444 !important;
    font-size: 0.78rem;
    padding: 0.45rem 0.75rem;
    border-top: 1px dashed #d4af37;
    line-height: 1.45;
}
.br-score-note strong { color: #0d5c2e !important; }
@media (max-width: 768px) {
    .br-score-table { font-size: 0.78rem; }
}
</style>
"""


def render_guida_expander(html_tabella: str, titolo: str = "📖 Regole e punteggi"):
    """Mostra tabella regole in expander (stile tavolo verde/oro)."""
    with st.expander(titolo, expanded=False):
        st.markdown(CSS_GUIDA + html_tabella, unsafe_allow_html=True)
