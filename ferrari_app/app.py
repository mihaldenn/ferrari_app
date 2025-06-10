import streamlit as st
import pandas as pd
from PIL import Image
import pdfkit
import io  # ✅ Import necessario per Excel
import xlsxwriter  # ✅ Import per l'export Excel

# ─────────────────────────────────────────────
# CONFIGURAZIONE GENERALE
st.set_page_config(page_title="Preventivo FerrariContract", layout="wide")

def stile_ferrari():
    st.markdown("""
        <style>
        html, body {
            background-color: #f2f2f2;
            color: #000000;
        }
        h1, h2, h3 {
            color: #000000;
            text-align: center;
        }
        .stButton>button {
            background-color: #f7c600;
            color: #000;
            border: none;
            font-weight: bold;
            border-radius: 5px;
            padding: 0.6em 1.2em;
        }
        .stDataFrame {
            border: 1px solid #ddd;
        }
        .watermark {
            position: fixed;
            top: 35%;
            left: 15%;
            font-size: 10em;
            color: #f7c600;
            opacity: 0.05;
            transform: rotate(-25deg);
            z-index: -1;
        }
        .logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 10px;
        }
        </style>
        <div class="watermark">FERRARI</div>
    """, unsafe_allow_html=True)

stile_ferrari()

# ─────────────────────────────────────────────
# SEZIONE LOGO CENTRATO E TITOLO

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    logo = Image.open("logo_ferrari.jpg")
    st.image(logo, width=150)


st.title("Preventivo – FerrariContract")

# ─────────────────────────────────────────────
# SEZIONE 1️⃣ – DATI CLIENTE
st.header("Dati Cliente e Parametri Generali")

nome_cliente = st.text_input("Nome Cliente", value="Mario Rossi")
superficie_pt = st.number_input("Superficie Piano Terra (mq)", value=125)
superficie_p1 = st.number_input("Superficie Piano Primo (mq)", value=125)
margine_errore = st.number_input("Margine di errore (%)", value=0.1)
costi_variabili = st.number_input("Costi Variabili (€)", value=1000)
superficie_totale = superficie_pt + superficie_p1

st.write(f"**Superficie Totale:** {superficie_totale} mq")
st.write(f"**Cliente selezionato:** {nome_cliente}")

# ─────────────────────────────────────────────
# SEZIONE 2️⃣ – TABELLA PRODOTTI
st.header("Configura Prodotti e Costi")

prodotti = [
    "PAVIMENTO", "SOPRAELEVATO", "CONTROSOFFITTO", "CARTONGESSO DELTA 125/175",
    "MODULARI", "VETRO", "BAGNI", "ELETTRICO", "ARIA", "VMC", "ARREDI", "SOPPALCO"
]

data_iniziale = pd.DataFrame({
    "Prodotto": prodotti,
    "Costo/mq": [50.0] * len(prodotti),
    "PT": [False] * len(prodotti),
    "P1": [False] * len(prodotti),
    "Stima PT": [0.0] * len(prodotti),
    "Stima P1": [0.0] * len(prodotti),
    "Stima Macro": [0.0] * len(prodotti)
})

data_editable = st.data_editor(data_iniziale, key="editor")

# 🔹 Calcolo automatico delle stime
data_editable["Stima PT"] = data_editable.apply(
    lambda row: row["Costo/mq"] * superficie_pt if row["PT"] else 0.0, axis=1)

data_editable["Stima P1"] = data_editable.apply(
    lambda row: row["Costo/mq"] * superficie_p1 if row["P1"] else 0.0, axis=1)

data_editable["Stima Macro"] = data_editable["Stima PT"] + data_editable["Stima P1"]

# 🔹 Salvataggio dei dati
st.session_state["data_tabella"] = data_editable
st.session_state["superficie_pt"] = superficie_pt
st.session_state["superficie_p1"] = superficie_p1
st.session_state["margine_errore"] = margine_errore
st.session_state["costi_variabili"] = costi_variabili

# ─────────────────────────────────────────────
# SEZIONE 3️⃣ – CALCOLI FINALI
st.header("Calcoli Finali")

data = st.session_state["data_tabella"]

if data["Stima Macro"].sum() == 0:
    st.warning("⚠️ Nessuna stima attiva: seleziona almeno un PT o P1 per vedere i risultati.")
    st.stop()

# 🔹 Calcolo totale con margine
totale = (data["Stima Macro"]).sum()
totale_con_margine = round(totale * (1 + margine_errore) + costi_variabili, 2)

incidenza_pt = round(totale_con_margine / superficie_pt, 2) if superficie_pt else 0
incidenza_p1 = round(totale_con_margine / superficie_p1, 2) if superficie_p1 else 0

# 🔹 Visualizzazione risultati
st.subheader("📊 Riepilogo")
st.write(f"**Totale stimato con margine e costi variabili:** €{totale_con_margine}")
st.write(f"**Incidenza al mq:**")
st.write(f"• Piano Terra → €{incidenza_pt} / mq")
st.write(f"• Piano Primo → €{incidenza_p1} / mq")

# ─────────────────────────────────────────────
# SEZIONE 4️⃣ – ESPORTAZIONE PDF & EXCEL
config = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")

if st.button("💾 Scarica Preventivo in PDF"):
    html = f"""
    <h1>Preventivo - FerrariContract</h1>
    <p>Cliente: <strong>{nome_cliente}</strong></p>
    <p>Totale stimato: <strong>€{totale_con_margine}</strong></p>
    <p>Incidenza PT: €{incidenza_pt} / mq</p>
    <p>Incidenza P1: €{incidenza_p1} / mq</p>
    """
    pdfkit.from_string(html, "preventivo.pdf", configuration=config)
    with open("preventivo.pdf", "rb") as f:
        st.download_button("⬇️ Scarica il PDF", f, file_name="preventivo_ferrari.pdf")

if st.button("📥 Esporta Excel"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        data_editable.to_excel(writer, index=False, sheet_name="Preventivo")
    buffer.seek(0)
    st.download_button("📥 Scarica Excel", buffer, file_name="preventivo_ferrari.xlsx")
