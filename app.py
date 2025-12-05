import streamlit as st
import pandas as pd
import altair as alt

# Titolo dell'app
st.title("Bitcoin Price Interactive Visualization")

# Funzione per caricare e pulire i dati
@st.cache_data
def load_data():
    # Carica il CSV
    df = pd.read_csv("/Users/alessiabattistella/Desktop/btc1.csv")  # aggiorna percorso/nome file
    
    # Rimuove eventuali spazi nei nomi colonne
    df.columns = df.columns.str.strip()
    
    # Conversione della data
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date_only'] = df['Date'].dt.date  # solo la data per lo slider
    
    # Pulizia colonne numeriche con migliaia separate da virgola
    numeric_cols = ['Price', 'Open', 'High', 'Low']
    for col in numeric_cols:
        df[col] = df[col].astype(str).str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Pulizia Volume (Vol.) con K, M, B
    def parse_volume(x):
        if pd.isna(x):
            return None
        x = str(x).replace(',', '')  # rimuove eventuali virgole
        if 'K' in x:
            return float(x.replace('K','')) * 1_000
        elif 'M' in x:
            return float(x.replace('M','')) * 1_000_000
        elif 'B' in x:
            return float(x.replace('B','')) * 1_000_000_000
        else:
            return float(x)
    
    df['Vol.'] = df['Vol.'].apply(parse_volume)
    
    # Pulizia Change %
    df['Change %'] = df['Change %'].str.replace('%','', regex=False)
    df['Change %'] = pd.to_numeric(df['Change %'], errors='coerce')
    
    return df

df = load_data()

# Slider per selezionare l'intervallo di date
start_date = st.slider(
    "Select start date",
    min_value=df['Date_only'].min(),
    max_value=df['Date_only'].max(),
    value=df['Date_only'].min()
)

end_date = st.slider(
    "Select end date",
    min_value=df['Date_only'].min(),
    max_value=df['Date_only'].max(),
    value=df['Date_only'].max()
)

# Filtra i dati secondo le date selezionate
df_filtered = df[(df['Date_only'] >= start_date) & (df['Date_only'] <= end_date)]

# Anteprima dei dati filtrati
st.write("Filtered data preview:", df_filtered.head())

# Grafico interattivo del prezzo (Price)
line_chart = alt.Chart(df_filtered).mark_line(color='blue').encode(
    x='Date',
    y='Price',
    tooltip=['Date', 'Open', 'High', 'Low', 'Price', 'Vol.', 'Change %']
).interactive()

st.altair_chart(line_chart, use_container_width=True)

# Grafico del volume
volume_chart = alt.Chart(df_filtered).mark_bar(opacity=0.3, color='orange').encode(
    x='Date',
    y='Vol.',
    tooltip=['Date', 'Vol.']
)

st.altair_chart(volume_chart, use_container_width=True)
