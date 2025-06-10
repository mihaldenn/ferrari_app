import pandas as pd

# Carica il file Excel
file_path = "ferrari_app.xlsx"  # Cambia con il nome corretto
excel_data = pd.ExcelFile(file_path)

# Leggi il foglio specifico (inserisci il nome corretto)
sheet_name = "dati"  # Cambia con il nome del foglio che contiene le tabelle
df = pd.read_excel(excel_data, sheet_name=sheet_name)

# Mostra le prime righe per verificare il contenuto
print(df.head())

