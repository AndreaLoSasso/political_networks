#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 10:31:02 2024

@author: andrealosasso
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import networkx as nx
import plotly.graph_objs as go
import folium
from streamlit_folium import folium_static

# Aggiungere una barra laterale per la navigazione
st.sidebar.title("Navigazione")
page = st.sidebar.radio("Seleziona la pagina:", ["Pagina 1", "Pagina 2"])

# Barra in alto con due immagini e testo in maiuscolo (capitello)
# Impostiamo una larghezza fissa per le colonne per evitare sovrapposizioni
col1, col2 = st.columns([1, 1])  # Due colonne di dimensioni uguali

# Definisci la dimensione delle immagini
image_size = 150  # Puoi regolare la dimensione qui

# Prima immagine
with col1:
    st.image("https://github.com/AndreaLoSasso/political_networks/blob/main/d74eb321-6f68-4907-bfd3-01b8c3b791f0.png", width=700)


# Aggiungi del margine per separare le immagini dal testo
st.markdown("<br>", unsafe_allow_html=True)
 # Testo in maiuscolo
# Testo in maiuscolo


# Caricamento del file per la prima pagina
file_path_df = 'https://github.com/AndreaLoSasso/political_networks/blob/main/240729_Modified_Elenco_Circoscrizioni_Refer.csv'
df = pd.read_csv(file_path_df)

# Caricamento del file Excel per la seconda pagina
file_path_voti = 'https://github.com/AndreaLoSasso/political_networks/blob/main/Voti comunali Bari 2024.csv'
df_voti = pd.read_csv(file_path_voti)


### Contenuto della Prima Pagina ###
if page == "Pagina 1":
    st.title("Network Geografico e Mappe")

    # Seleziona l'ID della community da visualizzare nel grafo
    community_options = ['Community ID Coaliione 1', 'Community ID Coaliione 2', 'Community ID Coaliione 3']
    selected_community = st.selectbox("Seleziona Community ID per visualizzare nel grafo:", community_options)

    # Coordinate di Bari, Italia
    bari_latitude = 41.117143
    bari_longitude = 16.871871

    # Costruzione del grafo di rete
    def create_graph(df, selected_community):
        G = nx.Graph()

        # Aggiungi nodi con coordinate e attributi di comunità
        for i, row in df.iterrows():
            G.add_node(
                row['Ubicazione'],
                pos=(row['Longitude']/100, row['Latitude']/100),
                community=row[selected_community]
            )

        # Aggiungi connessioni (opzionale, qui sono illustrate connessioni semplici)
        for i in range(len(df) - 1):
            G.add_edge(df['Ubicazione'][i], df['Ubicazione'][i + 1])

        return G

    # Genera il layout del grafo
    G = create_graph(df, selected_community)
    pos = nx.get_node_attributes(G, 'pos')
    community_colors = nx.get_node_attributes(G, 'community')

    # Definisci una mappa di colori per le comunità
    color_map = px.colors.qualitative.Set1

    # Assegna i colori in base alla community
    unique_communities = list(set(community_colors.values()))
    color_dict = {community: color_map[i % len(color_map)] for i, community in enumerate(unique_communities)}
    node_colors = [color_dict[community_colors[node]] for node in G.nodes]

    # Crea il grafo Plotly
    def draw_network_graph(G, pos, node_colors):
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_x = []
        node_y = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale=color_map,
                color=node_colors,
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Community ID',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2))

        node_text = []
        for node in G.nodes():
            node_text.append(f'Ubicazione: {node}, Community: {community_colors[node]}')

        node_trace.text = node_text

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title='Geographical Network Display',
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=0, l=0, r=0, t=40),
                            xaxis=dict(showgrid=False, zeroline=False),
                            yaxis=dict(showgrid=False, zeroline=False))
                        )
        return fig

    # Visualizza il grafo di rete con nodi colorati
    fig = draw_network_graph(G, pos, node_colors)
    st.plotly_chart(fig)

    # Mappa 1: Visualizza media voti
    st.write("## Indice 1: Media Voti per Coalizione")

    # Seleziona la media voti da visualizzare
    voti_options = ['Media Voti Coal 1', 'Media Voti Coal 2', 'Media Voti Coal 3']
    selected_voti = st.selectbox("Seleziona Media Voti da visualizzare nella mappa:", voti_options)

    # Crea una mappa Folium per la media voti, centrata su Bari
    map_voti = folium.Map(location=[bari_latitude, bari_longitude], zoom_start=12)

    for _, row in df.iterrows():
        folium.CircleMarker(
            location=(row['Latitude']/100, row['Longitude']/100),
            radius=5,
            popup=f"{row['Ubicazione']}: {row[selected_voti]}",
            color='blue',
            fill=True,
            fill_opacity=0.6
        ).add_to(map_voti)

    # Visualizza la mappa
    folium_static(map_voti)

    # Mappa 2: Visualizza popolazione residente totale
    st.write("## Indice 2: Popolazione Residente Totale")

    # Crea una mappa Folium per la popolazione residente totale
    map_population = folium.Map(location=[bari_latitude, bari_longitude], zoom_start=12)

    for _, row in df.iterrows():
        folium.CircleMarker(
            location=(row['Latitude']/100, row['Longitude']/100),
            radius=5,
            popup=f"{row['Ubicazione']}: {row['Popolazione residente totale']}",
            color='green',
            fill=True,
            fill_opacity=0.6
        ).add_to(map_population)

    # Visualizza la mappa
    folium_static(map_population)


elif page == "Pagina 2":
    st.title("Analisi dei Voti per Coalizione")

    # Menu a tendina multi-selezione per selezionare più liste contemporaneamente
    liste_options = df_voti['Lista'].unique()
    selected_liste = st.multiselect("Seleziona le liste da analizzare:", liste_options)

    if selected_liste:
        # Filtra il dataframe per le liste selezionate
        df_selected = df_voti[df_voti['Lista'].isin(selected_liste)]

        # Ordina i candidati in base ai voti (dal meno votato al più votato)
        df_selected = df_selected.sort_values(by='Voti')

        # Aggiungi una colonna per l'ordinamento (asse X)
        df_selected['Ordine'] = range(1, len(df_selected) + 1)

        # Crea lo scatter plot con dimensioni maggiori
        fig_scatter = px.scatter(df_selected, x='Ordine', y='Voti', color='Lista', hover_data=['Candidato'],
                                 title="Scatter Plot: Candidati per Voti",
                                 labels={'Ordine': 'Posizione ordinata (dal meno votato al più votato)', 'Voti': 'Numero di voti'},
                                 template='plotly_white')

        # Modifica le dimensioni della figura
        fig_scatter.update_layout(width=800, height=600)  # Imposta larghezza e altezza

        # Visualizza lo scatter plot
        st.plotly_chart(fig_scatter)

        # Calcola il totale dei voti per le liste selezionate
        total_votes = df_selected['Voti'].sum()

        # Mappa colori per le liste
        color_map = {
            "AGORA'": "#FF6347",  # Rosso
            "BARI BENE COMUNE": "#4682B4",  # Blu
            "BARI CITTA' D'EUROPA": "#32CD32",  # Verde lime
            "BARI X FABIO ROMITO": "#FFD700",  # Giallo
            "CON LECCESE SINDACO": "#8A2BE2",  # Blu violaceo
            "DECARO PER BARI": "#FF4500",  # Arancione
            "EUROPA VERDE - VERDI": "#228B22",  # Verde scuro
            "FDI": "#B22222",  # Rosso scuro
            "FORZA ITALIA": "#0000FF",  # Blu
            "GENERAZIONE URBANA": "#DAA520",  # Giallo dorato
            "LAFORGIA SINDACO": "#8B4513",  # Marrone
            "LECCESE SINDACO": "#7B68EE",  # Blu pervinca
            "LIBERALI E RIFORMISTI - nPSI": "#D2691E",  # Cioccolato
            "M5S": "#00FF00",  # Verde
            "MARIO CONCA PER BARI": "#A52A2A",  # Marrone
            "NOI MODERATI": "#FF8C00",  # Arancione scuro
            "NOI PER BARI - ITALEXIT PER L'ITALIA PER SCIACOVELLI SINDACO": "#FFE4B5",  # Beige
            "NOI POPOLARI": "#9370DB",  # Viola chiaro
            "OLTRE MANGANO SINDACO": "#20B2AA",  # Verde acqua
            "PCI": "#FF1493",  # Rosa intenso
            "PD": "#000080",  # Blu navy
            "PENSIONATI E INVALIDI": "#7FFF00",  # Verde chiaro
            "PROGETTO BARI CON LECCESE": "#FFD700",  # Giallo
            "ROMITO SINDACO": "#DC143C",  # Rosso crudo
            "SCIACOVELLI SINDACO - CI PIACE!": "#ADFF2F",  # Verde giallastro
            "UDC - PRIMA L'ITALIA PER ROMITO SINDACO": "#778899"   # Grigio bluastro
        }
        
        # Genera una lista di colori per le liste selezionate
        colors = [color_map.get(lista, "#D3D3D3") for lista in selected_liste]  # Grigio di default se non trovato

        # Crea un nuovo dataframe per il pie chart con la frazione dei voti
        df_selected['Frazione'] = df_selected['Voti'] / df_selected['Voti'].sum()  # Calcola la frazione

        # Crea un diagramma a torta che mostra la distribuzione dei voti
        fig_pie = px.pie(df_selected, names='Lista', values='Frazione',
                         title="Distribuzione dei voti per lista selezionata",
                         labels={'Frazione': 'Frazione di voti'},
                         template='plotly_white',
                         color_discrete_sequence=colors)

        # Visualizza il diagramma a torta
        st.plotly_chart(fig_pie)
        
        # Mostra la riga informativa sui voti
        if len(selected_liste) == 1:
            # Se una sola lista è selezionata
            lista_selezionata = selected_liste[0]
            voti_ottenuti = df_selected['Voti'].sum()
            percentuale = (voti_ottenuti / df_voti['Voti'].sum()) * 100  # Percentuale sui voti totali
            st.write(f"La lista **{lista_selezionata}** ha ottenuto complessivamente **{voti_ottenuti}** voti. "
                     f"Essi equivalgono al **{percentuale:.2f}%** delle preferenze.")
        else:
            # Se più liste sono selezionate
            liste_selezionate = ", ".join(selected_liste)
            voti_ottenuti = df_selected['Voti'].sum()
            percentuale = (voti_ottenuti / df_voti['Voti'].sum()) * 100  # Percentuale sui voti totali
            st.write(f"Le liste **{liste_selezionate}** hanno ottenuto complessivamente **{voti_ottenuti}** voti. "
                     f"Questi voti equivalgono al **{percentuale:.2f}%** delle preferenze totali.")

        
    
# Barra in basso con due immagini e testo in maiuscolo (capitello)
st.markdown("<br>", unsafe_allow_html=True)  # Aggiungi uno spazio sopra la barra

# Imposta le colonne per le immagini
col1, col2 = st.columns([1, 1])  # Due colonne di dimensioni uguali

# Definisci la dimensione delle immagini
image_size = 150  # Puoi regolare la dimensione qui

# Seconda immagine
with col2:
    st.image("https://github.com/AndreaLoSasso/political_networks/blob/main/logo_4f1d3968fa43777fe3839415140eeef6_2x.png", width=image_size)

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
