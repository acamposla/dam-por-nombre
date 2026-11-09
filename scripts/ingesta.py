"""Planifica la carga de la entrega sintética: qué va a qué ficha y campo, y qué se rechaza.

Uso:
    python scripts/ingesta.py                       # el plan y el resumen por pantalla
    python scripts/ingesta.py figuras [es|en]       # y además los gráficos en esa carpeta
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from dam import datos as d
from dam import ingesta as i


def main(salida: Path | None, idioma: str = "es") -> None:
    pd.set_option("display.width", 160)
    pd.set_option("display.max_rows", 200)
    entrega = d.entrega()
    plan = i.planificar(entrega["archivo"].tolist(), d.catalogo())

    cargar = plan[plan["estado"] == "cargar"]
    print(f"{len(plan)} archivos recibidos: {len(cargar)} se cargan, "
          f"{len(plan) - len(cargar)} se rechazan\n")
    print("Se cargan, por tabla y campo")
    print(cargar.groupby(["tabla", "campo"]).size().to_string(), "\n")
    print("Se rechazan, con el motivo (lo que se devuelve a la agencia)")
    rech = plan[plan["estado"] == "rechazado"].sort_values(["motivo", "archivo"])
    print(rech[["archivo", "motivo"]].to_string(index=False))

    pim = i.PIMSimulado()
    i.aplicar(plan, pim, simular=False)
    print(f"\nPIM simulado: {len(pim.fichas)} combinaciones de ficha y campo con archivos")

    if salida is not None:
        from dam import graficos as g

        salida.mkdir(parents=True, exist_ok=True)
        g.anatomia(idioma).savefig(salida / "anatomia.png", dpi=110)
        g.resultado(plan, idioma).savefig(salida / "resultado.png", dpi=110)
        g.anatomia(idioma).savefig(salida / "portada.png", dpi=100)
        print(f"Gráficos en {salida} ({idioma})")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None,
         sys.argv[2] if len(sys.argv) > 2 else "es")
