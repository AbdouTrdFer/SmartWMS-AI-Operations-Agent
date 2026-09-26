# Contexte complet du stage Smart WMS + prompt de révision du rapport

> Document de contexte à fournir à Codex / Claude / autre assistant de développement documentaire.  
> Objectif : permettre à l’agent de comprendre le stage, le rapport déjà construit, les décisions prises, les difficultés rencontrées, les conventions de rédaction, et les corrections attendues sur le PDF actuel.

---

## 1. Identité du stage

**Étudiant :** FERHAN Abdelali  
**Établissement :** ENIAD — École Nationale de l’Intelligence Artificielle & du Digital, Berkane  
**Filière :** Génie informatique  
**Organisme d’accueil :** Smart Automation Technologies, Tanger, Maroc  
**Encadrante en entreprise :** Chaimae Kaina  
**Période du stage :** août à octobre 2026  

**Sujet du stage :**

> **Conception d'une Architecture Intelligente pour la Transformation d'un Warehouse Management System (WMS) Traditionnel en Smart WMS : Modélisation Métier, Fonctionnelle et Applicative**

Le stage ne porte pas sur le développement complet d’une application WMS. Il porte sur la **conception**, la **modélisation métier**, la **modélisation fonctionnelle**, la **modélisation UML**, puis la préparation d’une **architecture applicative logique**.

Le livrable attendu est un rapport de stage académique, structuré, professionnel, clair pour un jury, avec des schémas, tableaux, figures, citations et une progression logique depuis le benchmark jusqu’à l’architecture cible.

---

## 2. Contexte général du projet

Le projet vise à transformer un **WMS traditionnel** en **Smart WMS**.

Un WMS traditionnel couvre principalement :

- la réception des marchandises ;
- la gestion des emplacements ;
- la gestion des stocks ;
- l’inventaire ;
- la préparation des commandes ;
- le picking ;
- le packing ;
- l’expédition ;
- la gestion des tâches ;
- la traçabilité des mouvements.

Le Smart WMS proposé ne doit pas être une simple collection de technologies. Il doit être conçu comme une architecture **générique**, **modulaire**, **adaptable** et **configurable**.

Le système cible doit pouvoir s’adapter à plusieurs niveaux de maturité d’entrepôt :

1. **Entrepôt simple**
   - terminaux RF ;
   - codes-barres / QR ;
   - chariots manuels ;
   - scanners ;
   - règles métier classiques.

2. **Entrepôt automatisé**
   - RFID ;
   - convoyeurs ;
   - trieurs ;
   - AS/RS ;
   - shuttle ;
   - AMR / AGV ;
   - Pick-to-Light / Put-to-Light ;
   - WCS / WES.

3. **Entrepôt sensible ou réglementé**
   - produits à température contrôlée ;
   - humidité contrôlée ;
   - produits fragiles ;
   - lots ;
   - numéros de série ;
   - dates d’expiration ;
   - FEFO ;
   - capteurs IoT ;
   - BMS / EMS.

Le Smart WMS doit donc distinguer :

- **Core** : fonctionnalités indispensables au fonctionnement WMS.
- **Smart** : fonctionnalités qui améliorent la décision grâce aux données, à l’optimisation ou au ML, sans exiger forcément un équipement spécifique.
- **Optional** : fonctionnalités dépendantes d’une infrastructure ou d’un équipement particulier.

---

## 3. Méthodologie du stage

La démarche suivie est :

```text
SCAN → PLAN → ACT
```

### SCAN

Objectifs :

- comprendre les WMS modernes ;
- benchmarker les solutions leaders ;
- identifier les fonctions communes ;
- analyser les limites d’un WMS traditionnel ;
- identifier les problèmes et contraintes métier.

### PLAN

Objectifs :

- structurer les besoins ;
- cartographier les use cases ;
- proposer une architecture fonctionnelle cible ;
- distinguer Core / Smart / Optional ;
- construire une modélisation UML cohérente.

### ACT

Objectifs :

- préparer la validation du modèle ;
- vérifier la traçabilité problèmes → use cases → architecture ;
- préparer l’architecture applicative logique ;
- préparer les futures étapes techniques sans encore choisir une stack définitive.

---

## 4. Benchmark étudié

Le benchmark fonctionnel a porté sur trois solutions leaders :

1. **Manhattan Active Warehouse Management**
2. **SAP Extended Warehouse Management (SAP EWM)**
3. **Oracle Warehouse Management Cloud**

Le benchmark n’est pas un classement. Il sert à extraire des principes de conception.

### 4.1 Manhattan Active Warehouse Management

**Idée directrice :** unification de l’exécution.

Manhattan met en avant une approche où les stocks, commandes, tâches, opérateurs, équipements, robotique, yard, transport et intelligence décisionnelle sont connectés dans une même logique d’exécution.

Point fort retenu :

> Relier la décision à l’action opérationnelle réelle.

Exemples d’agents IA mentionnés dans l’étude :

- Wave Coordinator Agent ;
- Labor Agent ;
- Warehouse Associate Agent.

Apport pour le projet :

- importance de la boucle courte décision → tâche → exécution ;
- importance de connecter l’intelligence aux ressources terrain ;
- importance du moteur de tâches.

### 4.2 SAP Extended Warehouse Management

**Idée directrice :** richesse du modèle métier.

SAP EWM est retenu comme référence pour la structuration des objets métier :

- produit ;
- article ;
- handling unit ;
- lot ;
- numéro de série ;
- date d’expiration ;
- ressource ;
- livraison ;
- emplacement ;
- zone ;
- règle ;
- tâche ;
- données de référence.

Point fort retenu :

> Un Smart WMS doit comprendre correctement le contexte métier avant de proposer des optimisations.

Apport pour le projet :

- introduire un profil logistique produit ;
- prendre en compte température, humidité, fragilité, poids, volume, lot, DLC, FEFO ;
- traiter les données de référence comme couche fondamentale.

### 4.3 Oracle Warehouse Management Cloud

**Idée directrice :** orchestration commande → wave → allocation → tâches → opérateur / équipement → exécution.

Oracle a été utile pour clarifier la chaîne outbound :

```text
Commande client
→ Wave / Batch
→ Allocation du stock
→ Création des tâches
→ Affectation opérateur / équipement
→ Picking / packing
→ Chargement
→ Expédition
```

Point fort retenu :

> Centralité de l’orchestration des commandes et des tâches.

Apport pour le projet :

- renforcer le bloc gestion des commandes ;
- renforcer le bloc gestion des tâches ;
- montrer comment transformer une demande en travail exécutable ;
- intégrer les assistants liés aux tâches, inventaire, anomalies ou ruptures.

---

## 5. Architecture fonctionnelle cible du Smart WMS

L’architecture fonctionnelle finale est organisée en plusieurs couches.

### 5.1 Systèmes externes

Le Smart WMS échange avec :

- ERP / SAP ;
- MES ;
- TMS / YMS ;
- Fournisseurs ;
- Clients ;
- Autres systèmes : Finance, RH, BI, CRM, etc. ;
- BMS / EMS pour l’énergie, le bâtiment, la température, l’éclairage et les équipements techniques.

### 5.2 Cœur opérationnel du WMS

Le cœur opérationnel couvre :

1. **Réception marchandises**
   - prise de rendez-vous ;
   - gestion des quais ;
   - réception ;
   - contrôle qualité ;
   - réception quantitative ;
   - cross-docking ;
   - retours fournisseurs.

2. **Stockage & inventaire**
   - gestion des emplacements ;
   - gestion des stocks ;
   - emplacement ;
   - réapprovisionnement ;
   - stock de réserve ;
   - inventaire tournant ;
   - gestion des lots / dates ;
   - ajustement d’inventaire.

3. **Gestion des commandes**
   - ordonnancement ;
   - planification des commandes ;
   - préparation des lots ;
   - wave / batch ;
   - allocation ;
   - gestion des priorités.

4. **Exécution entrepôt**
   - picking ;
   - packing ;
   - staging ;
   - consolidation ;
   - chargement ;
   - expédition ;
   - retours clients.

5. **Yard & quais**
   - gestion de la cour ;
   - planification des quais ;
   - affectation des quais ;
   - gestion des portes ;
   - gestion des transporteurs ;
   - enregistrement des entrées / sorties.

6. **Données de référence**
   - produits / articles ;
   - clients ;
   - fournisseurs ;
   - emplacements / zones ;
   - unités logistiques ;
   - règles / politiques ;
   - utilisateurs / rôles.

### 5.3 Gestion des tâches et des travaux

Bloc central transversal :

- création des tâches ;
- affectation des tâches ;
- exécution des tâches ;
- suivi des statuts ;
- gestion des exceptions ;
- priorisation ;
- réaffectation.

Ce bloc est essentiel car il relie les décisions métier à l’exécution réelle sur le terrain.

### 5.4 Stockage des données

Deux niveaux :

- **Base opérationnelle OLTP**
  - transactions ;
  - stock courant ;
  - tâches ;
  - statuts ;
  - mouvements ;
  - données opérationnelles.

- **Base analytique OLAP / DWH**
  - historiques ;
  - KPI ;
  - analyse ;
  - prévisions ;
  - apprentissage ;
  - tableaux de bord.

Important : les données de référence et le stockage des données ne sont pas forcément des use cases déclenchés par un acteur. Ils doivent être traités dans le rapport comme des **couches de support** et dans l’UML plutôt via un **diagramme de classes / modèle de domaine** et un **diagramme de composants**, pas forcément dans les diagrammes de cas d’utilisation.

### 5.5 Ressources & infrastructures

Couvre :

1. **Gestion de la main-d’œuvre**
   - planification ;
   - suivi des performances ;
   - compétences ;
   - équilibrage de charge ;
   - productivité.

2. **Gestion des équipements**
   - chariots ;
   - transpalettes ;
   - convoyeurs ;
   - trieurs ;
   - AS/RS ;
   - shuttle ;
   - AMR ;
   - AGV ;
   - robots ;
   - maintenance.

3. **Gestion énergétique & environnementale**
   - consommation électrique par zone ;
   - consommation des équipements ;
   - température ;
   - humidité ;
   - seuils ;
   - modes marche / veille / arrêt ;
   - pics de consommation ;
   - historique énergétique.

4. **Interfaces WCS / WES**
   - instruction aux équipements ;
   - état des équipements ;
   - erreurs ;
   - itinéraires ;
   - trafic ;
   - tâches.

5. **Gestion des actifs**
   - suivi des actifs ;
   - étalonnage ;
   - taux d’utilisation ;
   - surveillance de l’état ;
   - cycle de vie.

### 5.6 Intelligence & aide à la décision

Couvre :

- prévision de la demande ;
- prévision de charge inbound / outbound ;
- prévision de ressources ;
- optimisation du slotting ;
- optimisation des ordres / tâches ;
- optimisation des parcours ;
- séquençage des tâches ;
- optimisation de la main-d’œuvre ;
- affectation intelligente ;
- détection d’anomalies ;
- détection de risques ;
- recommandations ;
- tableaux de bord.

### 5.7 Terminaux & appareils terrain

- terminaux RF ;
- scanners code-barres / QR ;
- lecteurs RFID ;
- capteurs ;
- caméras / vision ;
- caméra 3D ;
- balances / pesage ;
- systèmes vocaux ;
- smartphone / tablette ;
- Pick-to-Light / Put-to-Light ;
- vehicle terminal.

---

## 6. Use cases validés et numérotation

Les numérotations suivantes doivent être conservées.

### 6.1 Réception — UC-R01 à UC-R12

| ID | Use case | Type |
|---|---|---|
| UC-R01 | Planifier rendez-vous et quai | Core |
| UC-R02 | Réceptionner les marchandises | Core |
| UC-R03 | Identifier le produit | Core |
| UC-R04 | Contrôler la quantité | Core |
| UC-R05 | Contrôler la qualité | Core |
| UC-R06 | Gérer une anomalie de réception | Core |
| UC-R07 | Proposer emplacement de stockage | Core |
| UC-R08 | Prévoir la charge de réception | Smart |
| UC-R09 | Compter les cartons par caméra 3D | Optional |
| UC-R10 | Lire l’étiquette par OCR | Optional |
| UC-R11 | Détecter les défauts par vision | Optional |
| UC-R12 | Suivre le conteneur connecté | Optional |

### 6.2 Stockage & inventaire — UC-S01 à UC-S14

| ID | Use case | Type |
|---|---|---|
| UC-S01 | Mettre en stock / putaway | Core |
| UC-S02 | Gérer les stocks | Core |
| UC-S03 | Gérer les emplacements | Core |
| UC-S04 | Réaliser l’inventaire tournant | Core |
| UC-S05 | Réapprovisionner la zone picking | Core |
| UC-S06 | Détecter la congestion d’une zone | Smart |
| UC-S07 | Surveiller les produits sensibles | Core conditionnel |
| UC-S08 | Gérer lots / DLC / FEFO | Core conditionnel |
| UC-S09 | Choisir l’emplacement optimal / slotting | Smart |
| UC-S10 | Cibler les emplacements à recompter | Smart |
| UC-S11 | Prédire une rupture avant blocage | Smart |
| UC-S12 | Chercher un emplacement alternatif | Smart |
| UC-S13 | Suivre les palettes par RFID | Optional |
| UC-S14 | Déplacer le stock par AMR / AGV | Optional |

### 6.3 Commandes & exécution / expédition — UC-E01 à UC-E15

| ID | Use case | Type |
|---|---|---|
| UC-E01 | Recevoir la commande client | Core |
| UC-E02 | Planifier la commande | Core |
| UC-E03 | Créer la wave / batch | Core |
| UC-E04 | Allouer le stock | Core |
| UC-E05 | Créer tâches de picking | Core |
| UC-E06 | Effectuer le picking | Core |
| UC-E07 | Effectuer le packing | Core |
| UC-E08 | Charger le camion | Core |
| UC-E09 | Expédier la commande | Core |
| UC-E10 | Guider le picking RF / Pick-to-Light | Optional |
| UC-E11 | Optimiser le parcours picking | Smart |
| UC-E12 | Contrôler le picking scan / poids / vision | Optional |
| UC-E13 | Recommander l’emballage | Smart |
| UC-E14 | Contrôler le chargement scan / caméra | Optional |
| UC-E15 | Détecter commandes à risque de retard | Smart |

### 6.4 Yard & Quais — UC-Y01 à UC-Y07

| ID | Use case | Type |
|---|---|---|
| UC-Y01 | Planifier les rendez-vous camion | Core |
| UC-Y02 | Gérer les portes et quais | Core |
| UC-Y03 | Affecter un quai | Core |
| UC-Y04 | Enregistrer entrée / sortie transporteur | Core |
| UC-Y05 | Suivre véhicule / transporteur en temps réel | Optional |
| UC-Y06 | Détecter congestion cour / quai | Smart |
| UC-Y07 | Réaffecter dynamiquement un quai | Smart |

### 6.5 Ressources & infrastructures — UC-RES01 à UC-RES10

| ID | Use case | Type |
|---|---|---|
| UC-RES01 | Planifier main-d’œuvre | Core |
| UC-RES02 | Suivre compétences et performance | Core |
| UC-RES03 | Suivre état des équipements | Core |
| UC-RES04 | Optimiser affectation opérateur / équipement | Smart |
| UC-RES05 | Gérer maintenance équipements | Core |
| UC-RES06 | Suivre actifs | Core |
| UC-RES07 | Superviser interfaces WCS / WES | Optional |
| UC-RES08 | Suivre consommation énergétique | Core / support |
| UC-RES09 | Détecter surconsommation ou dérive | Optional + Smart |
| UC-RES10 | Recommander veille / arrêt équipement | Optional + Smart |

### 6.6 Intelligence et transversal

Conventions utilisées :

- UC-AI01 à UC-AI06 : prévision, optimisation, anomalies, recommandations.
- UC-T01 à UC-T05 : température, humidité, environnement, alertes.
- UC-EN01 à UC-EN06 : énergie, consommation, dérives, veille / arrêt.

---

## 7. UML et diagrammes attendus

Le rapport doit progressivement inclure :

1. **Diagrammes de cas d’utilisation**
   - vue globale simplifiée ;
   - réception ;
   - stockage & inventaire ;
   - commandes & expédition ;
   - transversal smart ;
   - yard & quais ;
   - ressources & infrastructures.

2. **Diagrammes d’activité**
   - réception intelligente ;
   - stockage intelligent ;
   - expédition intelligente ;
   - transversal énergie / environnement.

3. **Diagrammes de séquence**
   - réception avec caméra 3D / OCR / vision ;
   - slotting intelligent ;
   - réapprovisionnement prédictif ;
   - température produit sensible ;
   - optimisation énergétique ;
   - wave / picking / packing.

4. **Diagramme de classes / modèle de domaine**
   - Warehouse ;
   - Zone ;
   - Location ;
   - Product ;
   - ProductRequirement ;
   - StockUnit ;
   - HandlingUnit ;
   - Lot ;
   - CustomerOrder ;
   - OrderLine ;
   - Task ;
   - Worker ;
   - Equipment ;
   - Device ;
   - Sensor ;
   - SensorReading ;
   - Alert ;
   - Recommendation.

5. **Diagramme de composants**
   - composants métier WMS ;
   - services smart ;
   - intégrations ERP / MES / TMS / WCS / BMS ;
   - couche données ;
   - couche équipements / IoT.

Important : pour les diagrammes de cas d’utilisation, il faut désormais séparer visuellement :

```text
Core use cases
Smart use cases
Optional / infrastructure-dependent use cases
```

Ne pas mettre tout dans un seul bloc “capacités smart optionnelles”.

---

## 8. État actuel du rapport

Le rapport contient actuellement :

1. Page de couverture corrigée.
2. Fiche synthétique du stage.
3. Table des matières automatique.
4. Introduction générale.
5. Chapitre 1 — Présentation de l’organisme d’accueil et cadrage du stage.
6. Chapitre 2 — État de l’art et benchmark des solutions WMS.
7. Chapitre 3 — Analyse des besoins et identification des use cases.
8. Chapitre 4 — Architecture fonctionnelle cible du Smart WMS.

Fichiers actuels à considérer :

- PDF actuel : `Rapport_Stage_FERHAN_Abdelali_Chapitres_1_2_3_4_Final.pdf`
- DOCX courant si disponible : `Rapport_Stage_FERHAN_Abdelali_Chapitres_1_2_3_4.docx`
- Version corrigée précédente : `Rapport_Stage_FERHAN_Abdelali_Chapitres_1_2_3_Corrections_exactes.pdf`
- Support de benchmark / architecture : `SMart warehouse Mgt Systems .pdf`
- Slides / PPT sources selon besoin :
  - `SMart warehouse Mgt Systems .pptx`
  - `Smart_WMS_Use_Cases_Detailles.pptx`
  - `Smart_WMS_UML_Redesign.zip`
  - fichiers `.puml` existants si présents.

---

## 9. Style du rapport à conserver

Le style doit être :

- académique ;
- professionnel ;
- clair ;
- fluide ;
- sans remplissage ;
- accessible à un jury non expert WMS ;
- technique mais pas trop complexe ;
- humain, non robotique ;
- homogène du début à la fin.

À éviter :

- titres qui commentent le rapport lui-même ;
- encarts inutiles ;
- formulations comme “Transition vers le chapitre...” ;
- expressions trop IA ou trop générales ;
- “l’IA partout” ;
- tableaux trop longs sans justification ;
- schémas avec textes hors des boîtes ;
- flèches croisées ou diagrammes illisibles ;
- changement brutal de style entre chapitres.

À conserver :

- numérotation des figures par chapitre : `Figure 3.1`, `Figure 4.1`, etc. ;
- numérotation des tableaux par chapitre : `Tableau 3.1`, `Tableau 4.1`, etc. ;
- citations au format `[n]` ;
- schémas clairs ;
- tableaux de synthèse ;
- style bleu marine principal ;
- peu de couleurs, utilisées avec cohérence.

---

## 10. Corrections déjà décidées

Les corrections suivantes ont été décidées et doivent être respectées :

1. Supprimer les encadrés qui commentent le rapport lui-même.
2. Conserver uniquement l’encart **Problématique directrice** dans l’introduction.
3. Remplacer les titres de type :
   - “Ce que le benchmark ne dit pas”
   - “Principe retenu”
   - “Transition vers le chapitre...”
4. Intégrer le contenu utile des encadrés directement dans les paragraphes.
5. Traiter **Données de référence** et **Stockage des données OLTP / OLAP-DWH** dans le Chapitre 4 comme couches de support.
6. Ne pas créer des use cases artificiels pour les couches de données si elles sont mieux représentées par le modèle de domaine et les composants.
7. Dans les diagrammes UML, distinguer :
   - Core ;
   - Smart ;
   - Optional.

---

## 11. Prochaines parties probables du rapport

Le rapport devra encore couvrir :

### Chapitre 5 — Modélisation UML

À développer avec :

- philosophie de modélisation ;
- use case diagrams ;
- activity diagrams ;
- sequence diagrams ;
- domain model / class diagram ;
- state diagrams ;
- component diagram ;
- traçabilité.

### Chapitre 6 — Architecture applicative proposée

À développer avec :

- composants applicatifs ;
- services métier ;
- services smart ;
- couche données ;
- intégration ERP/MES/TMS/WCS/BMS ;
- intégration terrain ;
- logique modulaire ;
- scénario de déploiement progressif.

### Chapitre 7 — Validation, limites et perspectives

À développer avec :

- matrice de traçabilité ;
- validation par scénarios ;
- limites du benchmark ;
- limites du modèle ;
- limites techniques ;
- perspectives :
  - prototype ;
  - simulation ;
  - dashboard ;
  - microservices ;
  - IoT gateway ;
  - edge computing ;
  - intégration IA ciblée ;
  - tests terrain.

### Conclusion générale

À développer avec :

- synthèse du travail ;
- apports du stage ;
- apports personnels ;
- valeur de l’architecture ;
- perspectives futures.

---

# Prompt complet pour Codex / VS Code

Copier-coller le prompt suivant dans Codex si l’objectif est de réviser le PDF actuel, corriger les schémas, améliorer la mise en page et éventuellement migrer vers LaTeX.

```text
Tu es un expert en rédaction académique, architecture SI, WMS / supply chain, LaTeX, mise en page professionnelle et révision de rapports de stage.

Contexte :
Je travaille sur un rapport de stage intitulé :
« Conception d'une Architecture Intelligente pour la Transformation d'un Warehouse Management System (WMS) Traditionnel en Smart WMS : Modélisation Métier, Fonctionnelle et Applicative ».

Étudiant : FERHAN Abdelali
École : ENIAD — École Nationale de l’Intelligence Artificielle & du Digital, Berkane
Filière : Génie informatique
Entreprise : Smart Automation Technologies, Tanger, Maroc
Encadrante : Chaimae Kaina
Période : août à octobre 2026

Objectif du rapport :
Présenter une démarche complète allant du benchmark des solutions WMS leaders jusqu’à la proposition d’une architecture Smart WMS générique, modulaire et adaptable, puis sa modélisation UML et sa traduction vers une architecture applicative logique.

Fichiers à utiliser :
- Le PDF actuel du rapport : Rapport_Stage_FERHAN_Abdelali_Chapitres_1_2_3_4_Final.pdf
- Le DOCX courant s’il existe : Rapport_Stage_FERHAN_Abdelali_Chapitres_1_2_3_4.docx
- Les anciens rapports corrigés si utiles
- Les figures PNG/SVG existantes
- Les fichiers PlantUML existants
- Les slides/PDF source de benchmark et d’architecture si présents

Travail demandé :
1. Lire le rapport actuel.
2. Identifier les problèmes de mise en page :
   - schémas trop petits ;
   - texte hors des boîtes ;
   - figures mal alignées ;
   - légendes coupées ;
   - tableaux coupés ou trop denses ;
   - titres mal placés ;
   - pages trop vides ou trop chargées ;
   - incohérence des couleurs ;
   - numérotation de figures/tableaux incohérente ;
   - encadrés inutiles ;
   - ruptures de style.
3. Corriger les schémas en les redessinant proprement lorsque nécessaire.
4. Garder une seule couleur d’accent principale : bleu marine.
5. Utiliser des couleurs secondaires uniquement avec cohérence :
   - vert/teal pour ressources ou flux support ;
   - violet pour intelligence / aide à la décision ;
   - orange pour optional / infrastructure.
6. Ne pas modifier le fond métier sans raison.
7. Ne pas inventer de nouveaux use cases qui contredisent les conventions existantes.
8. Respecter strictement les numérotations suivantes :
   - UC-R01 à UC-R12 pour Réception ;
   - UC-S01 à UC-S14 pour Stockage & Inventaire ;
   - UC-E01 à UC-E15 pour Commandes & Expédition ;
   - UC-Y01 à UC-Y07 pour Yard & Quais ;
   - UC-RES01 à UC-RES10 pour Ressources & Infrastructures.
9. Respecter la classification :
   - Core = nécessaire au fonctionnement WMS ;
   - Smart = améliore la décision par données, optimisation ou ML ;
   - Optional = dépend d’une infrastructure spécifique.
10. Supprimer tout encadré dont le titre commente le rapport lui-même :
    - “Transition vers...”
    - “Principe retenu”
    - “Ce que X ne montre pas”
    - “Fondements documentaires...”
    Le contenu utile doit être fusionné dans les paragraphes, sans encart visuel.
11. Conserver uniquement l’encart “Problématique directrice”.
12. Vérifier tous les renvois aux figures et tableaux.
13. Générer une version PDF propre.
14. Générer aussi une version modifiable :
    - soit DOCX propre ;
    - soit projet LaTeX complet si je demande la migration.

Important :
Le rapport doit rester humain, académique et homogène. Il ne doit pas ressembler à un document généré automatiquement. Les paragraphes doivent être fluides, les transitions naturelles, et les schémas doivent être suffisamment lisibles pour un jury.

Contexte métier à respecter :
Le Smart WMS proposé est organisé en couches :
- systèmes externes ;
- cœur opérationnel WMS ;
- gestion des tâches ;
- données de référence ;
- stockage OLTP / OLAP-DWH ;
- ressources & infrastructures ;
- intelligence & aide à la décision ;
- terminaux et appareils terrain.

Le benchmark a retenu :
- Manhattan Active : unification de l’exécution ;
- SAP EWM : richesse du modèle métier ;
- Oracle WMS : orchestration commande → wave → allocation → tâches → exécution.

Ne pas transformer le rapport en document purement technique. On est encore dans une démarche de conception métier, fonctionnelle et applicative.

Livrables attendus :
- rapport PDF final propre ;
- fichier source modifiable ;
- dossier figures propre ;
- liste des corrections réalisées ;
- liste des points restant à valider manuellement.
```

---

# Prompt spécialisé pour migration LaTeX

Utiliser ce prompt si l’objectif est de reconstruire le rapport proprement en LaTeX.

```text
Tu es un expert LaTeX et rédaction de rapports de stage d’ingénierie.

Je veux transformer mon rapport Smart WMS actuel en projet LaTeX professionnel.

Objectif :
Créer un projet LaTeX clair, maintenable, académique et prêt à compiler en PDF.

Structure attendue :

rapport-smart-wms/
├── main.tex
├── config/
│   ├── packages.tex
│   ├── style.tex
│   └── commands.tex
├── chapters/
│   ├── 00_remerciements.tex
│   ├── 01_introduction.tex
│   ├── 02_chapitre1_organisme.tex
│   ├── 03_chapitre2_benchmark.tex
│   ├── 04_chapitre3_besoins_use_cases.tex
│   ├── 05_chapitre4_architecture_fonctionnelle.tex
│   ├── 06_chapitre5_modelisation_uml.tex
│   ├── 07_chapitre6_architecture_applicative.tex
│   ├── 08_chapitre7_validation_limites.tex
│   └── 09_conclusion.tex
├── figures/
│   ├── chapitre1/
│   ├── chapitre2/
│   ├── chapitre3/
│   ├── chapitre4/
│   └── uml/
├── tables/
├── bibliography/
│   └── references.bib
├── annexes/
│   ├── plantuml/
│   └── schemas/
└── README.md

Règles :
1. Utiliser une classe adaptée : report ou memoir.
2. Langue principale : français.
3. Utiliser babel français.
4. Numérotation des figures par chapitre : Figure 3.1, Figure 4.1...
5. Numérotation des tableaux par chapitre : Tableau 3.1, Tableau 4.1...
6. Table des matières automatique.
7. Liste des figures et liste des tableaux si nécessaire.
8. Bibliographie propre avec BibTeX ou biblatex.
9. Utiliser des environnements propres pour :
   - tableaux longs ;
   - encadrés rares ;
   - figures ;
   - notes méthodologiques.
10. Ne pas multiplier les encadrés.
11. Conserver uniquement l’encart “Problématique directrice”.
12. Prévoir des annexes pour UML et PlantUML.
13. Garder le style professionnel :
    - bleu marine comme couleur principale ;
    - beaucoup d’espace blanc ;
    - titres sobres ;
    - pas d’effet décoratif inutile.
14. Importer les figures existantes ou les redessiner proprement en TikZ si nécessaire.
15. Vérifier que le PDF compile sans erreur.

Procédure :
- Commencer par créer la structure du projet.
- Migrer chapitre par chapitre.
- Ne pas réécrire le contenu sans validation.
- Signaler les endroits où le contenu doit être amélioré.
- Compiler le PDF à chaque étape.
- Corriger les erreurs LaTeX.
- Fournir à la fin un PDF final et le projet source complet.
```

---

## 12. Checklist qualité avant livraison finale

Avant de considérer le rapport comme final, vérifier :

- [ ] couverture sobre et propre ;
- [ ] sommaire automatique ;
- [ ] pagination cohérente ;
- [ ] figures lisibles ;
- [ ] aucune figure avec texte hors boîte ;
- [ ] tableaux non coupés de manière illisible ;
- [ ] titres homogènes ;
- [ ] citations homogènes ;
- [ ] pas d’encarts inutiles ;
- [ ] pas de transition artificielle ;
- [ ] classification Core / Smart / Optional cohérente ;
- [ ] use cases numérotés correctement ;
- [ ] données de référence et OLTP / OLAP-DWH traités dans le chapitre architecture ;
- [ ] UML cohérent avec les use cases ;
- [ ] bibliographie cohérente ;
- [ ] PDF vérifié page par page.
