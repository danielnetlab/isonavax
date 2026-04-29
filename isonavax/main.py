#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import argparse
from pathlib import Path

import pycdlib
from tabulate import tabulate

from isonavax import __version__


# Sirve para crear la ruta completa del archivo.
def join_route(dirname: str, filename: str) -> str:
    # Comprueba si estamos en la raíz
    if dirname == "/":
        return f"/{filename}"
    # Si no estamos en la raíz
    return f"{dirname}/{filename}"


def format_output(fact, mode: str, title: str, extensions: bool = False) -> str:
    if isinstance(fact, list):
        if mode == "visual-dividers":
            lines = []

            lines.append("=" * 50)
            lines.append(f"= {title.center(46)} =")
            lines.append("=" * 50)

            for item in fact:
                lines.append(f" [*] {item}")

            return "\n".join(lines)
        if mode == "table":
            rows = [[item] for item in fact]
            return tabulate(rows, headers=[title])

    return "None"


def get_files(iso_route: Path) -> list:

    # Comprueba si la ruta proporcionada no existe suelta un error.
    if not iso_route.exists():
        raise FileNotFoundError(f"The file does not exist: {iso_route}")

    # Comprueba si la ruta proporcionada no es un archivo.
    if not iso_route.is_file():
        raise ValueError(f"Not a valid file: {iso_route}")

    # Crea un objeto en el que permite trabajar con una ISO.
    #  - Pero no abre todavía la ISO.
    iso = pycdlib.PyCdlib()

    try:
        # Abre el archivo ISO concreto para que `pycdlib` pueda leerlo.
        iso.open(str(iso_route))

        # Declaramos la variable donde se almacenarán las rutas de los arhivos.
        files = []

        # Recorre la ISO en busca de:
        #  - `dirname`: Carpeta actual donde se encuentra.
        #  - `dirnames`: Subcarpetas de la carpeta `dirname`.
        #  - `filenames`: Archivos de la carpeta `dirname`.
        for dirname, dirnames, filenames in iso.walk(iso_path="/"):
            # Recorre todos los archivos para luego imprimirlos.
            for filename in filenames:
                complete_route = join_route(dirname, filename)
                files.append(complete_route)
        return files
    finally:
        iso.close()


def files_filtered(file_route: list, extensions: tuple) -> list:
    filtered = []

    # Recorre todos los archivos de `file_route`, cada vuelta lo almacena en `file`.
    for file in file_route:
        # Si en `file` en minúsculas, terminal en `extensions` se añade a la variable `filtered`.
        if file.lower().endswith(tuple(extensions)):
            # Guarda el archivo en una variable.
            filtered.append(file)
    return filtered


def main():
    parser = argparse.ArgumentParser(
        prog="isonavax", description="Tools iso manipulation."
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument("iso", help=".iso file path")
    parser.add_argument(
        "--get-files", "-g", action="store_true", help="extrat files inside the ISO"
    )
    parser.add_argument(
        "--extensions", "-e", nargs="+", help="extension to search inside the ISO"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["table", "visual-dividers"],
        default="table",
        help="output format",
    )

    args = parser.parse_args()

    if args.extensions and not args.get_files:
        parser.error("--extensions can only be used in conjunction with --get-files")

    if args.get_files:
        files = get_files(Path(args.iso))

        if args.extensions:
            files = files_filtered(files, args.extensions)

        files = format_output(
            fact=files,
            mode=args.format,
            title="LIST OF FILES IN THE ISO",
            # extensions=bool(args.extensions),
        )

        return files

    parser.error("No specified argument")


if __name__ == "__main__":
    print(main())
