# DAM por nombre: que el nombre del archivo diga adónde va

Una marca guarda sus fotos y vídeos de producto en el PIM, que ya tiene campos de imagen en cada
ficha. Lo caro es ponerlos ahí: alguien abre cada ficha y arrastra cada archivo a su campo. Este
repo reproduce, sobre un catálogo sintético, el método que diseñé para que no hiciera falta: quien
produce el archivo lo nombra con una fórmula, y el nombre basta para saber a qué ficha y a qué
campo va.

```
ORION_VSET_01.mp4
  │     │   └─ serie: el orden dentro del campo, siempre dos dígitos
  │     └───── código: qué es (vídeo de puesta en marcha) y a qué campo va (vid_set)
  └─────────── identificador: se busca en el PIM (modelo, variante o tema)
```

El caso contado:
[Que el nombre del archivo diga adónde va](https://alejandrocamposlamas.com/portfolio/que-el-nombre-diga-adonde-va/).
Sale del DAM que diseñé en 2026 sobre Sales Layer para Garza, la marca que dirigía en Imprex.

> **English summary.** A digital asset manager on top of an existing PIM with no extra licence:
> whoever produces a photo or video names it `IDENTIFIER_CODE_SERIES.ext`, and the name alone
> says which record and which field it belongs to. The identifier is looked up in the PIM
> catalogue (model, variant or marketing theme; an identifier found in two tables is rejected,
> not guessed). A closed dictionary of 9 image codes and 3 video codes maps to fields per table;
> what a variant has no field for goes up to its model. Legacy names are translated, not renamed.
> Two files for the same slot are both rejected, unless one is legacy and the other follows the
> formula. Every rejected file keeps its reason, so it can go back to whoever sent it. Data is
> synthetic; code and docs are in Spanish; charts export in English too.

## La fórmula

`IDENTIFICADOR_CÓDIGO_SERIE.ext`, la misma para un producto que para un tema de marketing.

| Código | Qué es | Modelo | Variante | Tema |
|---|---|:-:|:-:|:-:|
| PK | Packshot, producto suelto | ✓ | ✓ | |
| 2PK | Packshot de la caja | | ✓ | |
| 3PK | Producto con su caja | | ✓ | |
| KV, KVV | Cabecera horizontal y vertical | ✓ | | KV |
| LF | Ambiente, producto en uso | ✓ | | ✓ |
| FT | Detalle de una característica | ✓ | | ✓ |
| FM, FMD | Mosaico de características y cada pieza suelta | ✓ | | ✓ |
| VMK | Vídeo para decidir la compra | ✓ | | ✓ |
| VSET | Vídeo de puesta en marcha: instalar, conectar, configurar | ✓ | | ✓ |
| VTR | Vídeo para resolver un fallo | ✓ | | ✓ |

- **Tres tablas.** El modelo es el producto; la variante, cada referencia de venta (color,
  formato); el tema, un concepto que no es ningún producto (solar, wifi) y que también tiene
  fotos y vídeos.
- **Los vídeos llevan V delante** y tres o cuatro letras, para distinguirlos de las imágenes a
  simple vista. Son tres, uno por momento del comprador.
- **Las variantes no llevan vídeo:** un vídeo de puesta en marcha vale para todos los colores. Si
  llega un vídeo o una foto de ambiente nombrado con la referencia de una variante, sube al modelo.
- **Los nombres heredados** (`_A`, `_5`, `_4`) se traducen a `_PK_01`, `_LF_01` y `_FT_01`. El
  archivo antiguo no hay que renombrarlo.
- **Los editables** (PSD, AI, InDesign, PDF) tienen su propia pestaña y se suben a mano.

Todo esto vive en `dam/nomenclatura.py`. Añadir un código o cambiar un campo es tocar ese
fichero, no la lógica.

## La carga

`dam/ingesta.py` convierte una carpeta en un plan: cada archivo, con su tabla, ficha, campo y
serie, o con el motivo por el que no entra.

| Paso | Qué comprueba | Si falla |
|---|---|---|
| Leer el nombre | Fórmula, código conocido, serie de dos dígitos, código del mismo medio que el archivo | Rechazo con el motivo |
| Buscar el identificador | En qué tabla del PIM existe | Si no existe o está en dos tablas, rechazo. No se adivina por la forma del nombre |
| Buscar el campo | Si la tabla tiene campo para ese código | Si es una variante, sube al modelo; si no, rechazo |
| Buscar choques | Dos archivos para la misma ficha, campo y serie | Gana el nombre nuevo sobre el heredado; si no, se rechazan los dos |

`aplicar` es la frontera con el PIM: recibe el plan y sube lo que entra, en orden de serie. Por
defecto simula, y aquí el PIM es un diccionario.

Con la entrega sintética (139 archivos de una sesión de fotos y vídeo), se cargan 118 y se
rechazan 21, cada uno con su motivo.

## Ejecutarlo

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

pytest                                   # 51 comprobaciones, en menos de un segundo
python scripts/ingesta.py                # el plan y los rechazos por pantalla
python scripts/ingesta.py figuras en     # y los gráficos, en inglés
```

Los tests comprueban que la nomenclatura es coherente consigo misma, que cada código se lee, cada
motivo de rechazo por separado, la traducción de los heredados, la tabla y el campo de cada caso,
la subida al modelo, los choques, que `aplicar` simula por defecto y que toda la entrega sintética
sale como se espera.

## Diferencias con el original

- El original iba contra Sales Layer. La nomenclatura, los campos del PIM y el analizador de
  nombres quedaron hechos y probados, pero la conexión con la API no llegó a montarse y el sistema
  no entró en producción.
- El original decidía si un identificador era producto o tema por su forma (solo letras: tema), y
  dejó anotado que eso no distingue un modelo de una campaña. Aquí se consulta el catálogo.
- El original rechazaba un nombre no válido sin decir por qué. Aquí cada rechazo lleva su motivo,
  y hay tres comprobaciones nuevas: código de vídeo en una imagen, choques entre archivos y lo que
  una variante no tiene, que sube a su modelo.
- Los modelos, referencias y temas son inventados.

## Licencia

MIT. Ver `LICENSE`.
