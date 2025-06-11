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
        html, body {
    background-color: #f2f2f2;  /* Grigio chiaro */
    color: #333333;  /* Testo in grigio scuro */
}

        h1, h2, h3 {
           color: white;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

stile_ferrari()

# ─────────────────────────────────────────────
# SEZIONE LOGO CENTRATO E TITOLO
col1, col2, col3 = st.columns([5, 1, 1])
with col1:
    logo = Image.open("./ferrari_app/logo_ferrari.jpg")
    st.image(logo, width=150)

st.markdown(
    "<h1 style='text-align: center; color: black;'>Stima Calcolo Preventivo - [BETA]</h1>",
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

# 🔹 Definizione dati iniziali
data_iniziale = pd.DataFrame({
    "Prodotto": [
        "PAVIMENTO", "SOPRAELEVATO", "CONTROSOFFITTO", "CARTONGESSO DELTA 125/175",
        "MODULARI", "VETRO", "BAGNI", "ELETTRICO", "ARIA", "VMC", "ARREDI", "SOPPALCO"
    ],
    "Costo/mq": [60, 110, 80, 150, 190, 230, 100, 190, 250, 250, 150, 600],
    "PT/P1": [False] * 11 + [False],
    "Stima PT": [0.0] * len(prodotti),
    "Stima P1": [0.0] * len(prodotti),
    "Stima Totale": [0.0] * len(prodotti)
})

# 🔹 Inizializza la sessione con dati validi
if "editor" not in st.session_state or not isinstance(st.session_state["editor"], list) or not st.session_state["editor"]:
    st.session_state["editor"] = data_iniziale.to_dict(orient="records")

# 🔹 Assicura che `data_editable` sia sempre un DataFrame corretto
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
    disabled=["Prodotto", "Stima PT", "Stima P1", "Stima Totale"],
    height=460  # 🔹 Imposta una altezza maggiore per evitare lo scroll
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
