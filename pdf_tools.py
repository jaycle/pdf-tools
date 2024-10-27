#!/usr/bin/env python3
from pathlib import Path
from typing import List
import typer
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from rich.console import Console
from rich.progress import track

app = typer.Typer(help="PDF manipulation tools")
console = Console()


@app.command()
def merge(
    input_files: List[Path],
    output_file: Path,
) -> None:
    """Merge multiple PDF files into a single PDF."""
    merger = PdfMerger()

    for pdf_file in track(input_files, description="Merging PDFs..."):
        if not pdf_file.exists():
            console.print(f"[red]Error:[/red] File {pdf_file} does not exist")
            raise typer.Exit(1)
        merger.append(str(pdf_file))

    merger.write(str(output_file))
    console.print(f"[green]Successfully merged PDFs into[/green] {output_file}")


def _parse_page_ranges(range_str: str) -> List[int]:
    """Parse page ranges like '1,2,3-5,7' into a list of page numbers."""
    pages = set()
    ranges = range_str.replace(" ", "").split(",")

    for r in ranges:
        try:
            if "-" in r:
                start, end = map(int, r.split("-"))
                if start > end:
                    raise ValueError(f"Invalid range: {start}-{end}")
                pages.update(range(start, end + 1))
            else:
                pages.add(int(r))
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid page range: {r}")
            raise typer.Exit(1)

    return sorted(list(pages))


@app.command()
def split(
    input_file: Path,
    output_file: Path,
    pages: str = typer.Option(
        ...,
        "--pages",
        "-p",
        help="Pages to extract (e.g. '1,2,3-5,7')",
    ),
) -> None:
    """Split a PDF file into individual pages."""
    if not input_file.exists():
        console.print(f"[red]Error:[/red] File {input_file} does not exist")
        raise typer.Exit(1)

    try:
        page_numbers = _parse_page_ranges(pages)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)

    pdf = PdfReader(str(input_file))
    writer = PdfWriter()
    max_pages = len(pdf.pages)

    for page_num in track(page_numbers, description="Extracting..."):
        idx = page_num - 1
        if idx < 0 or idx >= max_pages:
            console.print(f"[red]Error:[/red] Invalid page number {page_num}")
            raise typer.Exit(1)
        writer.add_page(pdf.pages[idx])

    if len(writer.pages) > 0:
        writer.write(str(output_file))
        console.print(f"[green]Successfully split PDF into[/green] {output_file}")
    else:
        console.print("[red]Error:[/red] No pages were extracted")


if __name__ == "__main__":
    app()
