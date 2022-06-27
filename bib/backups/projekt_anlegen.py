import os
from bib.info_db import create_new_info_db
from pathlib import Path

def new_project(name):
    path = f"./projects/{name}"
    try:
        os.mkdir(path)
    except OSError:
        print(f"Creation of the directory in {path} failed")
    else:
        print(f"Successfully created the directory in {path}")

    

    file_path = Path(f"./projects/{name}/passwortliste.txt")
    print(f"file_path.is_file() {file_path.is_file()}")
    if not file_path.is_file():
        open(f"/projects/{name}/passwortliste.txt","w").close()

    create_new_info_db(name)

    print(f"Projekt {name} angelegt")

    return None