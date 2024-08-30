from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

import pandas as pd 

app = FastAPI()

con = sqlite3.connect("library.db", check_same_thread=False)
con.row_factory = sqlite3.Row
cur = con.cursor()


## CLASES PARA HACER LLAMADOS
class autor(BaseModel):
    RUT:str
    NOMBRE:str
    FH_NACIMIENTO:str
    CIUDAD:str
    EMAIL:str

class libro(BaseModel):
    Titulo:str
    Anno:int
    Genero:str
    Paginas: int
    Rut_autor:str

@app.get('/listado_tot')
def listado_tot():
    cur.execute('SELECT * FROM Autores')
    autores = cur.fetchall()
    cur.execute('SELECT * FROM LIBROS')

    libs = cur.fetchall()
    lst_fnl = []
    for aut in autores:
        aut_aux = dict(aut)
        RUT = aut_aux["RUT"]
        
        aut_aux["libros"] = list(filter(lambda d: d['RUT_AUTOR'] == RUT, libs))
        lst_fnl.append(aut_aux)

    return lst_fnl

@app.put("/reg_autor") #NUEVO AUTOR
def reg_autor(n_autor: autor):
    quer = f"INSERT INTO Autores(RUT, NOMBRE, FH_NACIMIENTO, CIUDAD, EMAIL) Values('{n_autor.RUT}','{n_autor.NOMBRE}','{n_autor.FH_NACIMIENTO}','{n_autor.CIUDAD}','{n_autor.EMAIL}')"
    cur.execute(quer)
    con.commit()

    return {"Recibido": True}

@app.put("/reg_libro") #NUEVO LIBRO
def reg_libro(n_libro: libro):
    quer_autor = f"SELECT * FROM Autores WHERE RUT = '{n_libro.Rut_autor}'"
    cur.execute(quer_autor)
    auts = cur.fetchone()

    quer_libros = f"SELECT * FROM LIBROS WHERE RUT_AUTOR = '{n_libro.Rut_autor}'"
    cur.execute(quer_libros)
    libs = cur.fetchall()
    if(len(libs) < 10 and auts != None):
        quer = f"INSERT INTO Libros(TITULO, ANNIO_LANZAMIENTO, GENERO, PAGINAS, RUT_AUTOR) Values('{n_libro.Titulo}','{n_libro.Anno}','{n_libro.Genero}','{n_libro.Paginas}','{n_libro.Rut_autor}')"
        cur.execute(quer)
        con.commit()

        resp = True
        msj = "Incersión exitosa"

    if(len(libs) == 10):
        msj = "No es posible registrar el libro, se alcanzó el máximo permitido"
    if(auts == None):
        msj = "El autor no se encuentra registrado"
    resp = False
    return {"Recibido": resp, "msj": msj}