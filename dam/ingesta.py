"""De una carpeta de archivos a un plan de carga: qué va a qué campo de qué ficha, y qué no entra.

Tres pasos después de leer el nombre:

1. **Dónde vive el identificador.** Se busca en el catálogo del PIM: modelo, variante o tema.
   Por la forma del nombre no se puede saber si ORION es un modelo o una campaña; por eso se
   consulta, y si aparece en dos tablas se rechaza en vez de elegir una.
2. **Si el código tiene campo en esa tabla.** Si la variante no tiene el campo (una foto de
   ambiente, un vídeo), el archivo sube al modelo de esa variante: es el mismo producto y la foto
   vale para todos sus colores. Un packshot en un tema no tiene sitio y se rechaza.
3. **Si dos archivos van al mismo hueco** (misma ficha, campo y serie). Si uno es un nombre
   heredado y el otro sigue la fórmula, gana el nuevo. Si no, se rechazan los dos: elegir entre
   dos fotos es una decisión de quien las ha hecho.

`aplicar` es la frontera con el PIM: recibe el plan y sube lo que se puede cargar. Por defecto
simula.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from dam.nomenclatura import CAMPOS, CODIGOS
from dam.parser import Rechazo, leer

NO_EXISTE = "identificador que no está en el PIM"
DOS_TABLAS = "identificador en dos tablas"
SIN_CAMPO = "código sin campo en esa tabla"
SUSTITUIDO = "lo sustituye un nombre nuevo"
CHOQUE = "dos archivos para el mismo hueco"

COLUMNAS = ["archivo", "estado", "motivo", "tabla", "registro", "campo", "serie", "medio", "tipo",
            "contexto", "heredado", "nota"]
AL_MODELO = "sube al modelo de la variante"


@dataclass
class Catalogo:
    """Lo que ya existe en el PIM: modelos, variantes (con su modelo) y temas de marketing."""
    modelos: set[str]
    variantes: dict[str, str]
    temas: set[str]

    def tablas(self, identificador: str) -> list[str]:
        i = identificador.upper()
        return [t for t, esta in (("modelo", i in self.modelos), ("variante", i in self.variantes),
                                  ("tema", i in self.temas)) if esta]


def _fila(archivo: str, **kw) -> dict:
    return {c: kw.get(c) for c in COLUMNAS} | {"archivo": archivo}


def planificar(archivos: list[str], catalogo: Catalogo) -> pd.DataFrame:
    filas = []
    for archivo in archivos:
        a = leer(archivo)
        if isinstance(a, Rechazo):
            filas.append(_fila(archivo, estado="rechazado", motivo=a.motivo))
            continue
        tablas = catalogo.tablas(a.identificador)
        medio, tipo, contexto = CODIGOS[a.codigo]
        base = {"serie": a.serie, "medio": medio, "tipo": tipo, "contexto": contexto,
                "heredado": a.heredado, "registro": a.identificador.upper()}
        if not tablas:
            filas.append(_fila(archivo, estado="rechazado", motivo=NO_EXISTE, **base))
            continue
        if len(tablas) > 1:
            filas.append(_fila(archivo, estado="rechazado", motivo=DOS_TABLAS, **base))
            continue
        tabla = tablas[0]
        campo = CAMPOS[tabla].get(a.codigo)
        if campo is None and tabla == "variante":
            modelo = catalogo.variantes[base["registro"]]
            base |= {"registro": modelo, "nota": AL_MODELO}
            tabla, campo = "modelo", CAMPOS["modelo"].get(a.codigo)
        if campo is None:
            filas.append(_fila(archivo, estado="rechazado", motivo=SIN_CAMPO, tabla=tabla,
                               **base))
            continue
        filas.append(_fila(archivo, estado="cargar", tabla=tabla, campo=campo, **base))

    plan = pd.DataFrame(filas, columns=COLUMNAS)
    return _resolver_choques(plan)


def _resolver_choques(plan: pd.DataFrame) -> pd.DataFrame:
    hueco = ["tabla", "registro", "campo", "serie"]
    cargar = plan["estado"] == "cargar"
    for _, g in plan[cargar].groupby(hueco):
        if len(g) == 1:
            continue
        nuevos = g[~g["heredado"].astype(bool)]
        if len(nuevos) == 1:
            perdedores, motivo = g.index.difference(nuevos.index), SUSTITUIDO
        else:
            perdedores, motivo = g.index, CHOQUE
        plan.loc[perdedores, ["estado", "motivo"]] = ["rechazado", motivo]
    return plan


@dataclass
class PIMSimulado:
    """Lo mínimo que haría falta de la API del PIM: subir un archivo a un campo de una ficha."""
    fichas: dict[tuple[str, str, str], dict[str, str]] = field(default_factory=dict)

    def subir(self, tabla: str, registro: str, campo: str, serie: str, archivo: str) -> None:
        self.fichas.setdefault((tabla, registro, campo), {})[serie] = archivo


def aplicar(plan: pd.DataFrame, pim: PIMSimulado, simular: bool = True) -> int:
    """Sube al PIM lo que el plan marca para cargar, en orden de serie. Devuelve cuántos."""
    a_cargar = plan[plan["estado"] == "cargar"].sort_values(["tabla", "registro", "campo",
                                                             "serie"])
    if not simular:
        for f in a_cargar.itertuples():
            pim.subir(f.tabla, f.registro, f.campo, f.serie, f.archivo)
    return len(a_cargar)
