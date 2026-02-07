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


def build_markdown_report(
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


def build_html_report(
    frame: pd.DataFrame,
    source: Path,
    top_n: int = 5,
) -> str:
    numeric_columns = find_numeric_columns(frame)
    category_columns = infer_category_columns(frame)

    def render_metric_items() -> str:
        if not numeric_columns:
            return "<p>Nenhuma coluna numérica encontrada.</p>"
        items = []
        for column in numeric_columns:
            series = pd.to_numeric(frame[column], errors="coerce")
            total = series.sum(skipna=True)
            average = series.mean(skipna=True)
            items.append(
                f"<li><strong>{column}</strong>: total {format_currency(total)} | "
                f"média {format_currency(average)}</li>"
            )
        return "<ul>" + "".join(items) + "</ul>"

    def render_category_items() -> str:
        if not category_columns:
            return "<p>Nenhuma coluna categórica encontrada.</p>"
        sections = []
        for column in category_columns:
            counts = frame[column].astype(str).value_counts(dropna=True).head(top_n)
            rows = "".join(f"<li>{value}: {count}</li>" for value, count in counts.items())
            sections.append(f"<div class='category'><h3>{column}</h3><ul>{rows}</ul></div>")
        return "".join(sections)

    preview_table = frame.head(top_n).to_html(index=False, classes="data-table")

    return f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Relatório de Transparência</title>
    <style>
      :root {{
        color-scheme: light dark;
        font-family: "Inter", "Segoe UI", sans-serif;
        background-color: #f5f6fa;
        color: #111827;
      }}
      body {{
        margin: 0;
        padding: 24px;
        background-color: #f5f6fa;
      }}
      .container {{
        max-width: 920px;
        margin: 0 auto;
        background: #ffffff;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
      }}
      h1 {{
        font-size: 1.75rem;
        margin-bottom: 0.25rem;
      }}
      h2 {{
        margin-top: 2rem;
        font-size: 1.25rem;
      }}
      .meta {{
        color: #475569;
        font-size: 0.95rem;
      }}
      .category {{
        margin-bottom: 1rem;
      }}
      .data-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
      }}
      .data-table th,
      .data-table td {{
        border-bottom: 1px solid #e2e8f0;
        padding: 8px 10px;
        text-align: left;
      }}
      .data-table th {{
        background-color: #f1f5f9;
      }}
      @media (max-width: 600px) {{
        body {{
          padding: 12px;
        }}
        .container {{
          padding: 16px;
        }}
        .data-table {{
          font-size: 0.8rem;
        }}
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Relatório de Transparência</h1>
      <p class="meta"><strong>Arquivo analisado:</strong> {source}</p>
      <p class="meta"><strong>Linhas:</strong> {len(frame)} | <strong>Colunas:</strong> {len(frame.columns)}</p>

      <h2>Totais e Médias</h2>
      {render_metric_items()}

      <h2>Principais Categorias</h2>
      {render_category_items()}

      <h2>Prévia dos Dados</h2>
      {preview_table}
    </div>
  </body>
</html>
"""


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
        help="Salvar o relatório em um arquivo Markdown ou HTML.",
    )
    parser.add_argument(
        "--top",
        "-t",
        type=int,
        default=5,
        help="Quantidade de linhas e categorias a exibir.",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=("markdown", "html"),
        default="markdown",
        help="Formato do relatório (markdown ou html).",
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
    if args.format == "html":
        report = build_html_report(frame, csv_path, top_n=args.top)
    else:
        report = build_markdown_report(frame, csv_path, top_n=args.top)
    save_report(report, args.output)


if __name__ == "__main__":
    main()
