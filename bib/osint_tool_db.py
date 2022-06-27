import sqlite3
from matplotlib.pyplot import connect
import pandas as pd

connect_db =[] #PROBLEM: SQL vbdg bauen sich nciht ab!
types_of_return_values = ["list" , "single_value" , "json"]

def create_new_osint_modul_db():
    new_osint_connection = sqlite3.connect("tool_db.db")
    connect_db.append(new_osint_connection)
    cursor = new_osint_connection.cursor()
    #prüfen ob Tabelle schon existiert
    cursor.execute("""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND name='module';
        """)
    #print(cursor.fetchone()[0]) #nur einmal fetchone() aufrufen, ansonsten gibt es kein None mehr.
    if cursor.fetchone() is None:
        #print("lege module an")
        cursor.execute("""
            CREATE TABLE module
            (name TEXT,
            werkzeug BLOB,
            processed_value TEXT,
            return_value TEXT,
            return_class TEXT);
            """
            )
    cursor.close()
    new_osint_connection.close()

    return None

def add_osint_modul(name,werkzeug,processed_value,return_value):
    if return_value in types_of_return_values:
        return_class = "information"
    else:
        return_class = "file"
    add_osint_connection = sqlite3.connect("tool_db.db")
    connect_db.append(add_osint_connection)
    cursor = add_osint_connection.cursor()
    cursor.execute(""" 
            INSERT INTO module
            VALUES(?,?,?,?,?) 
            """,(name,werkzeug,processed_value,return_value,return_class)
            )
    add_osint_connection.commit()
    cursor.close()
    add_osint_connection.close()

    return f"{name} wurde als {werkzeug} dem Framework hinzugefügt."

def get_osint_tool_processed_value(name):
    get_osint_connection = sqlite3.connect("tool_db.db")
    connect_db.append(get_osint_connection)
    cursor = get_osint_connection.cursor()
    cursor.execute("""
        SELECT processed_value FROM module 
        WHERE name=?""", (name,)) 
    processed_value = cursor.fetchone()[0] 
    cursor.close()
    get_osint_connection.close()
    if (processed_value is None):
        return False
        
    return processed_value

def get_osint_tool_return_value(name):
    get_osint_connection = sqlite3.connect("tool_db.db")
    connect_db.append(get_osint_connection)
    cursor = get_osint_connection.cursor()
    cursor.execute("""
        SELECT return_value FROM module 
        WHERE name=?""", (name,)) 
    return_value = cursor.fetchone()[0] 
    cursor.close()
    get_osint_connection.close()
    if (return_value is None):
        return False
        
    return return_value

def get_osint_tool_return_class(name):
    get_osint_connection = sqlite3.connect("tool_db.db")
    connect_db.append(get_osint_connection)
    cursor = get_osint_connection.cursor()
    cursor.execute("""
        SELECT return_class FROM module 
        WHERE name=?""", (name,)) 
    return_class = cursor.fetchone()[0] 
    cursor.close()
    get_osint_connection.close()
    if (return_class is None):
        return False
        
    return return_class

def delete_osint_modul_db():
    delete_connection = sqlite3.connect("tool_db.db")
    connect_db.append(delete_connection)
    cursor = delete_connection.cursor()
    cursor.execute("DROP TABLE module")
    cursor.close()
    delete_connection.close()

    return None

""" Diese Funktion liest den gesamten Inhalt von der "module"-Tabelle auf und gibt sie als pandas Dataframe zurück.
"""
def create_panda_df():
    create_panda_connection = sqlite3.connect("tool_db.db")
    connect_db.append(create_panda_connection)
    dataframe = pd.read_sql_query("SELECT * FROM module", create_panda_connection)
    create_panda_connection.close()
    return dataframe


""" Diese Funktion bekommt den Namem eines OSINT-Werkzeuges und liefert den den Namen der entsprechenden Datei zurück.
    Die Abfrage erfolgt aus der "module" Tabelle, in der alle OSINT Werkzeuge samt Name und Dateiname gelistet sind.
"""
def get_osint_function(name):
    print(f"get_osint_function(name) {name} {type(name)}")
    get_function_connection = sqlite3.connect("tool_db.db")
    connect_db.append(get_function_connection)
    cursor = get_function_connection.cursor()
    cursor.execute("""SELECT werkzeug FROM module WHERE name=?""",(name,)) 
    function = cursor.fetchone()[0]
    cursor.close()
    get_function_connection.close()

    if (function is None):
        return False
    return function
 
def get_dir(path):
    path = path.split("/")
    path = path[:-1]
    path = "/".join(path)
    return path