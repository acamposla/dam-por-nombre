"""La nomenclatura: qué códigos existen, qué significan y a qué campo del PIM va cada uno.

Todo archivo sigue la fórmula IDENTIFICADOR_CÓDIGO_SERIE.ext:

- **Identificador:** la referencia de una variante (70412), el nombre de un modelo (ORION) o un
  tema de marketing que no es ningún producto (SOLAR).
- **Código:** qué tipo de activo es. Las imágenes llevan dos o tres caracteres y los vídeos,
  tres o cuatro letras que empiezan por V, para que se distingan a simple vista.
- **Serie:** dos dígitos siempre, aunque solo haya una pieza (01).

Ejemplos: 70412_PK_01.jpg, SOLAR_KV_02.jpg, ORION_VSET_01.mp4.

Cambiar un código o un campo es cambiar este fichero; la lógica no se toca.
"""
from __future__ import annotations

# código: (medio, tipo, contexto). Tipo y contexto son metadatos para filtrar en el portal de marca.
CODIGOS: dict[str, tuple[str, str, str]] = {
    "PK": ("imagen", "Packshot", "Producto suelto"),
    "2PK": ("imagen", "Packshot", "Caja"),
    "3PK": ("imagen", "Packshot", "Producto con caja"),
    "KV": ("imagen", "Marketing", "Cabecera horizontal"),
    "KVV": ("imagen", "Marketing", "Cabecera vertical"),
    "LF": ("imagen", "Ambiente", "Uso"),
    "FT": ("imagen", "Detalle", "Característica"),
    "FM": ("imagen", "Infografía", "Mosaico"),
    "FMD": ("imagen", "Infografía", "Pieza del mosaico"),
    # Tres vídeos, uno por momento del comprador: decidir, ponerlo en marcha y resolver un fallo
    "VMK": ("vídeo", "Marketing", "Demostración"),
    "VSET": ("vídeo", "Técnico", "Puesta en marcha"),
    "VTR": ("vídeo", "Soporte", "Resolución de problemas"),
}

# Campo del PIM que recibe cada código, por tabla. Lo que no está aquí no tiene sitio:
# las variantes no llevan vídeo (un vídeo de puesta en marcha vale para todo el modelo) y los
# temas no llevan packshot (no son un producto que se pueda fotografiar).
CAMPOS: dict[str, dict[str, str]] = {
    "modelo": {
        "PK": "img_pk", "KV": "img_kv", "KVV": "img_kvv", "LF": "img_lf", "FT": "img_ft",
        "FM": "img_fm", "FMD": "img_fmd",
        "VMK": "vid_mk", "VSET": "vid_set", "VTR": "vid_tr",
    },
    "variante": {"PK": "img_pk", "2PK": "img_2pk", "3PK": "img_3pk"},
    "tema": {
        "KV": "img_kv", "LF": "img_lf", "FT": "img_ft", "FM": "img_fm", "FMD": "img_fmd",
        "VMK": "vid_mk", "VSET": "vid_set", "VTR": "vid_tr",
    },
}

# Nombres heredados: el archivo antiguo no se renombra, se traduce. Solo existen en imágenes.
HEREDADOS: dict[str, tuple[str, str]] = {
    "A": ("PK", "01"),
    "5": ("LF", "01"),
    "4": ("FT", "01"),
}

EXT_IMAGEN = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
EXT_VIDEO = {".mp4", ".mov", ".webm"}
# Los editables (fuentes de diseño) tienen su propia pestaña en el PIM y se suben a mano
EXT_EDITABLE = {".psd", ".ai", ".indd", ".pdf"}
