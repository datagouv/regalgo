# Regalgo — Librairie pour standardiser les algorithmes publics en python

`regalgo` permet de standardiser un algorithme en python afin de bénéficier des **services automatisés de [regles.data.gouv.fr](https://shallowred.github.io/regles.data.gouv.fr-frontend-poc/mvp/regles/)** :
* référencement
* documentation
* API
* simulateur
* explicabilité
* simplification des signatures de fonctions grâce aux champs déjà disponibles dans API Particulier
* ...


## Pourquoi ?

Les algorithmes publics (éligibilité, calcul de droits, conditions d'accès…) sont souvent réimplémentés en silos, avec des structures de données incompatibles et sans traçabilité vers les textes réglementaires qui les fondent.


## Comment ?

`regalgo` propose un socle commun :

- une harmonisation et une traçabilité des **données entrantes** alignées sur API Particulier
- une **sortie traçable** (`AlgoResult`) qui lie chaque résultat à son identifiant d'algorithme et à la réglementation applicable ;
- une méthode `compute()`, porte d'entrée de votre code réglementaire
- une aide à la saisie des metadonnées nécessaires au réferencement (fichier `metadata.json`, lu par [regles.data.gouv.fr])


| Classe | Rôle |
|---|---|
| `AlgoInput` | Entrée normalisée passée à un algorithme réglementaire |
| `AlgoResult` | Sortie normalisée : valeur + identifiant algo + texte réglementaire + snapshot des entrées |
| `PersonInput` | Représentation d'une personne alignée sur `cv:` (Core Person Vocabulary) et `cccev:`. Permet de créer un `AlgoInput`|

## Installation

```bash
pip install regalgo
```

## Exemple d'utilisation
### Code

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


### Projet : Algorithme droit de vote (POC)

[regalgo-civique-droit-vote](https://github.com/qloridant/regalgo-civique-droit-vote) implémente l'algorithme d'éligibilité au droit de vote (Code électoral, Art. L.2 à L.7 et L.O. 227-1) en s'appuyant sur cette librairie.


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
