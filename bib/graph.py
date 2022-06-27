import pandas as pd
import networkx as nx
import sqlite3
import plotly.graph_objects as go

from bib.info_db import has_data

def graph_erstellen(project):
    layout = dict(plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(t=10, b=10, l=10, r=10, pad=0),
                xaxis=dict(linecolor='black',
                            showgrid=False,
                            showticklabels=False,
                            mirror=True),
                yaxis=dict(linecolor='black',
                            showgrid=False,
                            showticklabels=False,
                            mirror=True))

    connection = sqlite3.connect(f"projects/{project}/database.db")
    if has_data(project)==False:
        print("erstelle leere Figure")
        return go.Figure(layout=layout)
    #sql Datenbank in panda Dataframe umwandeln
    print("erzeuge Graph")
    dataframe = pd.read_sql_query("SELECT * FROM graph", connection)
    connection.close()
    #Graph in networkx erzeugen
    graph=nx.from_pandas_edgelist(dataframe,source='knoten', target='name') 
    nx.draw(graph)
    edge_x = []
    edge_y = []
    pos = nx.spring_layout(graph)

    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(color='black', width=1),
        hoverinfo='none',
        showlegend=False,
        mode='lines'
        )

    node_x=[]
    node_y=[]
    meta=[]
    werkzeug=[]

    for node in graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        text=dataframe['knoten'] #als Text im Knoten vielleicht die ID nehmen

    #Metaausgabe erstellen, wichtig, das die Werkzeuge drin sind 
    for index,row in dataframe.iterrows():
        meta.append(f"{row['name']},{row['werkzeug']},{row['zeitpunkt']}")
        werkzeug.append(f"{row['werkzeug']},<br> zuletzt bearbeitet am {row['zeitpunkt']}")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        text=text, #als text wird auf die Spalte 'gewicht' aus dem Dataframe df genommen 
        meta=meta,
        mode='markers+text',
        showlegend=False,
        hovertemplate=werkzeug, #noch zurecht schneiden, für die Info welchen Werkzeugen es schon bearbeitet wurde
        hoverinfo="text",
        marker=dict(
            color='pink',
            size=50,
            line=dict(color='black', width=1))
        )
    #für die Kanten
    

    fig = go.Figure(data=[edge_trace,node_trace], layout=layout)  
    fig.update_layout(clickmode='event+select')
    return fig