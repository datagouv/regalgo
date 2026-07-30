# Regalgo — Wrapper Python pour standardiser les algorithmes publics

`regalgo` fournit les structures de données pour packager des algorithmes réglementaires français de façon interopérable.

## Pourquoi ?

Les algorithmes publics (éligibilité, calcul de droits, conditions d'accès…) sont souvent réimplémentés en silos, avec des structures de données incompatibles et sans traçabilité vers les textes réglementaires qui les fondent.

`regalgo` propose un socle commun :

- des **modèles de données normalisés** alignés sur les standards européens (Core Person Vocabulary, CCCEV) ;
- une **sortie traçable** (`AlgoResult`) qui lie chaque résultat à son identifiant d'algorithme et à la réglementation applicable ;

## Installation

```bash
pip install regalgo
```


## Concepts clés

| Classe | Rôle |
|---|---|
| `AlgoInput` | Entrée normalisée passée à un algorithme réglementaire |
| `AlgoResult` | Sortie normalisée : valeur + identifiant algo + texte réglementaire + snapshot des entrées |
| `PersonInput` | Représentation d'une personne alignée sur `cv:` (Core Person Vocabulary) et `cccev:`. Permet de créer un `AlgoInput`|

## Exemple d'utilisation

```python
from datetime import date
from regalgo import PersonInput

# Décrire une personne avec les Core Vocabularies EU ISA²
personne = PersonInput(
    cv_nationality="FR",           # ISO 3166-1 alpha-2
    schema_birth_date=date(1990, 6, 15),
    cccev_civil_rights_intact=True,
    cccev_electoral_list_registered=True,
    cv_domicile_country="FR",
)

# Convertir en AlgoInput (calcule l'âge automatiquement)
algo_input = personne.to_algo_input()
print(algo_input.data)
# {
#   'nationalite_francaise': True,
#   'citoyennete_ue': True,
#   'domicile_france': True,
#   'age': 35,
#   'capacite_civique': True,
#   'inscrit_listes_electorales': True
# }
```


## Exemple de réutilisation : algorithme droit de vote

[regalgo-civique-droit-vote](https://github.com/qloridant/regalgo-civique-droit-vote) implémente l'algorithme d'éligibilité au droit de vote (Code électoral, Art. L.2 à L.7 et L.O. 227-1) en s'appuyant sur ce wrapper.


## CLI

### `regalgo init` — initialiser un nouveau projet

```bash
regalgo init mon-algo
```

La commande pose une série de questions pour configurer le fichier `metadata.json` :

```
Configuration du fichier metadata.json :
  Titre de l'algorithme [mon-algo]: Éligibilité à la prestation X
  Description de l'algorithme [Description de l'algorithme]: Calcule l'éligibilité...
  Source réglementaire (URL ou référence légale) []: https://legifrance.gouv.fr/...
  Description de la référence réglementaire [Référence réglementaire]: Décret n° 2024-XXX
```

Pour un usage non interactif (CI/CD), utilisez `--no-input` :

```bash
regalgo init mon-algo --no-input
```

Options :

| Option | Description |
|---|---|
| `--output-dir`, `-o` | Répertoire parent où créer le projet (défaut : `.`) |
| `--no-input` | Utilise les valeurs par défaut, sans poser de questions |


## Développement

```bash
# Installer les dépendances
poetry install 

# Lancer les tests
pytest
```