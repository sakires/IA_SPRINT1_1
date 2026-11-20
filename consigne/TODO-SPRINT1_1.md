# Créer les cartes d'identité des fichiers CSV

## Mise en place

### Initialiser un projet UV

```shell
uv init indusense
cd indusense
uv python install 3.15
```
Lancer vscode :

```shell
code .
```

Vérifiez les fichiers : *.python-version* et *pyprojet.toml* pour aligner les versions
de l'interpréteur Python à **3.15**

Ouvrez un terminal dans VSCode (*Terminal > New Terminal*)

Epinglez la version de Python :

```shell
uv python pin 3.15
```

Préparez ensuite l'environnement :

```shell
uv venv
```

### Installez les dépendances nécessaires à l'exécution des Notbooks Jupyter

```shell
uv add --dev ipykernel
uv sync
```

Ajoutez les extensions VSCode requises :

- Python (ms-python.python)
- Jupyter (ms-toolsai.jupyter)

### Créez votre Notbook

```Ctrl+Shift+P puis Create new Jupyter Notbook```

Sélectionnez l'interpréteur qui doit avoir le même nom que votre environnement (*indusense*)

## Todo :

- Placez ces documents dans un dossier *datas* à la racine de votre projet, au même niveau que votre Notebook,
- Installez la dépendances *pandas* ```uv add pandas```

### La carte d'identité de chaque fichier

Votre challenge est de créer deux fichiers *markdown* ou autre dans un dossier "*artifacts/ingestion/identities*" :
- artifacts/ingestion/identities/20261120/releves_indicents_HHMMSS.md
- artifacts/ingestion/identities/20261120/telemetry_HHMMSS.md

Chaque fichier sera constitué de la manière suivante :

- Source: <chemin/complet/vers/le/document/source>,
- Filsize : 9999.99 [Ko | Mo | ....]
- ProcessBeginAt: HH:MM:SS
- ProcessEndAt: HH:MM:SS
- Charset: [UTF8 | ISO8859 | Latin | ...]
- Rows Number : 9999
- Cols Number : 9999
- Column list (idéalement dans un tableau)
| Colname | Infered Type |
| --------| -------------|
| machine_id | IDENTITY |

- Pour chaque colonne identifiée numérique ou date :
    - Col name,
    - Min value,
    - Max value,
    - Mean value (uniquement pour les numériques),
    - Median value (uniquuement pour les numériques)

### Pour aller plus loin

Il reste un fichier SQL à traiter, il s'agit d'un script, or, il est nécessaire de dresser sa carte d'identité aussi.

- Chercher une librairie capable de *parser* du SQL,
- Installer la librairie concernée,
- Traiter le document sql transmis de la même manière que les CSV

### En parallèle

- Créez un repository sur **github**,
- Si ce n'est pas déjà le cas, suivez votre projet Indusense,
- Vérifiez votre fichier .gitignore,
- Pensez qu'on ne travaille jamais dans la branche *main*,
- Pensez à créer des branches pour créer vos incréments,
- Commitez souvent, avec de vrais messages de commit,
- Poussez uniquement la branche *main* donc pensez à fusionner votre travail avec un push

## Consignes

- Commencez à "factorer" votre code, écrivez des fonctions dans votre Notebook,
- Pensez que le séparateur d'un CSV n'est pas toujours une virgule (; ou \t) sont aussi souvent utilisés,
- Ne faites pas plus que ce qui est demandé, mais pas moins,
- Utilisez votre agent IA pour vous aider à réaliser le code, ne cherchez pas à le faire vous même