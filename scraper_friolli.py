"""Ferramenta simples para coletar dados de transparência em CSV.

Este script fornece um exemplo funcional de scraper usando `requests` e
`BeautifulSoup`. Ele processa uma tabela HTML com id `transparency-table`.
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from typing import List, Sequence

import pandas as pd
import requests
from bs4 import BeautifulSoup


SAMPLE_HTML = """
<html>
  <body>
    <table id="transparency-table">
      <thead>
        <tr>
          <th>Item</th>
          <th>Categoria</th>
          <th>Valor (R$)</th>
          <th>Data</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Compra de EPIs</td>
          <td>Saúde</td>
          <td>12.500,00</td>
          <td>2024-01-15</td>
        </tr>
        <tr>
          <td>Reforma de escola</td>
          <td>Educação</td>
          <td>78.900,50</td>
          <td>2024-02-01</td>
        </tr>
        <tr>
          <td>Iluminação pública</td>
          <td>Infraestrutura</td>
          <td>35.200,00</td>
          <td>2024-02-20</td>
        </tr>
      </tbody>
    </table>
  </body>
</html>
"""


@dataclass
class TransparencyRecord:
    item: str
    categoria: str
    valor: str
    data: str


class FriolliTransparencyScraper:
    """Scraper que lê uma tabela HTML e exporta um CSV.

    Parameters
    ----------
    source_url: str | None
        URL que retorna uma página contendo a tabela `transparency-table`. Se
        não for informado, o scraper usará uma tabela de exemplo embutida no
        código.
    headless: bool
        Preservado para compatibilidade com uso de navegadores; atualmente não
        altera o comportamento, mas é registrado nos logs para clareza.
    """

    def __init__(self, source_url: str | None = None, *, headless: bool = True):
        self.source_url = source_url
        self.headless = headless

    def fetch_html(self) -> str:
        """Obtém o HTML de origem via HTTP ou retorna o exemplo local."""

        if not self.source_url:
            logging.debug("Nenhuma URL informada; usando HTML de exemplo embutido.")
            return SAMPLE_HTML

        logging.info("Buscando dados em %s (headless=%s)", self.source_url, self.headless)
        response = requests.get(self.source_url, timeout=30)
        response.raise_for_status()
        logging.debug("Conteúdo recebido com %d bytes", len(response.text))
        return response.text

    def parse_records(self, html: str) -> List[TransparencyRecord]:
        """Converte a tabela `transparency-table` em objetos estruturados."""

        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", id="transparency-table")
        if not table:
            raise ValueError("Tabela com id 'transparency-table' não encontrada no HTML.")

        rows = table.find_all("tr")
        records: List[TransparencyRecord] = []

        for row in rows[1:]:  # pula o cabeçalho
            cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
            if len(cols) != 4:
                logging.debug("Linha ignorada por não ter 4 colunas: %s", cols)
                continue
            record = TransparencyRecord(*cols)
            records.append(record)

        if not records:
            logging.warning("Nenhum registro encontrado na tabela.")
        else:
            logging.info("%d registros parseados.", len(records))

        return records

    def to_csv(self, records: Sequence[TransparencyRecord], output_path: str) -> str:
        """Salva os registros em CSV e retorna o caminho de saída."""

        df = pd.DataFrame([record.__dict__ for record in records])
        df.to_csv(output_path, index=False)
        logging.info("Arquivo salvo em %s", output_path)
        return output_path

    def run(self, output_path: str) -> str:
        html = self.fetch_html()
        records = self.parse_records(html)
        if not records:
            raise RuntimeError("Nenhum registro encontrado para exportar.")

        return self.to_csv(records, output_path)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Exemplo de scraper de transparência para a Prefeitura de Friolli",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--output",
        default="dados_transparencia.csv",
        help="Arquivo CSV de saída.",
    )
    parser.add_argument(
        "--source-url",
        dest="source_url",
        help="URL contendo uma tabela com id 'transparency-table'.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Mantido para compatibilidade; registrado nos logs.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Habilita logs detalhados.",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s - %(message)s",
    )

    scraper = FriolliTransparencyScraper(
        source_url=args.source_url,
        headless=args.headless,
    )

    try:
        output_path = scraper.run(args.output)
        logging.info("Extração concluída com sucesso: %s", output_path)
    except Exception as exc:  # noqa: BLE001
        logging.error("Erro durante a extração: %s", exc)
        raise


if __name__ == "__main__":
    main()
