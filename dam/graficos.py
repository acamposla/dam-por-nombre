"""Los dos gráficos del caso, en español o en inglés.

- Anatomía de un nombre: qué dato lleva cada parte y adónde manda el archivo.
- Resultado de una entrega: cuántos archivos se cargan en cada tabla y por qué se rechaza el resto.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from dam import ingesta as i
from dam import parser as p

TINTA, SUAVE, ACENTO, LINEA, FONDO, VERDE = ("#16161a", "#55555f", "#9a3412", "#dededa",
                                             "#fbfbf9", "#2f6f73")
AZUL = "#3b4f7a"
plt.rcParams.update({
    "figure.facecolor": FONDO, "axes.facecolor": FONDO, "savefig.facecolor": FONDO,
    "axes.edgecolor": LINEA, "axes.labelcolor": SUAVE, "xtick.color": SUAVE,
    "ytick.color": SUAVE, "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
})

TEXTOS = {
    "es": {
        "t_anatomia": "Un nombre de archivo, tres datos",
        "partes": [
            ("Identificador", "se busca en el PIM:\n¿modelo, variante o tema?", "modelo ORION"),
            ("Código", "qué es y a qué campo va", "campo vid_set\nTécnico · Puesta en marcha"),
            ("Serie", "el orden dentro del campo,\nsiempre dos dígitos", "posición 01"),
        ],
        "heredado": "Un nombre heredado no se renombra, se traduce:",
        "t_resultado": "Una entrega de agencia: qué se carga y por qué se rechaza el resto",
        "cargan": "Se cargan", "rechazan": "Se rechazan",
        "tablas": {"modelo": "En el modelo", "variante": "En la variante", "tema": "En el tema"},
        "motivos": {
            i.CHOQUE: "Dos archivos para el mismo hueco", i.SIN_CAMPO: "Código sin campo en esa tabla",
            i.NO_EXISTE: "Identificador que no está en el PIM",
            i.DOS_TABLAS: "Identificador en dos tablas", i.SUSTITUIDO: "Lo sustituye un nombre nuevo",
            p.EDITABLE: "Editables: van a mano", p.EXTENSION: "Extensión no admitida",
            p.FORMULA: "No sigue la fórmula", p.CODIGO: "Código desconocido",
            p.SERIE: "Serie sin dos dígitos", p.MEDIO: "El código no casa con el archivo",
            p.HEREDADO_VIDEO: "Nombre heredado en un vídeo",
        },
        "x": "archivos",
        "pie": "de {n} archivos recibidos",
    },
    "en": {
        "t_anatomia": "One file name, three pieces of data",
        "partes": [
            ("Identifier", "looked up in the PIM:\nmodel, variant or theme?", "model ORION"),
            ("Code", "what it is and which\nfield it goes to", "field vid_set\nTechnical · Setup"),
            ("Series", "the order within the field,\nalways two digits", "position 01"),
        ],
        "heredado": "A legacy name isn't renamed, it's translated:",
        "t_resultado": "An agency delivery: what gets loaded and why the rest is rejected",
        "cargan": "Loaded", "rechazan": "Rejected",
        "tablas": {"modelo": "Into the model", "variante": "Into the variant",
                   "tema": "Into the theme"},
        "motivos": {
            i.CHOQUE: "Two files for the same slot", i.SIN_CAMPO: "Code with no field in that table",
            i.NO_EXISTE: "Identifier not in the PIM", i.DOS_TABLAS: "Identifier in two tables",
            i.SUSTITUIDO: "Replaced by a new name", p.EDITABLE: "Source files: uploaded by hand",
            p.EXTENSION: "File type not accepted", p.FORMULA: "Doesn't follow the formula",
            p.CODIGO: "Unknown code", p.SERIE: "Series without two digits",
            p.MEDIO: "Code doesn't match the file type", p.HEREDADO_VIDEO: "Legacy name on a video",
        },
        "x": "files",
        "pie": "out of {n} files received",
    },
}


def anatomia(idioma: str = "es"):
    t = TEXTOS[idioma]
    fig = plt.figure(figsize=(12, 6.3))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.04, 0.92, t["t_anatomia"], fontsize=20, weight="bold", color=TINTA, va="top")

    tam = 40
    ancho = 0.6 * tam / (12 * 72)  # ancho de un carácter monoespaciado, en fracción del eje
    trozos = [("ORION", AZUL), ("_", SUAVE), ("VSET", ACENTO), ("_", SUAVE), ("01", VERDE),
              (".mp4", SUAVE)]
    total = sum(len(s) for s, _ in trozos)
    x, y = 0.5 - total * ancho / 2, 0.68
    centros = []
    for s, color in trozos:
        ax.text(x, y, s, fontsize=tam, family="DejaVu Sans Mono", color=color, va="center",
                weight="bold" if color != SUAVE else "normal")
        if color != SUAVE:
            centros.append((x + len(s) * ancho / 2, color, len(s) * ancho))
        x += len(s) * ancho

    destinos = [0.20, 0.50, 0.80]
    for (cx, color, w), dx, (nombre, que, valor) in zip(centros, destinos, t["partes"]):
        ax.plot([cx - w / 2, cx + w / 2], [y - 0.065, y - 0.065], color=color, lw=3,
                solid_capstyle="round")
        ax.annotate("", xy=(dx, 0.45), xytext=(cx, y - 0.075),
                    arrowprops={"arrowstyle": "-|>", "color": color, "lw": 1.3,
                                "mutation_scale": 13})
        ax.text(dx, 0.41, nombre, ha="center", va="top", fontsize=13.5, weight="bold",
                color=color)
        ax.text(dx, 0.355, que, ha="center", va="top", fontsize=11, color=SUAVE, linespacing=1.3)
        ax.text(dx, 0.235, valor, ha="center", va="top", fontsize=11.5, color=TINTA,
                family="DejaVu Sans Mono", linespacing=1.4)

    ax.plot([0.04, 0.96], [0.12, 0.12], color=LINEA, lw=1)
    ax.text(0.04, 0.065, t["heredado"], fontsize=11.5, color=SUAVE, va="center")
    ax.text(0.96, 0.065, "71010_A.jpg  →  71010_PK_01.jpg", fontsize=12.5, color=TINTA,
            va="center", ha="right", family="DejaVu Sans Mono")
    return fig


def resultado(plan: pd.DataFrame, idioma: str = "es"):
    t = TEXTOS[idioma]
    cargan = plan[plan["estado"] == "cargar"]["tabla"].value_counts()
    cargan = cargan.reindex(["modelo", "variante", "tema"]).fillna(0).astype(int)
    rechazos = plan[plan["estado"] == "rechazado"]["motivo"].value_counts()
    filas = ([(t["tablas"][k], v, VERDE) for k, v in cargan.items()]
             + [(t["motivos"][k], v, ACENTO) for k, v in rechazos.items()])
    filas = filas[::-1]

    fig, ax = plt.subplots(figsize=(11, 0.42 * len(filas) + 2.2))
    ys = list(range(len(filas)))
    ax.barh(ys, [v for _, v, _ in filas], color=[c for _, _, c in filas], height=0.62)
    ax.set_yticks(ys, [n for n, _, _ in filas])
    for y, (_, v, c) in zip(ys, filas):
        ax.text(v + 0.8, y, str(v), va="center", fontsize=10, color=c)
    corte = len(rechazos) - 0.5
    ax.axhline(corte, color=LINEA, lw=1)
    xmax = max(v for _, v, _ in filas)
    ax.text(xmax * 1.02, corte + 0.35, f"{t['cargan']}: {int(cargan.sum())}", ha="right",
            va="bottom", color=VERDE, weight="bold", fontsize=11.5)
    ax.text(xmax * 1.02, corte - 0.35, f"{t['rechazan']}: {int(rechazos.sum())}", ha="right",
            va="top", color=ACENTO, weight="bold", fontsize=11.5)
    ax.set_xlim(0, xmax * 1.08)
    ax.set_xlabel(f"{t['x']} ({t['pie'].format(n=len(plan))})")
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_title(t["t_resultado"], loc="left", fontsize=14, color=TINTA, weight="bold", pad=14)
    fig.tight_layout()
    return fig
