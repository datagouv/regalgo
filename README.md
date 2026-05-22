# Regalgo — Wrapper Python pour standardiser les algorithmes publics

`regalgo` fournit les structures de données et l'outillage de validation nécessaires pour packager des algorithmes réglementaires français de façon interopérable, en s'appuyant sur les [Core Vocabularies de l'Union Européenne](https://joinup.ec.europa.eu/collection/semic-support-centre/core-vocabularies).

## Pourquoi ?

Les algorithmes publics (éligibilité, calcul de droits, conditions d'accès…) sont souvent réimplémentés en silos, avec des structures de données incompatibles et sans traçabilité vers les textes réglementaires qui les fondent.

`regalgo` propose un socle commun :

- des **modèles de données normalisés** alignés sur les standards européens (Core Person Vocabulary, CCCEV) ;
- une **sortie traçable** (`AlgoResult`) qui lie chaque résultat à son identifiant d'algorithme et à la réglementation applicable ;
- une **validation SHACL optionnelle** des entrées contre les shapes du Core Person Vocabulary 2.1.0.

## Installation

```bash
pip install regalgo
```

Avec la validation SHACL (optionnel) :

```bash
pip install 'regalgo[shacl]'
```

## Concepts clés

| Classe | Rôle |
|---|---|
| `AlgoInput` | Entrée normalisée passée à un algorithme réglementaire |
| `AlgoResult` | Sortie normalisée : valeur + identifiant algo + texte réglementaire + snapshot des entrées |
| `PersonInput` | Représentation d'une personne alignée sur `cv:` (Core Person Vocabulary) et `cccev:`. Permet de créer un `AlgoInput`|
| `ValidationResult` | Résultat de la validation SHACL d'un `PersonInput` |

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

### Validation SHACL (optionnel)

```python
from regalgo import validate_person_input

result = validate_person_input(personne)
if not result:
    for violation in result.violations:
        print(violation)
```

## Exemple de réutilisation : algorithme droit de vote

[regalgo-civique-droit-vote](https://github.com/qloridant/regalgo-civique-droit-vote) implémente l'algorithme d'éligibilité au droit de vote (Code électoral, Art. L.2 à L.7 et L.O. 227-1) en s'appuyant sur ce wrapper.


## Structure du dépôt

```
src/regalgo/
├── algorithm.py      # Structures de données : AlgoInput, AlgoResult, PersonInput
├── validatation.py   # Validation SHACL optionnelle
└── shapes/
    └── cpv_person.ttl  # Shapes SHACL dérivées du Core Person Vocabulary 2.1.0
tests/
└── test_validation.py
```

## Développement

```bash
# Installer les dépendances (dont les extras SHACL pour les tests)
poetry install --extras shacl

# Lancer les tests
pytest
```

## Standards de référence

- [Core Person Vocabulary 2.1.0](https://semiceu.github.io/Core-Person-Vocabulary/releases/2.1.0/) —  SEMIC
- [Core Criterion and Evidence Vocabulary (CCCEV)](https://semiceu.github.io/CCCEV/) —SEMIC
