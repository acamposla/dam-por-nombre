"""Un catálogo y una entrega de archivos sintéticos, con semilla fija.

- **Catálogo del PIM:** ocho modelos de una marca de iluminación inventada, tres variantes por
  modelo (referencias numéricas) y cinco temas de marketing. LUNA es a la vez un modelo y una
  campaña, a propósito: es el caso que la forma del nombre no puede resolver.
- **Entrega:** la carpeta que manda una agencia después de una sesión de fotos y vídeo. La mayoría
  de los nombres siguen la fórmula; el resto trae los errores de siempre (serie de un dígito,
  códigos inventados, editables mezclados, guiones en vez de guiones bajos, el mismo archivo en
  dos formatos) y nombres heredados del sistema antiguo.

Cada archivo lleva `esperado`: el estado o el motivo de rechazo que le corresponde. Sirve para
los tests, nunca para planificar. Todos los nombres y referencias son inventados.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from dam.ingesta import (
    AL_MODELO,
    CHOQUE,
    DOS_TABLAS,
    NO_EXISTE,
    SIN_CAMPO,
    SUSTITUIDO,
    Catalogo,
)
from dam.nomenclatura import CAMPOS
from dam.parser import CODIGO, EDITABLE, EXTENSION, FORMULA, HEREDADO_VIDEO, MEDIO, SERIE

SEMILLA = 2026
MODELOS = ["ORION", "NUBE", "BRISA", "TERRA", "VEGA", "CORAL", "NOVA", "LUNA"]
TEMAS = ["SOLAR", "WIFI", "ZIGBEE", "EXTERIOR", "LUNA"]


def catalogo() -> Catalogo:
    variantes = {f"7{i:02d}{j}0": m for i, m in enumerate(MODELOS, start=10) for j in range(1, 4)}
    return Catalogo(modelos=set(MODELOS), variantes=variantes, temas=set(TEMAS))


def entrega(semilla: int = SEMILLA, n_buenos: int = 110) -> pd.DataFrame:
    rng = np.random.default_rng(semilla)
    cat = catalogo()
    variantes = sorted(cat.variantes)
    temas = [t for t in TEMAS if t not in MODELOS]
    modelos = [m for m in MODELOS if m not in TEMAS]
    usados: dict[tuple[str, str], int] = {}  # (ficha final, código) -> última serie usada
    filas: list[tuple[str, str]] = []

    def ficha(ident: str, codigo: str) -> str:
        if ident in cat.variantes and codigo not in CAMPOS["variante"]:
            return cat.variantes[ident]
        return ident

    def siguiente(ident: str, codigo: str) -> str:
        k = (ficha(ident, codigo), codigo)
        usados[k] = usados.get(k, 0) + 1
        return f"{usados[k]:02d}"

    def ext(codigo: str) -> str:
        if codigo.startswith("V"):
            return str(rng.choice([".mp4", ".mov"], p=[0.8, 0.2]))
        return str(rng.choice([".jpg", ".png", ".tif"], p=[0.7, 0.2, 0.1]))

    # Nombres buenos: variantes, modelos y temas, en proporción a lo que produce una sesión
    for _ in range(n_buenos):
        donde = rng.choice(["variante", "modelo", "tema", "variante al modelo"],
                           p=[0.40, 0.35, 0.15, 0.10])
        if donde == "variante":
            ident, codigo = str(rng.choice(variantes)), str(rng.choice(["PK", "2PK", "3PK"]))
        elif donde == "modelo":
            ident = str(rng.choice(modelos))
            codigo = str(rng.choice(["PK", "KV", "KVV", "LF", "FT", "FM", "FMD", "VMK", "VSET",
                                     "VTR"]))
        elif donde == "tema":
            ident = str(rng.choice(temas))
            codigo = str(rng.choice(["KV", "LF", "FT", "VMK"]))
        else:
            ident, codigo = str(rng.choice(variantes)), str(rng.choice(["LF", "VSET"]))
        esperado = AL_MODELO if donde == "variante al modelo" else "cargar"
        filas.append((f"{ident}_{codigo}_{siguiente(ident, codigo)}{ext(codigo)}", esperado))

    # Heredados que entran: la variante aún no tiene packshot, o el modelo no tiene ambiente
    libres = [v for v in variantes if (v, "PK") not in usados]
    for v in libres[:6]:
        siguiente(v, "PK")
        filas.append((f"{v}_A.jpg", "cargar"))
    heredados_lf = 0
    for v in variantes:
        if heredados_lf < 2 and (cat.variantes[v], "LF") not in usados:
            siguiente(v, "LF")
            filas.append((f"{v}_5.jpg", AL_MODELO))
            heredados_lf += 1

    # Heredado y nombre nuevo para el mismo hueco: gana el nuevo
    v = libres[6]
    siguiente(v, "PK")
    filas += [(f"{v}_A.jpg", SUSTITUIDO), (f"{v}_PK_01.jpg", "cargar")]

    # El mismo archivo exportado dos veces: nadie elige por la agencia
    m, codigo = "CORAL", "KV"
    serie = siguiente(m, codigo)
    filas += [(f"{m}_{codigo}_{serie}.jpg", CHOQUE), (f"{m}_{codigo}_{serie}.png", CHOQUE)]

    # Los errores de siempre
    filas += [
        ("70110_PK_1.jpg", SERIE),
        ("NUBE_KV_2.jpg", SERIE),
        ("ORION_PKS_01.jpg", CODIGO),
        ("BRISA_LIFE_01.jpg", CODIGO),
        ("TERRA_VSET_01.jpg", MEDIO),  # el fotograma de portada del vídeo, con el nombre del vídeo
        ("VEGA_A.mp4", HEREDADO_VIDEO),
        ("ORION-KV-01.jpg", FORMULA),
        ("foto definitiva nube.jpg", FORMULA),
        ("NOVA_KV_01.psd", EDITABLE),
        ("NOVA_KV_01.ai", EDITABLE),
        ("ficha_tecnica_vega.pdf", EDITABLE),
        ("BRISA_LF_01.gif", EXTENSION),
        ("ORIONN_PK_01.jpg", NO_EXISTE),
        ("79990_PK_01.jpg", NO_EXISTE),
        ("LUNA_KV_01.jpg", DOS_TABLAS),
        ("SOLAR_PK_01.jpg", SIN_CAMPO),
        ("WIFI_3PK_01.jpg", SIN_CAMPO),
        ("NUBE_2PK_01.jpg", SIN_CAMPO),
    ]
    orden = rng.permutation(len(filas))
    return pd.DataFrame([filas[i] for i in orden], columns=["archivo", "esperado"])
