import pandas as pd
import pytest


def pytest_configure(config):
    config._drive_summary = {}


def pytest_sessionfinish(session):
    summary = session.config._drive_summary
    if not summary:
        return
    print()
    print("=" * 65)
    print("  RESUMEN: ARCHIVOS DETECTADOS EN GOOGLE DRIVE DATASET")
    print("=" * 65)
    print(f"  DRIVE_BASE:           {summary.get('drive_base', 'N/A')}")
    print(f"  ¿Ruta existe?:        {'SÍ' if summary.get('drive_exists') else 'NO'}")
    print()
    if summary.get("drive_exists"):
        print("  DIRECTORIOS:")
        for d in summary.get("directorios", []):
            print(f"    - {d}")
        print()
        print("  ARCHIVOS EN CSVFiles/:")
        for f in summary.get("csv_files", []):
            print(
                f"    - {f['nombre']:50s} "
                f"{f['filas']:>6,} filas  "
                f"({f['bytes']:>10,} bytes)"
            )
        print(
            f"    {'TOTAL':50s} "
            f"{summary['csv_total_filas']:>6,} filas"
        )
        print()
        print(f"  BreastCancer_Images/jpeg/:")
        print(f"    Carpetas (SeriesInstanceUID): {summary.get('image_folders', 0):>6,}")
        print(f"    Archivos de imagen totales:   {summary.get('image_files', 0):>6,}")
        print()
        print(f"  BreastCancer_Tabular/data.csv:")
        print(f"    ¿Existe?:        {'SÍ' if summary.get('tabular_exists') else 'NO'}")
        print(f"    Filas:           {summary.get('tabular_rows', 0):>6,}")
        print(f"    Columnas:        {summary.get('tabular_cols', 0)}")
        print()
        print(f"  META (meta.csv):")
        print(f"    SeriesInstanceUID únicos:      {summary.get('series_in_meta', 0):>6,}")
        print(f"    Coincidencias con imágenes:    {summary.get('matching_series', 0):>6,}")
        print()
        total = summary.get('total_archivos', 0)
        print(f"  TOTAL ARCHIVOS EN DATASET:          {total:>6,}")
    print("=" * 65)
    print()
