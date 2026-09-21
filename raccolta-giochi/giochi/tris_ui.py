"""Helper CSS centratura componente Tris."""

VUOTO = " "


def css_tris_wrap() -> str:
    return """
    <style>
    div[data-testid="stLayoutWrapper"]:has([data-testid="stBidiComponentIsolated"]) {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    div[data-testid="stElementContainer"]:has([data-testid="stBidiComponentIsolated"]) {
        display: flex !important;
        justify-content: center !important;
        align-items: flex-start !important;
        width: 100% !important;
        min-height: 620px !important;
        overflow: visible !important;
        margin-bottom: 0.5rem !important;
    }
    [data-testid="stBidiComponentIsolated"] {
        min-height: 620px !important;
        overflow: visible !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    div[data-testid="stCustomComponentV2"],
    div[data-testid="stCustomComponentV2"] > div {
        display: flex !important;
        justify-content: center !important;
        margin: 0.35rem auto 0.75rem !important;
        width: 100% !important;
        min-height: 620px !important;
        max-height: none !important;
        overflow: visible !important;
    }
    section.main .block-container {
        padding-bottom: 2.75rem !important;
    }
    </style>
    """
