# Grafica di un file csv con una web-app streamlit
#
# L. Vanni, vers.0, 30/06/2026

# Librerie
import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px

# Funzioni ausiliarie
def converti_data(valore_stringa):
    # funzione per convertire la stringa con data-ora in np.datetime64
    s = valore_stringa.strip()
    # Se per caso la riga è vuota (es. test di NumPy), restituisce NaT
    if not s or s == '1':
        return np.datetime64('NaT')
    # Ricostruisce la stringa nel formato ISO accettato da NumPy
    data_iso = f"{s[6:10]}-{s[3:5]}-{s[0:2]}T{s[11:19]}.{s[20:]}"
    return np.datetime64(data_iso)

# Acquisizione dei dati in pandas dataframe
# l'oggetto file_caricato è un oggetto nativo streamlit per i file
file_caricato = st.file_uploader("Carica il file csv con i dati", type=["csv"])
if file_caricato is not None:
    dati = pd.read_csv(
        file_caricato,
        delimiter=',',
        skiprows=11,
        header=None,
        names=['Scan', 'Tempo', 'canale 110', 'Alarm 110', 'tensione', 'Alarm 120'],
        dtype={
            'Scan': np.int_,
            'canale 110': np.float64,
            'Alarm 110': np.bool_,
            'tensione': np.float64,
            'Alarm 120': np.bool_
        },
        converters={'Tempo': converti_data},
        encoding='utf-16'
    )
    dati['Tempo'] = pd.to_datetime(dati['Tempo']) # conversione del formato

    # Grafica dei dati
    fig = px.line(dati, x='Tempo', y='tensione', title='Tensione vs Tempo')
    fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig.update_layout(hovermode='x unified')  # mostra tutti i valori alla stessa x in un unico tooltip
    SOGLIA = -0.32
    fig.add_hline(
        y=SOGLIA,  # valore della soglia
        line_dash='dash',
        line_color='red',
        annotation_text='tensione di taglio',
        annotation_position='top left'
    )
    st.plotly_chart(fig, use_container_width=True)
