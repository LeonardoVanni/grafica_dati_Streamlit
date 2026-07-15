# Grafica di un file csv con una web-app streamlit
# Lo script è finalizzato a caricare la curva di scarica
# e a consentire all'utente di calcolare la durata della scarica attraverso
# l'esame del grafico
#
# L. Vanni, vers.0, 30/06/2026
# L. Vanni, vers.1, 14/07/2026, aggiunta di campi

# Librerie
import numpy as np
import streamlit as st
import pandas as pd
from datetime import timedelta as td
# import datetime
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

# Intestazione interfaccia
# print('inizio calcolo', datetime.datetime.now())
"""
Calcolo dei tempi di scarica Anodo Alluminio
============================
"""

# Acquisizione dei dati in pandas dataframe
# l'oggetto file_caricato è un oggetto nativo streamlit per i file
file_caricato = st.file_uploader("Carica il file csv con i dati", type=["csv"])
if file_caricato is not None:
    dati = pd.read_csv(
        file_caricato,
        delimiter=',',
        skiprows=12,
        header=None,
        names=['Scan', 'Tempo', 'Temperatura', 'Alarm 110','Caduta tensione','Alarm 114','Potenziale', 'Alarm 120'],
        #Scan, Time, 110 (C), Alarm 110, 114 (VDC), Alarm 114, 120 <tensione> (VDC), Alarm 120
        dtype={
            'Scan': np.int_,
            'canale 110': np.float64,
            'Alarm 110': np.bool_,
            'Caduta tensione': np.float64,
            'Alarm 114': np.bool_,
            'Potenziale': np.float64,
            'Alarm 120': np.bool_
        },
        converters={'Tempo': converti_data},
        encoding='utf-16'
    )
    dati['Tempo'] = pd.to_datetime(dati['Tempo']) # conversione del formato
    # print(dati)

    # Grafica dei dati
    fig = px.line(dati, x='Tempo', y=['Potenziale', 'Caduta tensione'], title='Potenziale vs Tempo')
    fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig.update_layout(hovermode='x unified')  # mostra tutti i valori alla stessa x in un unico tooltip
    SOGLIA = -1.55
    fig.add_hline(
        y=SOGLIA,  # valore della soglia
        line_dash='dash',
        line_color='red',
        annotation_text='tensione di taglio',
        annotation_position='top left'
    )
    st.plotly_chart(fig)
    # secondo grafico
    fig2 = px.line(dati, x='Tempo', y='Temperatura', title='Temperatura vs Tempo')
    fig2.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig2.update_yaxes(showspikes=True, spikemode='across', spikesnap='cursor', spikethickness=1)
    fig2.update_layout(hovermode='x unified')  # mostra tutti i valori alla stessa x in un unico tooltip
    st.plotly_chart(fig2)

# calcolo del tempo trascorso tra inizio e fine della scarica
inizio = st.text_input("Inserisci ora inizio scarica hh:mm:ss")
fine = st.text_input("Inserisci ora fine scarica:")
try:
    # estrazione di ora, min, sec
    L_i = [int(e) for e in inizio.split(':')]
    L_f = [int(e) for e in fine.split(':')]
    #creazione di oggetti timedelta di inizio e fine
    td_i = td(hours=L_i[0], minutes=L_i[1], seconds=L_i[2])
    td_f = td(hours=L_f[0], minutes=L_f[1], seconds=L_f[2])
    # calcolo del tempo trascorso
    Δt = td_f - td_i
    st.write(f"\nTra {inizio} e {fine} sono trascorsi {Δt}")
    st.write(f"pari a {round(Δt.total_seconds())} s \n")
except Exception as e:
    # Questo blocco cattura TUTTI gli errori standard
    print(f"Si è verificato un imprevisto! Errore: {e}")
    st.write("Sto attendendo un formato valido per gli orari.")
