import os
import sys 
import subprocess
import datetime

from dash import Dash
from dash.dependencies import Output, Input
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc 
from defer import return_value


import pandas as pd

import plotly.graph_objects as go

from bib.graph import graph_erstellen
from bib.info_db import add_info,check_for_edge,update_connection,add_file,is_file,get_path
from bib.osint_tool_db import create_panda_df,create_new_osint_modul_db,add_osint_modul,get_dir,get_osint_function,get_osint_tool_return_value,get_osint_tool_processed_value,types_of_return_values
from bib.projekt_anlegen import new_project


from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform

now = datetime.datetime.now()
zeit=f"{now.day}.{now.month}.{now.year} um {now.hour}:{now.minute}"

create_new_osint_modul_db()
osint_tools_df = create_panda_df().iloc[:,0]
dropdown_option = [tool for tool in osint_tools_df]
project ="test" 

new_project(project)
fig = graph_erstellen(project)

#passwörter auslesen
with open("./projects/test/passwortliste.txt") as f:
    passwords = f.read().splitlines()
password_text = html.P(",".join(passwords))

#app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app = DashProxy(external_stylesheets=[dbc.themes.BOOTSTRAP],prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])

app.layout = html.Div([
        html.H6("OSINT Framework"),
        html.Div([
        dcc.Dropdown(
            options=dropdown_option,
            id='dropdown_for_tools',
            #value=' ', #Startwert
            multi=False, #Mehrfachauswahl erst nach implementierung im Code möglich machen
            placeholder="Wähle ein Werkzeug aus", #Text im Auswahlmenü
        ),        
        dbc.Button("OSINT Werkzeuge hinzufügen", id="open", n_clicks=0),
        dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("OSINT Werkzeuge hinzufügen")),
                    dbc.ModalBody(
                        html.Div([
                            dbc.Input(id="input_osint_tool_name", placeholder="Gib hier den Namen des Werkzeugs ein, wie er später in der Liste stehen soll", type="text"),
                            html.Br(),
                            dbc.Input(id="input_osint_file", placeholder="Gib hier den Dateinamen des Werkzeug an, wie er im Ordner tools liegt", type="text"),
                            html.Br(),
                            dcc.Dropdown(
                                    options=[
                                        {'label': 'Information', 'value': 'information'},
                                        {'label': 'Dateien', 'value': 'file'},
                                            ],
                                    id="input_osint_processed_type",
                                    #value=' ', #Startwert
                                    multi=False, #Mehrfachauswahl ist möglich
                                    placeholder="Gib an, was das Programm verarbeitet." #Text im Auswahlmenü
                                ),
                            html.Br(),
                            dcc.Dropdown(
                                    options=[
                                        {'label': 'Liste', 'value': 'list'},
                                        {'label': 'Einzelwert', 'value': 'single_value'},
                                        {'label': 'JSON', 'value': 'json'},
                                        {'label': 'Dateien', 'value': 'files'},
                                            ],
                                    id="input_osint_return_type",
                                    #value=' ', #Startwert
                                    multi=False, #Mehrfachauswahl ist möglich
                                    placeholder="Welches Format gibt das Werkzeug zurück" #Text im Auswahlmenü
                                ),
                            #dbc.Input(id="input_osint_return_type", placeholder="Gib hier ob eine Liste oder ein einzelner Wert zurück gegeben wird", type="text"),
                            html.Br(),
                            html.Button(id='modul_abschicken', n_clicks=0, children='Submit'),
                            html.Br(),
                            html.Div(id="add_modul_answer"),
                                ]
                            )
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close", id="close", className="ms-auto", n_clicks=0
                        )
                    ),
                ],
                id="pop_up",
                is_open=False,
            ),
        
    ]),
    html.Div([
        dcc.Input(id='input_knoten', type='text', value='B'),
        html.Button("Wert abschicken", id='werte_abschicken', n_clicks=0),
        html.Div(id='textfeld_for_node'),
        html.Div(id='status'),
        html.Div([  html.Button("Modul ausführen",id='modul_ausfuehren', n_clicks=0),
                    html.Button("Text nach möglichen Passwörtern crawlen",id='start_crawl', n_clicks=0)]),
    ]),
    dcc.Graph(id='graph_id',figure=fig),
    #PopUp Fenster für dieOSINT Werkzeugeingabe
    
    html.Div([
        html.Div("hier stehen die Passwörter:"),
        password_text        
    ],
    id="textfeld_for_passwords"),
  
])





@app.callback(
    Output("pop_up", "is_open"),
    Input("open", "n_clicks"), 
    Input("close", "n_clicks"),
    State("pop_up", "is_open"),
)
def open_popup_tools(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

#OSINT Werkzeug hinzufügen
@app.callback(
    [Output("add_modul_answer", "children"), #hier hin wird answer zugewiesen
    Output("dropdown_for_tools","options")], #hierhin wird der panda_df zugewiesen
    Input("modul_abschicken", "n_clicks"),
    State("input_osint_tool_name","value"),
    State("input_osint_file","value"),
    State("input_osint_processed_type","value"),
    State("input_osint_return_type","value")
    )
def add_tool(n_clicks,name,werkzeug,processed_type,return_value):
    if n_clicks > 0: #muss drin stehen, ansonsten wird answer schon ausgeführt, bevor der Nutzer etwas klickt   
        answer = add_osint_modul(name,werkzeug,processed_type,return_value)
        panda_df = create_panda_df().iloc[:,0]
        return answer,panda_df #reihenfolge ist wichtig, erste Erg. wird dem ersten Output zugewiesen

#Knotenwert anzeigen
@app.callback(    
    Output('textfeld_for_node', 'children'),
    Input('graph_id', 'clickData')
    )
def display_click_data(clickData):
    researchvalue=clickData['points'][0]['text'] #ruft aus der json, die durch das klicken auf den Knoten erstellt wird, nur die text aus
    return  researchvalue


#knoten hinzufügen
@app.callback(
        [Output('status', 'children'),
        Output('graph_id','figure')],          
        Input('werte_abschicken', 'n_clicks'),
        State('input_knoten','value'))
def add_node(n_clicks,knoten):
    if n_clicks > 0:
        #now = datetime.datetime.now()
        #zeitpunkt=f"{now.day}.{now.month}.{now.year} um {now.hour}:{now.minute}"
        add_info(project, knoten, knoten, zeit, 5, "bisher mit keinem Werkzeug bearbeitet")
        fig = graph_erstellen(project)
        return ['Wert eingetragen' , fig]
 

#operation starten
@app.callback(
    [Output('graph_id','figure'),
    Output('status', 'children')],#2 outputs nötig, ansonsten keine dyn. Aktualisierung des Graphen
    [Input("dropdown_for_tools","value"), 
    Input('modul_ausfuehren', 'n_clicks')],
    [State('textfeld_for_node', 'children'),#State('graph_id', 'clickData')
    State("dropdown_for_tools","options")]
)
def run_research(dropdown_value,n_clicks,researchvalue,dropdown_option):
    def receive_list(output):
        #print(f"receive_list output {output}")
        #print(f"receive_list type(output) {type(output)}")
        chars="\'[]()\{\}\":;"
        for char in chars:
            output = output.replace(char,"")
        output = output.split(",")
        #erst nach dem erstellen der Liste die Leerzeichen entfernen, ansonsten wird alles zusammengeschrieben
        while(" " in output) : 
            output.remove(" ")

        return output
        #info_db.add_list_to_info_db(project,output,werkzeug[0],researchvalue)

        return 
   
    def receive_information(project,researchvalue,output,zeit, osint_tool_file_name,return_value):
        #print(f"receive_information aufgerufen")
        if return_value == 'list':
            #print(f"verarbeitet liste")
            output = receive_list(output)
            #print(f"output {output}")
            for information in output:
                #print(f"information ist {information}") #<- hier nochmal ansetzen!!!!! noch mal ein durchgang und sehen welche info hier ankommt bzw rauskommt
                check_edge = check_for_edge(project,researchvalue,information)
                if (check_edge[0]):
                    #wenn existiert wird die row id aus der SQLLite3 DB mit übergeben und die Kante aktualisiert
                    update_connection(project,check_edge[1],zeit,osint_tool_file_name)
                else: 
                    add_info(project,researchvalue,information,zeit, 1, osint_tool_file_name)
        else:
            check_edge = check_for_edge(project,researchvalue,output)
            #prüfen ob die Kante schon existiert [0] = der boolean Wert
            if (check_edge[0]):
                #wenn existiert wird die row id aus der SQLLite3 DB mit übergeben und die Kante aktualisiert
                update_connection(project,check_edge[1],zeit,osint_tool_file_name)
            else: 
                add_info(project,researchvalue,output,zeit, 1, osint_tool_file_name)
        
        return
    
    def receive_files(project,researchvalue,output,zeit, osint_tool_file_name,return_value):
        
        #if return_value == 'list':
        output = receive_list(output)
        
        for file_path in output:
            file_path=file_path.split("/")                
            file_name=file_path[-1]
            file_path="/".join(file_path[:-1])
            #print(f"file_path {file_path} file_name {file_name}")
            add_file(project,researchvalue,file_name,zeit, 1, osint_tool_file_name,str(file_path))
            """else:
            file_path=file_path.split("/")                
            file_name=file_path[-1]
            info_db.add_file(project,researchvalue,file_name,zeit, 1, osint_tool_file_name,str(file_path))
             """
        return


        #...
    def process_files(project,researchvalue,osint_tool_file_name):
        old_cwd =os.getcwd()
        #print("osint_tool_file_name {osint_tool_file_name}")
        #path = info_db.get_path(project,researchvalue)[0] #im pfad ist die Datei schon mit drin
        #file_name = path.split("/")[-1] #nur den Dateinamen extrahieren
        parameter_with_path = f"{old_cwd}/projects/{project}/files/{researchvalue}" 
        #print(f"parameter_with_path {parameter_with_path}")
        #werkzeuge brauchen den Pfad, um auf die Datei zugreifen zukönnen
        #project wird mit übergeben, falls weitere dateien zurück kommen, können die in den richtigen Projektordner gespeichert werden. 
        #Werden nur Informationen zurückgegeben, wird der Wert von project ignoriert!
        osint_tool_file_name = f"tools/{osint_tool_file_name}"
         #altes verzeichnis speichern

        #wenn es einen extra Ordner gibt, in dem die Datei liegt, dann wird das Verzeichnis dahin gewechselt, ansonsten werden viele Programme Probleme mit ihren Dateien bekommen
        if "/" in  osint_tool_file_name:            
            dir = get_dir(osint_tool_file_name)
            os.chdir(dir)
            #print(os.getcwd())
            osint_tool_file_name = osint_tool_file_name.split("/")[-1]
            #print(osint_tool_file_name)
        run = subprocess.run(['python3',osint_tool_file_name,parameter_with_path], capture_output=True, text=True)
        #run = subprocess.run([sys.executable,osint_tool_file_name,parameter_with_path], capture_output=True, text=True)
        os.chdir(old_cwd)
        #print(f"run.stout = {run.stdout}")
        return run.stdout

    if n_clicks > 0:
        fig = graph_erstellen(project)
        #rausfiltern vom label aus der dropdown auswahl
        print(f"dropdown_option {dropdown_option}")
        print(f"dropdown_option[0] {dropdown_option[0]}")
        werkzeug = [x for x in dropdown_option if x == dropdown_value]
        print(f"werkzeug {werkzeug}")
        
        osint_tool_file_name=get_osint_function(werkzeug[0])   
        return_value = get_osint_tool_return_value(werkzeug[0]) 
        processed_value = get_osint_tool_processed_value(werkzeug[0])  
        #return_class = osint_tool_db.get_osint_tool_return_class(werkzeug[0])
        
        if processed_value == "file":
            if is_file(project,researchvalue) == False:                
                return [fig, f" Fehler: {werkzeug[0]} verarbeitet nur Dateien"]
            #Datei wird verarbeitet
            result = process_files(project,researchvalue,osint_tool_file_name)

            if return_value in types_of_return_values:
                receive_information(project,researchvalue,result,zeit, osint_tool_file_name,return_value)
            elif return_value == "files":
                receive_files(project,researchvalue,result,zeit, osint_tool_file_name,return_value)
        #wenn eine Information verarbeitet werden soll
        if processed_value == "information": 
            if is_file(project,researchvalue):#hier ist ein Fehler
                return [fig, f" Fehler: {werkzeug[0]} verarbeitet nur Informationen"]

            result = subprocess.run(['python3',f"tools/{osint_tool_file_name}",researchvalue,project], capture_output=True, text=True).stdout
            #result = subprocess.run([sys.executable,f"tools/{osint_tool_file_name}",researchvalue,project], capture_output=True, text=True).stdout
            if return_value in types_of_return_values: #prüfen ob instagram crawler den falschen return class hat <- hier morgen weiter !
                receive_information(project,researchvalue,result,zeit, osint_tool_file_name,return_value)
            elif return_value == "files":
                receive_files(project,researchvalue,result,zeit, osint_tool_file_name,return_value)
        
        fig = graph_erstellen(project)
        
        n_clicks = 0
        return [fig, f"{werkzeug[0]} hat {researchvalue} verarbeitet"]

@app.callback(
    [Output('textfeld_for_passwords','children'),
    Output('status', 'children')],
    [Input("dropdown_for_tools","value"), 
    Input('start_crawl', 'n_clicks')],
    [State('textfeld_for_node', 'children'),
    State("dropdown_for_tools","options")]
)
def search_pw(dropdown_value,n_clicks,researchvalue,dropdown_option):    

    def process_files(project,researchvalue,osint_tool_file_name):
        old_cwd =os.getcwd()
        path = get_path(project,researchvalue)[0] #im pfad ist die Datei schon mit drin
        file_name = researchvalue
        #file_name = path.split("/")[-1] #nur den Dateinamen extrahieren
        parameter_with_path = f"{old_cwd}/projects/{project}/files/{file_name}"
        #werkzeuge brauchen den Pfad, um auf die Datei zugreifen zukönnen
        #project wird mit übergeben, falls weitere dateien zurück kommen, können die in den richtigen Projektordner gespeichert werden. 
        #Werden nur Informationen zurückgegeben, wird der Wert von project ignoriert!
        osint_tool_file_name = f"tools/{osint_tool_file_name}"
         #altes verzeichnis speichern
        print(f"parameter_with_path {parameter_with_path}")
        #wenn es einen extra Ordner gibt, in dem die Datei liegt, dann wird das Verzeichnis dahin gewechselt, ansonsten werden viele Programme Probleme mit ihren Dateien bekommen
        if "/" in  osint_tool_file_name:            
            dir = get_dir(osint_tool_file_name)
            os.chdir(dir)
            print(os.getcwd())
            osint_tool_file_name = osint_tool_file_name.split("/")[-1]
            print(osint_tool_file_name)
        run = subprocess.run(['python3',osint_tool_file_name,parameter_with_path], capture_output=True, text=True)
        #run = subprocess.run([sys.executable,osint_tool_file_name,parameter_with_path], capture_output=True, text=True)
        os.chdir(old_cwd)
        return run.stdout

    def receive_list(output):
        chars="\'[]()\{\}\":;"
        for char in chars:
            output = output.replace(char,"")
        output = output.split(",")
        #erst nach dem erstellen der Liste die Leerzeichen entfernen, ansonsten wird alles zusammengeschrieben
        while(" " in output) : 
            output.remove(" ")

        return output

    if n_clicks > 0:
        #rausfiltern vom label aus der dropdown auswahl

        werkzeug = [x for x in dropdown_option if x == dropdown_value]

        osint_tool_file_name=get_osint_function(werkzeug[0])  
        result = process_files(project,researchvalue,osint_tool_file_name)
        print(f"researchvalue {researchvalue}")
        print(f"result mach ner {result}")
        result = receive_list(result) #result kann vom rein logischen nur eine Liste, mir ist  kein NER Alog bekannt der nur Einzelwerte zurück gibt, max. Dateien
        print(f"result als liste {result}")
        passwortliste = open("./projects/test/passwortliste.txt", "w")
        for elem in result:        
            passwortliste.write(f"{elem}\n")
        passwortliste.close()

        with open("./projects/test/passwortliste.txt") as f:
            print("passwortliste ist offen")
            ausgabe = f.read().splitlines()

        ausgabe = ",".join(result)

        n_clicks=0
        return [ausgabe, f"{werkzeug[0]} hat {researchvalue} verarbeitet"]


if __name__ == '__main__':
    app.run_server(debug=False,host='127.0.0.1', port=42773) #Debug muss False, ansonsten wird alles 2x ausgeführt
