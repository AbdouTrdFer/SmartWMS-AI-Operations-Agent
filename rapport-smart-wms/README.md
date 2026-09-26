# Rapport Smart WMS

Ce dossier contient une version restructurée du rapport de stage sous forme de projet LaTeX.

## Contenu

- `main.tex` : point d'entrée LaTeX.
- `config/` : packages, style et commandes.
- `chapters/` : chapitres séparés.
- `figures/` : schémas redessinés en SVG, PDF et PNG.
- `annexes/plantuml/` : sources PlantUML copiées depuis le dossier `diagramms/`.
- `build/` : PDF de prévisualisation et HTML de contrôle.

## Compilation LaTeX

Un moteur TeX n'est pas installé sur cette machine au moment de la génération. Après installation
de TeX Live ou MiKTeX, compiler avec :

```powershell
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Le PDF présent dans `build/` est une prévisualisation générée localement pour contrôler la mise en page.
