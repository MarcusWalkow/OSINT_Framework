import sqlite3
import datetime

from matplotlib.pyplot import connect


def check_existance(project):
    connection = sqlite3.connect(f"projects/{project}/database.db")
    cursor = connection.cursor()
    #prüfen ob Tabelle schon existiert
    cursor.execute("""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND name='graph';
        """)
    
    if cursor.fetchone() is None:
        connection.close()
        return False
    else: 
        connection.close()
        return True
    
def has_data(project):
    connection = sqlite3.connect(f"projects/{project}/database.db")
    cursor = connection.cursor()
    #prüfen ob Tabelle schon existiert
    cursor.execute("""
        SELECT *
        FROM graph;
        """)
    data = cursor.fetchall()
    connection.close()
    if len(data)==0:
        return False
    else:
        return True

#prüft ob eine Tabelle graph schon exisitiert
#wenn sie nicht exisitert, wird sie neu angelegt
def create_new_info_db(project):    
    '''
    #prüfen ob Tabelle schon existiert
    cursor.execute("""
        SELECT child 
        FROM sqlite_master 
        WHERE type='table' AND child='graph';
        """)
    if cursor.fetchone() is None:
        '''
    #prüfen ob Tabelle schon existiert
    if check_existance(project)==False:
        connection = sqlite3.connect(f"projects/{project}/database.db")
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE graph(
                parent TEXT,
                child TEXT, 
                zeitpunkt TEXT, 
                gewicht INTEGER, 
                werkzeug TEXT,
                pfad TEXT 
                )
            """)
        connection.close()
        #das später rauslöschen
        #create_example_info_data(project)

    return None



def add_info(project,parent, child, zeitpunkt, gewicht, werkzeug):
    connection = sqlite3.connect(f"projects/{project}/database.db")
    cursor = connection.cursor()
    sql = """
            INSERT INTO graph(
                parent,
                child, 
                zeitpunkt, 
                gewicht, 
                werkzeug
                )
            VALUES(?,?,?,?,?) 
            """
    werte=(child, parent, zeitpunkt, gewicht, werkzeug)
    cursor.execute(sql, werte)
    connection.commit()
    connection.close()

    return None

def add_file(project,parent, child, zeitpunkt, gewicht, werkzeug, pfad):
    connection = sqlite3.connect(f"projects/{project}/database.db")
    cursor = connection.cursor()
    sql = """
            INSERT INTO graph(
                parent,
                child, 
                zeitpunkt, 
                gewicht, 
                werkzeug,
                pfad
                )
            VALUES(?,?,?,?,?,?) 
            """
    werte=(child, parent, zeitpunkt, gewicht, werkzeug, pfad)
    cursor.execute(sql, werte)
    connection.commit()
    connection.close()

    return None

def is_file(project,parent):
    connection = sqlite3.connect(f"projects/{project}/database.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT pfad
        FROM graph
        WHERE parent = ?;
        """,(parent,))
    result = cursor.fetchall()
    
    if result[0][0]!= None:
        cursor.close()
        connection.close()
        return True
    cursor.close()
    connection.close()
    return False

def get_path(project,parent):
    connection = sqlite3.connect(f"projects/{project}/database.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT pfad
        FROM graph
        WHERE parent=?
        """,(parent,))
    pfad= cursor.fetchall()
    print(f"pfad: {pfad}")
    cursor.close()
    connection.close()
    return pfad[0]


def delete_info_db(project):
    connection = sqlite3.connect(f"projects/{project}/database.db")
    cursor = connection.cursor()
    cursor.execute("DROP TABLE graph")
    connection.close()

    return None

def del_entry(project,parent,child):
    connection = sqlite3.connect(f"projects/{project}/database.db")
    cursor = connection.cursor()
    cursor.execute("""
        DELETE FROM table
        WHERE parent = ? AND child = ?;""",
        (parent,child)
    )
    cursor.close()
    connection.close()
    return f"parent {child} wurde gelöscht"



def create_example_info_data(project):
    now = datetime.datetime.now()
    zeit=f"{now.day}.{now.month}.{now.year} um {now.hour}:{now.minute}"

    connection = sqlite3.connect(f"projects/{project}/database.db")

    bspDatensatz =[
    ("A","B",zeit,5,"bisher verwendete Werkzeuge mit Zeitpunkt der Nutzung"),
    ("A","D",zeit,11,"bisher verwendete Werkzeuge mit Zeitpunkt der Nutzung"),
    ("B","C",zeit,25,"bisher verwendete Werkzeuge mit Zeitpunkt der Nutzung"),
    ("B","E",zeit,10,"bisher verwendete Werkzeuge mit Zeitpunkt der Nutzung")]

    [add_info(project,bspDaten[0],bspDaten[1],bspDaten[2],bspDaten[3],bspDaten[4]) for bspDaten in bspDatensatz]
    
    connection.close()
    return None

""" abfragen einer Kante (Verbindung) 
node ist der recherchierte parent
child ist der gefundene Wert
"""
def check_for_edge(project,node,child):
    connection = sqlite3.connect(f"projects/{project}/database.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT rowid FROM graph 
        WHERE parent=? and child=?""", (node,child)) 
    #durch das , hinter child ist es ein Tuple, das nötig für die Abfrage ist, alternativ ginge auch [child]
    id = cursor.fetchone()
    cursor.close()
    connection.close()
    if (id is None):
        return False, None
    return True, id[0]

def update_connection(project,row_id,new_zeitpunkt,new_werkzeug):
    connection = sqlite3.connect(f"projects/{project}/database.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT gewicht,   
               werkzeug 
        FROM graph 
        WHERE rowid=?""", (row_id,)) 
    gewicht,werkzeug = cursor.fetchone() ##prüfen ob so auf fetchall zugegriffen werden kann
    gewicht += 1
    werkzeug += f"{new_werkzeug} am {new_zeitpunkt} verwendet"
    werte = (new_zeitpunkt,gewicht,werkzeug,row_id)
    sql="""
       UPDATE graph
       SET zeitpunkt = ?,
           gewicht =  ?,
           werkzeug = ?
       WHERE rowid = ?"""   
    cursor.execute(sql,werte)
    connection.commit()
    connection.close()
    return None


def add_list_to_info_db(project,list,osint_tool,researchvalue):
    now = datetime.datetime.now()
    zeit=f"{now.day}.{now.month}.{now.year} um {now.hour}:{now.minute}"
    for found_data in list:
        check_edge = check_for_edge(project,researchvalue,found_data)
        #prüfen ob die Kante schon existiert [0] = der boolean Wert
        if (check_edge[0]):
            #wenn existiert wird die row id aus der SQLLite3 DB mit übergeben und die Kante aktualisiert
            update_connection(project,check_edge[1],zeit,osint_tool)
        else: 
            add_info(project,researchvalue,found_data,zeit, 1, osint_tool)

    return None

        
