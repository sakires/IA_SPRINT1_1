"""Génération des cartes d'identité des fichiers sources."""

from datetime import datetime
from pathlib import Path

import pandas as pd


class IdentityGenerator:
    """Génère la carte d'identité (markdown) d'un fichier de données.

    Les fichiers sont créés dans : <output_root>/<YYYYMMDD>/<nom_source>_<HHMMSS>.md
    """

    def __init__(
        self,
        output_root: str | Path = "artifacts/ingestion/identities",
        separator: str = ",",
    ):
        self.output_root = Path(output_root)
        self.separator = separator

    def generateIdentities(self, source: str | Path) -> Path:
        """Analyse `source` et écrit sa carte d'identité. Retourne le chemin du fichier créé."""
        source = Path(source).resolve()
        begin = datetime.now()

        charset = self._detect_charset(source)
        df = pd.read_csv(source, sep=self.separator, encoding=charset)
        types = {col: self._infer_type(df[col]) for col in df.columns}

        end = datetime.now()

        target_dir = self.output_root / begin.strftime("%Y%m%d")
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{source.stem}_{begin.strftime('%H%M%S')}.md"

        lines = [
            f"# Identité : {source.name}",
            "",
            f"- Source: {self._relative_path(source)}",
            f"- Filesize: {self._human_size(source.stat().st_size)}",
            f"- ProcessBeginAt: {begin:%H:%M:%S}",
            f"- ProcessEndAt: {end:%H:%M:%S}",
            f"- Charset: {charset}",
            f"- Rows Number: {len(df)}",
            f"- Cols Number: {len(df.columns)}",
            "",
            "## Colonnes",
            "",
            "| Colname | Infered Type |",
            "| ------- | ------------ |",
            *(f"| {col} | {t} |" for col, t in types.items()),
            "",
            "## Statistiques",
            "",
            "| Colname | Min | Max | Mean | Median |",
            "| ------- | --- | --- | ---- | ------ |",
        ]

        for col, t in types.items():
            if t == "NUMERIC":
                s = df[col]
                lines.append(f"| {col} | {s.min()} | {s.max()} | {s.mean():.3f} | {s.median()} |")
            elif t == "DATE":
                s = pd.to_datetime(df[col], errors="coerce")
                lines.append(f"| {col} | {s.min()} | {s.max()} | - | - |")

        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return target

    @staticmethod
    def _relative_path(path: Path) -> str:
        """Chemin relatif à la racine du projet (dossier contenant pyproject.toml)."""
        root = next((p for p in path.parents if (p / "pyproject.toml").exists()), None)
        return path.relative_to(root).as_posix() if root else path.as_posix()

    @staticmethod
    def _detect_charset(path: Path) -> str:
        raw = path.read_bytes()
        for enc in ("utf-8", "iso-8859-1"):
            try:
                raw.decode(enc)
                return enc
            except UnicodeDecodeError:
                continue
        return "unknown"

    @staticmethod
    def _infer_type(s: pd.Series) -> str:
        if s.name and str(s.name).endswith("_id"):
            return "IDENTITY"
        if pd.api.types.is_bool_dtype(s):
            return "BOOLEAN"
        if pd.api.types.is_numeric_dtype(s):
            return "NUMERIC"
        sample = s.dropna().astype(str).head(100)
        if not sample.empty and sample.str.match(r"^\d{4}-\d{2}-\d{2}").all():
            return "DATE"
        return "TEXT"

    @staticmethod
    def _human_size(size: float) -> str:
        for unit in ("o", "Ko", "Mo", "Go"):
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} To"
