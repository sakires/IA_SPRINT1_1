"""Conversion d'un dump SQL (PostgreSQL) en fichiers CSV."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
import sqlglot
from sqlglot import exp


class DumpToCsv:
    """Extrait les `INSERT ... VALUES` d'un dump SQL et écrit un CSV par table.

    Les fichiers sont créés dans : <output_root>/<nomTable>_<YYYYMMDD_HHMMSS>.csv
    """

    def __init__(
        self,
        output_root: str | Path = "Datas/dump",
        dialect: str = "postgres",
        separator: str = ",",
        encoding: str = "utf-8",
    ):
        self.output_root = Path(output_root)
        self.dialect = dialect
        self.separator = separator
        self.encoding = encoding

    def convert(self, source: str | Path) -> list[Path]:
        """Convertit le dump `source`. Retourne la liste des CSV créés."""
        source = Path(source)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tables = self.extractTables(source)

        self.output_root.mkdir(parents=True, exist_ok=True)
        created = []
        for table, df in tables.items():
            target = self.output_root / f"{table}_{stamp}.csv"
            df.to_csv(target, sep=self.separator, index=False, encoding=self.encoding)
            created.append(target)
        return created

    def extractTables(self, source: str | Path) -> dict[str, pd.DataFrame]:
        """Lit le dump et retourne un DataFrame par table (plusieurs INSERT d'une même table sont concaténés)."""
        sql = Path(source).read_text(encoding=self.encoding)
        frames: dict[str, list[pd.DataFrame]] = {}

        for stmt in sqlglot.parse(sql, read=self.dialect):
            if not isinstance(stmt, exp.Insert) or not isinstance(stmt.expression, exp.Values):
                continue  # BEGIN, CREATE TABLE, COMMIT, INSERT ... SELECT, etc.

            target = stmt.this
            if isinstance(target, exp.Schema):
                table = target.this.name
                columns = [c.name for c in target.expressions]
            else:
                table = target.name
                columns = None  # INSERT sans liste de colonnes

            rows = [
                [self._toPython(v) for v in row.expressions]
                for row in stmt.expression.expressions
            ]
            frames.setdefault(table, []).append(pd.DataFrame(rows, columns=columns))

        return {table: pd.concat(dfs, ignore_index=True) for table, dfs in frames.items()}

    @staticmethod
    def _toPython(value: exp.Expression):
        """Convertit un littéral SQL en valeur Python ('a' -> str, 12 -> int, NULL -> None, TRUE -> bool)."""
        try:
            py = value.to_py()
            # Decimal('2.5') donnerait une colonne `object` dans pandas : on passe en float
            return float(py) if isinstance(py, Decimal) else py
        except ValueError:
            return value.sql()  # expression non littérale (ex: NOW()) : on garde le texte SQL
