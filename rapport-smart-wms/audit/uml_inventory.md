# Inventaire UML - étape préparatoire au chapitre 5

Date d'analyse : 6 octobre 2026. Cette note documente l'état des sources avant toute création du chapitre 5. Elle ne modifie ni la numérotation des cas d'usage ni le contenu validé du chapitre 3.

## Sources disponibles

| Fichier | Type identifié | Couverture | Réutilisation prévue |
|---|---|---|---|
| `00_vue_globale.puml` | Cas d'utilisation global | Domaines WMS et acteurs principaux | À simplifier : ses identifiants `UC-Gxx` ne font pas partie du catalogue validé. |
| `01_reception.puml` | Cas d'utilisation détaillé | UC-R01 à UC-R12 | Réutilisable après contrôle graphique. |
| `02_stockage.puml` | Cas d'utilisation détaillé | UC-S01 à UC-S14 | Réutilisable après contrôle graphique. |
| `03_expedition.puml` | Cas d'utilisation détaillé | UC-E01 à UC-E15 | Réutilisable après contrôle graphique. |
| `04_transversal.puml` | Cas d'utilisation transversal | UC-T, UC-EN et UC-AI | Réutilisable comme vue des capacités transversales. |
| `DA-01_reception.puml` | Activité | Réception, UC-R01 à UC-R11 | Réutilisable. |
| `DA-02_stockage.puml` | Activité | Stockage, UC-S01, UC-S04, UC-S05, UC-S09 à UC-S14 | Réutilisable. |
| `DA-03_expedition.puml` | Activité | Expédition, UC-E01 à UC-E15 | Réutilisable. |
| `DA-04_transversal.puml` | Activité | Température, énergie et supervision | Réutilisable. |
| `00_vue_globale (1).puml` | Doublon exact | Même contenu que `00_vue_globale.puml` | À ne pas intégrer deux fois. |

## Conformité avec le chapitre 3

Les sources détaillées couvrent complètement les identifiants UC-R01 à UC-R12, UC-S01 à UC-S14 et UC-E01 à UC-E15. Les intitulés devront être comparés ligne à ligne avec les tableaux de chapitre 3 avant génération des figures, sans les renommer.

Le diagramme global utilise des libellés `UC-G01` à `UC-G08`. Ces identifiants ne sont pas dans la numérotation validée. Pour le chapitre 5, il sera refait comme une vue de domaines sans identifiants détaillés, conformément au cahier des charges.

## Éléments manquants

- Cas d'utilisation Yard & Quais : UC-Y01 à UC-Y07.
- Cas d'utilisation Ressources & Infrastructures : UC-RES01 à UC-RES10.
- Diagramme de séquence : aucun fichier existant n'utilise la notation de séquence PlantUML.
- Modèle de domaine / diagramme de classes.
- Diagramme de composants.

## Ordre de réalisation retenu

1. Vérifier les libellés des trois diagrammes détaillés réutilisables contre les tableaux du chapitre 3.
2. Rendre les neuf sources existantes en figures lisibles et les inspecter visuellement.
3. Créer les vues manquantes Yard, Ressources, séquences, modèle de domaine et composants.
4. Rédiger le chapitre 5 seulement autour des figures réellement validées.
