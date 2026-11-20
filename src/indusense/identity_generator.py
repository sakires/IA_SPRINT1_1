"""Génération des cartes d'identité des fichiers sources."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from indusense.identity_markdown import ColumnStats, IdentityMarkdown


class IdentityGenerator:
    """Génère la carte d'identité (markdown) d'un fichier de données.

    Le travail se fait en deux temps, chacun dans sa propre méthode :
    1. récupération des données : `collectFromFile` (CSV) ou `collectFromDataFrame`
       (données déjà en mémoire, ex. une table extraite d'un dump SQL) ;
    2. construction du markdown : `buildMarkdown`, à partir des attributs.

    Entre les deux, chaque attribut a un getter et un setter (propriétés) pour
    compléter ou corriger les données collectées.

    Les fichiers sont créés dans : <output_root>/<YYYYMMDD>/<name>_<HHMMSS>.md
    """

    def __init__(
        self,
        output_root: str | Path = "artifacts/ingestion/identities",
        separator: str = ",",
    ):
        self.output_root = Path(output_root)
        self.separator = separator
        self.reset()

    # ------------------------------------------------------------------
    # Raccourci : récupération + construction + écriture
    # ------------------------------------------------------------------

    def generateIdentities(self, source: str | Path) -> Path:
        """Analyse le CSV `source` et écrit sa carte d'identité. Retourne le chemin du fichier créé."""
        self.collectFromFile(source)
        return self.write()

    # ------------------------------------------------------------------
    # 1. Récupération des données
    # ------------------------------------------------------------------

    def reset(self) -> "IdentityGenerator":
        """Vide tous les attributs (une donnée non renseignée s'affichera « Inconnu »)."""
        self._name = None
        self._source = None
        self._filesize = None
        self._begin = None
        self._end = None
        self._charset = None
        self._rows = None
        self._cols = None
        self._columns = None
        self._stats = None
        return self

    def collectFromFile(self, source: str | Path) -> "IdentityGenerator":
        """Lit le CSV `source` et renseigne tous les attributs."""
        path = Path(source).resolve()
        self.reset()
        begin = datetime.now()

        charset = self._detect_charset(path)
        df = pd.read_csv(path, sep=self.separator, encoding=charset)
        self.collectFromDataFrame(df)

        self.name = path.stem
        self.source = self._relative_path(path)
        self.filesize = path.stat().st_size
        self.charset = charset
        self.begin = begin  # inclut le temps de lecture du fichier
        return self

    def collectFromDataFrame(self, df: pd.DataFrame) -> "IdentityGenerator":
        """Renseigne les attributs calculables depuis un DataFrame (lignes, colonnes, types, stats).

        Les attributs liés au fichier (name, source, filesize, charset) ne sont pas
        touchés : ils se renseignent avec les setters.
        """
        self.begin = datetime.now()
        types = {col: self._infer_type(df[col]) for col in df.columns}
        self.rows = len(df)
        self.cols = len(df.columns)
        self.columns = types
        self.stats = self._compute_stats(df, types)
        self.end = datetime.now()
        return self

    # ------------------------------------------------------------------
    # 2. Construction du markdown
    # ------------------------------------------------------------------

    def buildMarkdown(self) -> str:
        """Construit le markdown à partir des attributs courants."""
        return IdentityMarkdown(
            title=self.name,
            source=self.source,
            filesize=self.filesize,
            begin=self.begin,
            end=self.end,
            charset=self.charset,
            rows=self.rows,
            cols=self.cols,
            columns=self.columns,
            stats=self.stats,
        ).render()

    def write(self) -> Path:
        """Écrit le markdown dans <output_root>/<YYYYMMDD>/<name>_<HHMMSS>.md."""
        now = self.begin or datetime.now()
        target_dir = self.output_root / now.strftime("%Y%m%d")
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{self.name or 'inconnu'}_{now:%H%M%S}.md"
        target.write_text(self.buildMarkdown(), encoding="utf-8")
        return target

    # ------------------------------------------------------------------
    # Getters / setters
    # ------------------------------------------------------------------

    @property
    def name(self) -> str | None:
        """Nom de la carte (titre et nom du fichier markdown)."""
        return self._name

    @name.setter
    def name(self, value: str | None) -> None:
        self._name = value

    @property
    def source(self) -> str | None:
        """Chemin de la source, relatif à la racine du projet."""
        return self._source

    @source.setter
    def source(self, value: str | Path | None) -> None:
        self._source = None if value is None else Path(value).as_posix()

    @property
    def filesize(self) -> int | None:
        """Taille de la source en octets."""
        return self._filesize

    @filesize.setter
    def filesize(self, value: int | None) -> None:
        self._filesize = value

    @property
    def begin(self) -> datetime | None:
        """Début du traitement."""
        return self._begin

    @begin.setter
    def begin(self, value: datetime | None) -> None:
        self._begin = value

    @property
    def end(self) -> datetime | None:
        """Fin du traitement."""
        return self._end

    @end.setter
    def end(self, value: datetime | None) -> None:
        self._end = value

    @property
    def charset(self) -> str | None:
        """Encodage de la source."""
        return self._charset

    @charset.setter
    def charset(self, value: str | None) -> None:
        self._charset = value

    @property
    def rows(self) -> int | None:
        """Nombre de lignes."""
        return self._rows

    @rows.setter
    def rows(self, value: int | None) -> None:
        self._rows = value

    @property
    def cols(self) -> int | None:
        """Nombre de colonnes."""
        return self._cols

    @cols.setter
    def cols(self, value: int | None) -> None:
        self._cols = value

    @property
    def columns(self) -> dict[str, str] | None:
        """Types inférés : {nom_colonne: type}."""
        return self._columns

    @columns.setter
    def columns(self, value: dict[str, str] | None) -> None:
        self._columns = None if value is None else dict(value)

    @property
    def stats(self) -> list[ColumnStats] | None:
        """Statistiques des colonnes numériques et dates."""
        return self._stats

    @stats.setter
    def stats(self, value: list[ColumnStats] | None) -> None:
        self._stats = None if value is None else list(value)

    # ------------------------------------------------------------------
    # Outils internes
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_stats(df: pd.DataFrame, types: dict[str, str]) -> list[ColumnStats]:
        stats = []
        for col, t in types.items():
            if t == "NUMERIC":
                s = df[col]
                stats.append(ColumnStats(col, s.min(), s.max(), s.mean(), s.median()))
            elif t == "DATE":
                s = pd.to_datetime(df[col], errors="coerce")
                stats.append(ColumnStats(col, s.min(), s.max(), is_date=True))
        return stats

    @staticmethod
    def _relative_path(path: Path) -> str:
        """Chemin relatif à la racine du projet (dossier contenant pyproject.toml)."""
        root = next((p for p in path.parents if (p / "pyproject.toml").exists()), None)
        return path.relative_to(root).as_posix() if root else path.as_posix()

    @staticmethod
    def _detect_charset(path: Path) -> str | None:
        raw = path.read_bytes()
        for enc in ("utf-8", "iso-8859-1"):
            try:
                raw.decode(enc)
                return enc
            except UnicodeDecodeError:
                continue
        return None  # affiché « Inconnu » dans la carte

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
