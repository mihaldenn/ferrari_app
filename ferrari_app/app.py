import streamlit as st
import pandas as pd
from PIL import Image
import pdfkit
import io
import xlsxwriter

# CONFIGURAZIONE GENERALE
st.set_page_config(page_title="Stima Calcolo Preventivo", layout="wide")

# STILE
st.markdown("""
<style>
    /* Sfondo generale */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: white !important;
        color: black !important;
    }

    /* Testo base nero */
    h1, h2, h3, h4, h5, h6, p, span, label, input, select, textarea, div {
        color: black !important;
    }

    /* Riquadro riepilogo */
    .result-box {
        background-color: #878787 !important;
        border: 3px solid #FFD300 !important;
        padding: 20px !important;
        border-radius: 10px !important;
        font-size: 18px !important;
        margin-top: 20px !important;
        width: 80% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        text-align: center !important;
    }

    .result-box * {
        color: black !important;
    }

    /* 🔹 Pulsanti sotto — testo bianco, sfondo nero */
    .stDownloadButton button, .stButton button, button[kind="download"],
    [data-testid="baseButton-secondary"] {
        background-color: #000000 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        padding: 8px 16px !important;
        border-radius: 6px !important;
        cursor: pointer !important;
    }

    .stDownloadButton button:hover, .stButton button:hover, [data-testid="baseButton-secondary"]:hover {
        background-color: #222222 !important;
    }

    /* 🔹 Barre sopra tabella (intestazioni) — testo bianco, sfondo nero */
    [data-testid="stDataEditorGrid"] thead,
    [data-testid="stDataEditorGrid"] thead * {
        background-color: #000000 !important;
        color: white !important;
    }

    /* 🔹 Celle della tabella — testo nero, sfondo chiaro */
    [data-testid="stDataEditorGrid"] div[role="gridcell"] {
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

# LOGO E TITOLO
col1, col2, col3 = st.columns([5, 1, 1])
with col1:
    logo = Image.open("./ferrari_app/logo_ferrari.jpg")
    st.image(logo, width=150)

st.markdown("<h1 style='text-align: center; color: black;'>Stima Calcolo Preventivo - WebApp</h1>", unsafe_allow_html=True)
st.header("vecchia webapp - versione con python e css")
# DATI CLIENTE
st.header("Dati Cliente e Parametri Generali")

nome_cliente = st.text_input("Nome Cliente", value="Marco De Francesco")
superficie_pt = st.number_input("Superficie Piano Terra (mq)", value=125)
superficie_p1 = st.number_input("Superficie Piano Primo (mq)", value=125)
margine_errore = st.number_input("Margine di errore (%)", value=0.1)
costi_variabili = st.number_input("Costi Variabili (€)", value=1000)

st.write(f"**Superficie Totale:** {superficie_pt + superficie_p1} mq")
st.write(f"**Cliente selezionato:** {nome_cliente}")

# TABELLA PRODOTTI
st.header("Configura Prodotti e Costi")

prodotti = [
    "PAVIMENTO", "SOPRAELEVATO", "CONTROSOFFITTO", "CARTONGESSO DELTA 125/175",
    "MODULARI", "VETRO", "BAGNI", "ELETTRICO", "ARIA", "VMC", "ARREDI", "SOPPALCO"
]

data_iniziale = pd.DataFrame({
    "Prodotto": prodotti,
    "Costo/mq": [60, 110, 80, 150, 190, 230, 100, 190, 250, 250, 150, 600],
    "PT": [False] * 11 + [False],
    "P1": [False] * 11 + [None]
})

if not {"Stima PT", "Stima P1", "Stima Totale"}.issubset(data_iniziale.columns):
    data_iniziale["Stima PT"] = 0.0
    data_iniziale["Stima P1"] = 0.0
    data_iniziale["Stima Totale"] = 0.0

if "editor" not in st.session_state or not isinstance(st.session_state["editor"], list):
    st.session_state["editor"] = data_iniziale.to_dict(orient="records")

data_editable = pd.DataFrame(st.session_state["editor"])

if not data_editable.empty:
    st.data_editor(data_editable, disabled=["Prodotto"], height=460, hide_index=True)

# CALCOLO STIME
data_editable["Stima PT"] = data_editable.apply(
    lambda row: row["Costo/mq"] * superficie_pt if row["PT"] else 0.0, axis=1)
data_editable["Stima P1"] = data_editable.apply(
    lambda row: row["Costo/mq"] * superficie_p1 if row["P1"] else 0.0, axis=1)
data_editable["Stima Totale"] = data_editable["Stima PT"] + data_editable["Stima P1"]

# FUNZIONI DI DOWNLOAD
def scarica_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Preventivo", index=False)
    output.seek(0)
    return output

def scarica_pdf(df):
    html = df.to_html()
    pdf_file = pdfkit.from_string(html, False)
    return io.BytesIO(pdf_file)

# RIEPILOGO PREVENTIVO NEL RIQUADRO
if not data_editable.empty:
    totale = data_editable["Stima Totale"].sum()
    totale_con_margine = round(totale * (1 + margine_errore) + costi_variabili, 2)
    incidenza_pt = round(totale_con_margine / superficie_pt, 2) if superficie_pt else 0
    incidenza_p1 = round(totale_con_margine / superficie_p1, 2) if superficie_p1 else 0

    # RIQUADRO UNIFICATO
    st.markdown(f"""
    <div class="result-box">
        <h3>📊 Riepilogo Preventivo</h3>
        <p>💰 <b>Totale stimato:</b> €{totale}</p>
        <p>💰 <b>Totale con margine e costi variabili:</b> €{totale_con_margine}</p>
        <p>🏠 <b>Incidenza Piano Terra:</b> €{incidenza_pt} / mq</p>
        <p>🏠 <b>Incidenza Piano Primo:</b> €{incidenza_p1} / mq</p>
    </div>
    """, unsafe_allow_html=True)

    st.download_button("📥 Scarica Excel", data=scarica_excel(data_editable), file_name="preventivo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("📥 Scarica PDF", data=scarica_pdf(data_editable), file_name="preventivo.pdf", mime="application/pdf")
