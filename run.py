import os
import sys
import streamlit
print(sys.path)
from streamlit.web import cli as stcli



if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.argv = [
        "streamlit",
        "run",
        "src/trader_journal.py",
        "--server.port=8501",
        "--global.developmentMode=false",
        "--theme.base=light",
        "--theme.primaryColor=#10475a",
        "--theme.secondaryBackgroundColor=#f2f9f2"
    ]
    sys.exit(stcli.main())