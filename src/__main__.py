import glob
import os

from typing import Annotated, Optional

import typer

from rich.progress import track

from .__version__ import __version__
from .to_csv import parse_line, create_metar, metar_to_csv, header

app = typer.Typer()


def version_callback(version: bool) -> None:
    if version:
        print(f"raw-to-csv, version {__version__}")
        raise typer.Exit()


@app.command()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            help="Show module version and exit.",
        ),
    ] = None,
) -> None:
    print("metar-datasets CLI")


@app.command("to-csv")
def create_csv_file() -> None:
    data_path = "./data/mrlb/"
    dfiles = glob.glob("*.txt", root_dir=data_path)
    dfiles.sort()

    with open(f"{data_path}/metars.csv", "w") as csvfile:

        csvfile.write(",".join(header) + "\n")

        for dfile in dfiles:
            f = open(f"{data_path}/{dfile}")
            file_basename = os.path.basename(f.name)
            for line in track(
                f.readlines(),
                description=f"[green]Processing file {file_basename}",
            ):
                if "NIL" in line:
                    continue

                tup = parse_line(line)
                metar = create_metar(tup)
                csvfile.write(metar_to_csv(metar))


if __name__ == "__main__":
    app()
