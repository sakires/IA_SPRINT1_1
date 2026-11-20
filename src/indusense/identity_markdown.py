"""Modèle Markdown d'une carte d'identité de fichier."""

import math
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import PurePosixPath

UNKNOWN = "Inconnu"


@dataclass
class ColumnStats:
    """Statistiques d'une colonne numérique ou date."""

    name: str | None = None
    min: object = None
    max: object = None
    mean: float | None = None
    median: float | None = None
    is_date: bool = False  # moyenne / médiane non applicables aux dates


@dataclass
class IdentityMarkdown:
    """Met en forme la carte d'identité d'un fichier en Markdown.

    Toutes les données sont optionnelles : une donnée absente (None, NaN, NaT, vide)
    est remplacée par 'Inconnu' dans le Markdown produit.
    """

    source: str | None = None             # chemin relatif à la racine du projet
    filesize: int | None = None           # en octets
    begin: datetime | None = None
    end: datetime | None = None
    charset: str | None = None
    rows: int | None = None
    cols: int | None = None
    columns: dict[str, str] | None = None  # {nom_colonne: type_inféré}
    stats: list[ColumnStats] | None = field(default=None)

    def render(self) -> str:
        title = PurePosixPath(self.source).name if self._is_known(self.source) else UNKNOWN
        lines = [
            f"# Identité : {title}",
            "",
            f"- Source: {self._fmt(self.source)}",
            f"- Filesize: {self._fmt(self.filesize, self._human_size)}",
            f"- ProcessBeginAt: {self._fmt(self.begin, self._time)}",
            f"- ProcessEndAt: {self._fmt(self.end, self._time)}",
            f"- Charset: {self._fmt(self.charset)}",
            f"- Rows Number: {self._fmt(self.rows)}",
            f"- Cols Number: {self._fmt(self.cols)}",
            "",
            "## Colonnes",
            "",
            "| Colname | Infered Type |",
            "| ------- | ------------ |",
        ]
        if self.columns:
            lines += [f"| {self._fmt(col)} | {self._fmt(t)} |" for col, t in self.columns.items()]
        else:
            lines.append(f"| {UNKNOWN} | {UNKNOWN} |")

        lines += [
            "",
            "## Statistiques",
            "",
            "| Colname | Min | Max | Mean | Median |",
            "| ------- | --- | --- | ---- | ------ |",
        ]
        if self.stats is None:
            lines.append(f"| {UNKNOWN} | {UNKNOWN} | {UNKNOWN} | {UNKNOWN} | {UNKNOWN} |")
        for s in self.stats or []:
            mean = "-" if s.is_date else self._fmt(s.mean, lambda v: f"{v:.3f}")
            median = "-" if s.is_date else self._fmt(s.median)
            lines.append(
                f"| {self._fmt(s.name)} | {self._fmt(s.min)} | {self._fmt(s.max)} | {mean} | {median} |"
            )

        return "\n".join(lines) + "\n"

    @staticmethod
    def _is_known(value) -> bool:
        if value is None or value == "":
            return False
        try:
            return not math.isnan(value)  # NaN numérique
        except TypeError:
            return str(value) != "NaT"    # NaT pandas, ou valeur non numérique

    @classmethod
    def _fmt(cls, value, formatter=str) -> str:
        return formatter(value) if cls._is_known(value) else UNKNOWN

    @staticmethod
    def _time(value: datetime) -> str:
        return f"{value:%H:%M:%S}"

    @staticmethod
    def _human_size(size: float) -> str:
        for unit in ("o", "Ko", "Mo", "Go"):
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} To"
