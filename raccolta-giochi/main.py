"""
Avvio locale dell'app Streamlit.

Per eseguire:
    streamlit run app.py

Per il deploy su Streamlit Community Cloud, imposta app.py come entry point.
"""

import subprocess
import sys


def main():
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)


if __name__ == "__main__":
    main()
