"""Parole per la Forca — dizionario italiano locale (parole_italiane.txt)."""

import re
import unicodedata
from functools import lru_cache
from pathlib import Path

MIN_LUNGHEZZA = 4
MAX_LUNGHEZZA = 12

_ALLOWED = re.compile(r"^[a-zàèéìòù]+$")
_RIPETIZIONE = re.compile(r"(.)\1{2,}")

_DESINENZE_VERBALI = (
    "ando",
    "endo",
    "assero",
    "essero",
    "issero",
    "arono",
    "erono",
    "irono",
    "avamo",
    "evamo",
    "ivamo",
    "erebbe",
    "erebbero",
    "assimo",
    "essimo",
    "issimo",
    "avano",
    "evano",
    "ivano",
)

_FALLBACK = (
    "casa",
    "mare",
    "sole",
    "libro",
    "gatto",
    "cane",
    "pizza",
    "musica",
    "gioco",
    "parola",
    "storia",
    "montagna",
    "fiume",
    "verde",
    "amico",
)

_DIZIONARIO = Path(__file__).resolve().parent / "data" / "parole_italiane.txt"


def base_lettera(carattere: str) -> str:
    """Normalizza una lettera (es. è → e) per il confronto in gioco."""
    return unicodedata.normalize("NFD", carattere)[0].lower()


def parola_contiene_base(parola: str, lettera_base: str) -> bool:
    return any(base_lettera(c) == lettera_base for c in parola)


def parola_completata(parola: str, lettere_indovinate: set[str]) -> bool:
    return all(base_lettera(c) in lettere_indovinate for c in parola)


def _parola_valida(parola: str) -> bool:
    if not MIN_LUNGHEZZA <= len(parola) <= MAX_LUNGHEZZA:
        return False
    if not _ALLOWED.match(parola):
        return False
    if any(parola.endswith(s) for s in _DESINENZE_VERBALI):
        return False
    if _RIPETIZIONE.search(parola):
        return False
    return bool(re.search(r"[aeiouàèéìòù]", parola))


@lru_cache(maxsize=1)
def get_parole() -> tuple[str, ...]:
    """Elenco parole italiane filtrate dal dizionario locale."""
    if not _DIZIONARIO.is_file():
        return _FALLBACK

    parole: set[str] = set()
    for riga in _DIZIONARIO.read_text(encoding="utf-8").splitlines():
        parola = riga.strip().lower()
        if parola and _parola_valida(parola):
            parole.add(parola)

    parole.update(w for w in _FALLBACK if _parola_valida(w))
    if not parole:
        return _FALLBACK
    return tuple(sorted(parole))


def __getattr__(name: str):
    if name == "PAROLE":
        return get_parole()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
