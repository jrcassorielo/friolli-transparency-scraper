#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Iterable

import pandas as pd


LOGGER = logging.getLogger("transparency_reporter")


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def find_numeric_columns(frame: pd.DataFrame) -> list[str]:
    numeric_frame = frame.select_dtypes(include="number")
    return list(numeric_frame.columns)


def infer_category_columns(frame: pd.DataFrame) -> list[str]:
    category_columns = []
    for column in frame.columns:
        if frame[column].dtype == "object":
            unique_ratio = frame[column].nunique(dropna=True) / max(len(frame), 1)
            if unique_ratio < 0.5:
                category_columns.append(column)
    return category_columns


def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def summarize_numeric(frame: pd.DataFrame, numeric_columns: Iterable[str]) -> list[str]:
    lines = []
    for column in numeric_columns:
        series = pd.to_numeric(frame[column], errors="coerce")
        total = series.sum(skipna=True)
        average = series.mean(skipna=True)
        lines.append(
            f"- **{column}**: total {format_currency(total)} | média {format_currency(average)}"
        )
    return lines


def summarize_categories(frame: pd.DataFrame, category_columns: Iterable[str], top_n: int) -> list[str]:
    lines = []
    for column in category_columns:
        counts = frame[column].astype(str).value_counts(dropna=True).head(top_n)
        lines.append(f"- **{column}**:")
        for value, count in counts.items():
            lines.append(f"  - {value}: {count}")
    return lines


def build_report(
    frame: pd.DataFrame,
    source: Path,
    top_n: int = 5,
) -> str:
    numeric_columns = find_numeric_columns(frame)
    category_columns = infer_category_columns(frame)

    lines = [
        "# Relatório de Transparência",
        "",
        f"**Arquivo analisado:** `{source}`",
        f"**Linhas:** {len(frame)}",
        f"**Colunas:** {len(frame.columns)}",
        "",
    ]

    if numeric_columns:
        lines.extend(["## Totais e Médias", *summarize_numeric(frame, numeric_columns), ""])
    else:
        lines.extend(["## Totais e Médias", "_Nenhuma coluna numérica encontrada._", ""])

    if category_columns:
        lines.extend(
            ["## Principais Categorias", *summarize_categories(frame, category_columns, top_n), ""]
        )
    else:
        lines.extend(["## Principais Categorias", "_Nenhuma coluna categórica encontrada._", ""])

    lines.append("## Prévia dos Dados")
    lines.append(frame.head(top_n).to_markdown(index=False))
    lines.append("")

    return "\n".join(lines)


def save_report(report: str, output_path: Path | None) -> None:
    if output_path is None:
        print(report)
        return

    output_path.write_text(report, encoding="utf-8")
    LOGGER.info("Relatório salvo em %s", output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera um relatório rápido de um CSV de transparência."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        default="dados_transparencia.csv",
        help="Caminho do CSV para analisar.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Salvar o relatório em um arquivo Markdown.",
    )
    parser.add_argument(
        "--top",
        "-t",
        type=int,
        default=5,
        help="Quantidade de linhas e categorias a exibir.",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Ativa logs detalhados.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(args.verbose)

    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        LOGGER.error("Arquivo não encontrado: %s", csv_path)
        raise SystemExit(1)

    LOGGER.info("Lendo CSV %s", csv_path)
    frame = pd.read_csv(csv_path)
    report = build_report(frame, csv_path, top_n=args.top)
    save_report(report, args.output)


if __name__ == "__main__":
    main()
