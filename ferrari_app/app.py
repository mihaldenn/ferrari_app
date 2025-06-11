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
            background-color: white !important;
            color: black !important;
        }
        .result-box {
            border: 3px solid #FFD300;
            background-color: white;
            color: black !important;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 5px 5px 10px rgba(0,0,0,0.1);
            text-align: center;
            font-size: 18px;
            margin-top: 20px;
        }
        .stDataEditor {
            background-color: white !important;
            color: black !important;
        }
        th, td {
            border: 1px solid #DDD !important;
            padding: 8px !important;
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

# 🔹 Definizione dati iniziali con checkbox unificata per SOPPALCO
data_iniziale = pd.DataFrame({
    "Prodotto": prodotti,
    "Costo/mq": [60, 110, 80, 150, 190, 230, 100, 190, 250, 250, 150, 600],
    "PT": [False] * 11 + [True],  # 🔹 SOPPALCO ha solo una checkbox
    "P1": [False] * 11 + [""]  # 🔹 La seconda colonna è vuota per SOPPALCO
})

# 🔹 Stile per evidenziare la riga di SOPPALCO
def style_soppalco(df):
    styles = pd.DataFrame("", index=df.index, columns=df.columns)
    styles.iloc[-1, -2] = "background-color: #FFD300; text-align: center; font-weight: bold;"
    styles.iloc[-1, -1] = "visibility: hidden;"  # 🔹 Nasconde la seconda checkbox per SOPPALCO
    return styles

data_editable = data_iniziale.style.apply(style_soppalco, axis=None)

# 🔹 Mostra la tabella con checkbox corrette
if not data_editable.empty:
    data_editable = st.data_editor(data_editable, key="tabella_soppalco")

else:
    st.warning("⚠️ Nessun dato disponibile per la tabella!")

# ─────────────────────────────────────────────
# SEZIONE RISULTATI FINALI
st.header("📊 Riepilogo Preventivo")

if not data_editable.empty:
    totale = data_editable["Costo/mq"].sum()
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

st.download_button("📥 Scarica Excel", data=scarica_excel(data_editable), file_name="preventivo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
st.download_button("📥 Scarica PDF", data=scarica_pdf(data_editable), file_name="preventivo.pdf", mime="application/pdf")
