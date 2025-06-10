import streamlit as st
import pandas as pd
from PIL import Image
import pdfkit
import io
import xlsxwriter

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
        </style>
        <div class="watermark">FERRARI</div>
    """, unsafe_allow_html=True)

stile_ferrari()

# ─────────────────────────────────────────────
# SEZIONE LOGO CENTRATO E TITOLO
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    logo = Image.open("./ferrari_app/logo_ferrari.jpg")
    st.image(logo, width=150)

st.title("Preventivo – FerrariContract")

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

data_iniziale = pd.DataFrame({
    "Prodotto": prodotti,
    "Costo/mq": [50.0] * len(prodotti),
    "PT": [False] * len(prodotti),
    "P1": [False] * len(prodotti),
    "Stima PT": [0.0] * len(prodotti),
    "Stima P1": [0.0] * len(prodotti),
    "Stima Totale": [0.0] * len(prodotti)
})

# 🔹 Permetti modifiche solo su alcune colonne
data_editable = st.data_editor(
    data_iniziale, disabled=["Prodotto", "Stima PT", "Stima P1", "Stima Totale"], key="editor"
)

# 🔹 Assicura che `st.session_state["editor"]` sia sempre un DataFrame valido
if "editor" not in st.session_state or not isinstance(st.session_state["editor"], pd.DataFrame):
   if "editor" not in st.session_state:
    st.session_state["editor"] = data_iniziale.copy()  # ✅ Ora è correttamente indentata!

# 🔹 Recupera i dati della sessione
data_raw = st.session_state["editor"]

try:
    data_editable = pd.DataFrame(data_raw) if isinstance(data_raw, list) else pd.DataFrame.from_dict(data_raw)
except ValueError:
    st.error("⚠️ Errore nella conversione dei dati!")
    data_editable = pd.DataFrame(columns=["Prodotto", "Costo/mq", "PT", "P1", "Stima PT", "Stima P1", "Stima Totale"])

# 🔹 Calcolo automatico delle stime
if set(["PT", "P1", "Costo/mq"]).issubset(set(data_editable.columns)):
    data_editable["Stima PT"] = data_editable.apply(
        lambda row: row["Costo/mq"] * superficie_pt if row["PT"] else 0.0, axis=1)

    data_editable["Stima P1"] = data_editable.apply(
        lambda row: row["Costo/mq"] * superficie_p1 if row["P1"] else 0.0, axis=1)

    data_editable["Stima Totale"] = data_editable["Stima PT"] + data_editable["Stima P1"]
else:
    st.error("⚠️ Errore: Mancano colonne necessarie nei dati!")

# 🔹 Aggiorna la sessione con i dati corretti
st.session_state["editor"] = data_editable.to_json()  # ✅ Ora Streamlit accetta i dati senza problemi

# ─────────────────────────────────────────────
# SEZIONE RISULTATI FINALI
st.header("📊 Riepilogo Preventivo")

if not data_editable.empty:
    totale = data_editable["Stima Totale"].sum()
    totale_con_margine = round(totale * (1 + margine_errore) + costi_variabili, 2)
    incidenza_pt = round(totale_con_margine / superficie_pt, 2) if superficie_pt else 0
    incidenza_p1 = round(totale_con_margine / superficie_p1, 2) if superficie_p1 else 0

    st.subheader("Totale Preventivo")
    st.write(f"💰 **Totale stimato:** €{totale}")
    st.write(f"💰 **Totale con margine e costi variabili:** €{totale_con_margine}")

    st.subheader("Incidenza al mq")
    st.write(f"🏠 **Piano Terra:** €{incidenza_pt} / mq")
    st.write(f"🏠 **Piano Primo:** €{incidenza_p1} / mq")

# ─────────────────────────────────────────────
# SEZIONE ESPORTAZIONE PDF & EXCEL
config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")

if st.button("💾 Scarica Preventivo in PDF"):
    html = f"""
    <h1>Preventivo - FerrariContract</h1>
    <p>Cliente: <strong>{nome_cliente}</strong></p>
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
