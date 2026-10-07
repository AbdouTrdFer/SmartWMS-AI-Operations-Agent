# Rapport complet Smart WMS

Source : `Rapport_Stage_FERHAN_Abdelali_Chapitres_1_2_3_4_Organise_Professionnel.pdf`, conserve sans modification.

Version actuelle : `Rapport_FERHAN_SmartWMS_Complet_Chapitres_1_5_Final.pdf`, disponible directement a la racine du workspace et dans `build/`. Toutes les pages sont au format A4 portrait. La figure 4.1 est l'image source `Architecture_f.png`, inseree sans modification.

## Livrables

- `build/Rapport_FERHAN_SmartWMS_Complet_Chapitres_1_5_Final.pdf` : PDF complet final compile depuis LaTeX.
- `build/Architecture_Fonctionnelle_Smart_WMS_A4_Portrait.pdf` : vue d'ensemble vectorielle, une page portrait ; details dans le rapport.
- `main.tex`, `config/revision.tex`, `chapters/revision/`, `tables/`, `bibliography/revision.bib` : sources actives.
- `figures/revision/*.tex` : schemas TikZ editables.
- `audit/revision_complete/index.html` : captures de toutes les pages, generees localement lors du controle.
- `audit/revision_complete/verification.json` : controles automatiques.
- `CORRESPONDANCE.md`, `CORRECTIONS.md` : couverture et journal de revision.

## Compilation

Depuis ce dossier :

```powershell
.\tools\tectonic\tectonic.exe --keep-logs --keep-intermediates --outdir build main.tex
Copy-Item build/main.pdf build/Rapport_Stage_FERHAN_Abdelali_Complet_Corrige.pdf
```

Sur une autre machine, installer Tectonic puis executer `tectonic --keep-logs --outdir build main.tex`. Le premier lancement peut necessiter une connexion pour obtenir les packages TeX. Tectonic traite la bibliographie et les renvois automatiquement.

Controle des pages depuis la racine du workspace (PyMuPDF et Pillow requis) :

```powershell
.\.venv\Scripts\python.exe -X utf8 rapport-smart-wms/tools/check_report.py
```

La version abregee precedente est archivee dans `archive/version_abregee/`. Les anciens generateurs ReportLab ne font pas partie de cette compilation. Ne pas relancer la migration initiale sur les sources corrigees.
