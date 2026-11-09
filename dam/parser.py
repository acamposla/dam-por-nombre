"""Leer un nombre de archivo: o es un activo con sus tres partes, o es un rechazo con su motivo.

Un nombre que no se entiende no se adivina. Se devuelve con el motivo para que quien lo subió
sepa qué cambiar, y la carga sigue con el resto.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass

from dam.nomenclatura import CODIGOS, EXT_EDITABLE, EXT_IMAGEN, EXT_VIDEO, HEREDADOS

EDITABLE = "editable: va a mano a su pestaña"
EXTENSION = "extensión no admitida"
FORMULA = "no sigue la fórmula"
CODIGO = "código desconocido"
SERIE = "serie sin dos dígitos"
MEDIO = "el código no casa con el tipo de archivo"
HEREDADO_VIDEO = "nombre heredado en un vídeo"


@dataclass(frozen=True)
class Activo:
    archivo: str
    identificador: str
    codigo: str
    serie: str
    medio: str  # "imagen" o "vídeo"
    heredado: bool


@dataclass(frozen=True)
class Rechazo:
    archivo: str
    motivo: str


def leer(archivo: str) -> Activo | Rechazo:
    base, ext = os.path.splitext(archivo)
    ext = ext.lower()
    if ext in EXT_EDITABLE:
        return Rechazo(archivo, EDITABLE)
    if ext not in EXT_IMAGEN | EXT_VIDEO:
        return Rechazo(archivo, EXTENSION)
    medio = "imagen" if ext in EXT_IMAGEN else "vídeo"
    partes = base.split("_")

    # Fórmula actual: IDENTIFICADOR_CÓDIGO_SERIE (el identificador puede llevar guiones bajos)
    if len(partes) >= 3:
        identificador, codigo, serie = "_".join(partes[:-2]), partes[-2].upper(), partes[-1]
        if codigo in CODIGOS and identificador:
            if not re.fullmatch(r"\d{2}", serie):
                return Rechazo(archivo, SERIE)
            if CODIGOS[codigo][0] != medio:
                return Rechazo(archivo, MEDIO)
            return Activo(archivo, identificador, codigo, serie, medio, heredado=False)

    # Nombre heredado: IDENTIFICADOR_SUFIJO, solo imágenes
    if len(partes) >= 2 and partes[-1].upper() in HEREDADOS and partes[0]:
        if medio == "vídeo":
            return Rechazo(archivo, HEREDADO_VIDEO)
        codigo, serie = HEREDADOS[partes[-1].upper()]
        return Activo(archivo, "_".join(partes[:-1]), codigo, serie, medio, heredado=True)

    # Tiene forma de fórmula (algo_XX_01) pero el código no existe
    if len(partes) >= 3 and partes[0] and re.fullmatch(r"\d+", partes[-1]):
        return Rechazo(archivo, CODIGO)
    return Rechazo(archivo, FORMULA)
