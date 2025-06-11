import streamlit as st
import pandas as pd
from PIL import Image
import pdfkit
import io
import xlsxwriter

# ─────────────────────────────────────────────
# CONFIGURAZIONE GENERALE
st.set_page_config(page_title="Stima Calcolo Preventivo", layout="wide")

def stile_ferrari():
    st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #101012 !important;
        }
        .result-box {
            width: 100% !important;
            min-height: 250px;
            border: 3px solid #FFD300;
            background-color: #5c5c5c;
            color: black;
            padding: 200px;
            border-radius: 10px;
            box-shadow: 5px 5px 10px rgba(0,0,0,0.1);
            text-align: center;
            font-size: 18px;
            margin-top: 20px;
        }
        tr:nth-child(12) td:nth-child(4) {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

stile_ferrari()

# ─────────────────────────────────────────────
# SEZIONE LOGO E TITOLO
col1, col2, col3 = st.columns([5, 1, 1])
with col1:
    logo = Image.open("./ferrari_app/logo_ferrari.jpg")
    st.image(logo, width=150)

st.markdown(
    "<h1 style='text-align: center; color: white;'>Stima Calcolo Preventivo - [BETA]</h1>",
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# SEZIONE DATI CLIENTE
st.header("Dati Cliente e Parametri Generali")

nome_cliente = st.text_input("Nome Cliente", value="Marco De Francesco")
superficie_pt = st.number_input("Superficie Piano Terra (mq)", value=125)
superficie_p1 = st.number_input("Superficie Piano Primo (mq)", value=125)
margine_errore = st.number_input("Margine di errore (%)", value=0.1)
costi_variabili = st.number_input("Costi Variabili (€)", value=1000)

st.write(f"**Superficie Totale:** {superficie_pt + superficie_p1} mq")
st.write(f"**Cliente selezionato:** {nome_cliente}")

# ─────────────────────────────────────────────
# SEZIONE TABELLA PRODOTTI
st.header("Configura Prodotti e Costi")

prodotti = [
    "PAVIMENTO", "SOPRAELEVATO", "CONTROSOFFITTO", "CARTONGESSO DELTA 125/175",
    "MODULARI", "VETRO", "BAGNI", "ELETTRICO", "ARIA", "VMC", "ARREDI", "SOPPALCO"
]

# 🔹 Definizione dati iniziali con checkbox unificata per SOPPALCO
data_iniziale = pd.DataFrame({
    "Prodotto": prodotti,
    "Costo/mq": [60, 110, 80, 150, 190, 230, 100, 190, 250, 250, 150, 600],
    "PT": [False] * 11 + [False],  # ✅ Solo SOPPALCO ha una checkbox attiva
    "P1": [False] * 11 + [None]  # ✅ La colonna P1 è vuota per SOPPALCO
})

# 🔹 Inizializza la sessione con dati validi
if "editor" not in st.session_state or not isinstance(st.session_state["editor"], list) or not st.session_state["editor"]:
    st.session_state["editor"] = data_iniziale.to_dict(orient="records")

if isinstance(st.session_state["editor"], list) and len(st.session_state["editor"]) > 0:
    data_editable = pd.DataFrame(st.session_state["editor"])
else:
    data_editable = pd.DataFrame(data_iniziale)

# 🔹 Mostra la tabella con dati modificabili 
if not data_editable.empty:
    data_editable = st.data_editor(
        data_editable, 
        disabled=["Prodotto"],
        height=460,
        hide_index=True
    )
else:
    st.warning("⚠️ Nessun dato disponibile per la tabella!")

# 🔹 Calcolo automatico delle stime
if set(["PT", "P1", "Costo/mq"]).issubset(set(data_editable.columns)):
    data_editable["Stima PT"] = data_editable.apply(
        lambda row: row["Costo/mq"] * superficie_pt if row["PT"] else 0.0, axis=1)

    data_editable["Stima P1"] = data_editable.apply(
        lambda row: row["Costo/mq"] * superficie_p1 if row["P1"] else 0.0, axis=1)

    data_editable["Stima Totale"] = data_editable["Stima PT"] + data_editable["Stima P1"]

# ─────────────────────────────────────────────
# SEZIONE RISULTATI FINALI
st.markdown("""
    <div class="result-box">
        <h2>📊 Riepilogo Preventivo</h2>
""", unsafe_allow_html=True)

if not data_editable.empty:
    totale = data_editable["Stima Totale"].sum()
    totale_con_margine = round((totale * (1 + margine_errore) + costi_variabili), 2)
    incidenza_pt = round(totale_con_margine / superficie_pt, 2) if superficie_pt else 0
    incidenza_p1 = round(totale_con_margine / superficie_p1, 2) if superficie_p1 else 0

    st.markdown(f"<h3>Totale Preventivo</h3>", unsafe_allow_html=True)
    st.markdown(f"<p>💰 <b>Totale stimato:</b> €{totale}</p>", unsafe_allow_html=True)
    st.markdown(f"<p>💰 <b>Totale con margine e costi variabili:</b> €{totale_con_margine}</p>", unsafe_allow_html=True)

    st.markdown(f"<h3>Incidenza al mq</h3>", unsafe_allow_html=True)
    st.markdown(f"<p>🏠 <b>Piano Terra:</b> €{incidenza_pt} / mq</p>", unsafe_allow_html=True)
    st.markdown(f"<p>🏠 <b>Piano Primo:</b> €{incidenza_p1} / mq</p>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
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

# 🔹 Pulsante per scaricare Excel
excel_file = scarica_excel(data_editable)
st.download_button(
    label="📥 Scarica Excel",
    data=excel_file,
    file_name="preventivo.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# 🔹 Pulsante per scaricare PDF
pdf_file = scarica_pdf(data_editable)
st.download_button(
    label="📥 Scarica PDF",
    data=pdf_file,
    file_name="preventivo.pdf",
    mime="application/pdf"
)
