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

- une **entrée typée** (`AlgoInput`) : chaque algorithme déclare les variables qu'il attend, ce qui permet de valider les données et de générer automatiquement le schéma JSON (simulateur, documentation, API) ;
- des **modèles sources** (comme `FCPersonInput`) alignés sur [API Particulier](https://particulier.api.gouv.fr/catalogue) et FranceConnect, pour harmoniser et tracer les données entrantes ;
- une **sortie traçable** (`AlgoResult`) qui lie chaque résultat à son identifiant d'algorithme, à la réglementation applicable et à un snapshot des entrées ;
- une classe `PublicRule`, générique sur le type d'entrée, dont la méthode `compute()` est la porte d'entrée de votre code réglementaire ;
- une aide à la saisie des métadonnées nécessaires au référencement (fichier `metadata.json`, lu par [regles.data.gouv.fr]).

## Installation

Avec [uv](https://docs.astral.sh/uv/) (recommandé) :

```bash
uv add --index testpypi=https://test.pypi.org/simple/ your-package
```

Avec pip :

```bash
pip install -i https://test.pypi.org/simple/ regalgo==0.0.3
```


## Concepts clés

| Classe | Rôle |
|---|---|
| `AlgoInput` | Classe de base (Pydantic) à sous-classer : déclare les champs typés qu'attend un algorithme. Fournit `input_schema()` (schéma JSON) et `snapshot()` |
| `AlgoResult` | Sortie normalisée : valeur + identifiant algo + texte réglementaire + snapshot des entrées |
| `PublicRule[I]` | Classe de base d'un algorithme, générique sur son type d'entrée `I` (un `AlgoInput`). On implémente `compute()` ; `self.result()` construit l'`AlgoResult` |
| `InputSource` | Contrat (Protocol) des modèles sources : tout objet qui sait produire un `AlgoInput` via `to_algo_input()` |
| `FCPersonInput` | Modèle source prêt à l'emploi : personne alignée sur l'identité pivot de FranceConnect |
| `compute_age` | Utilitaire : âge révolu à une date de référence donnée |


## Exemple d'utilisation

### 1. Déclarer le contrat d'entrée

Chaque algorithme décrit ses entrées en sous-classant `AlgoInput`.

```python
from datetime import date

from pydantic import Field
from regalgo import AlgoInput, AlgoResult, PublicRule


class DroitVoteInput(AlgoInput):
    age: int = Field(ge=0)
    nationalite_francaise: bool
    capacite_civique: bool
    reference_date: date  # date utilisée pour calculer l'âge (traçabilité)
```

### 2. Implémenter la règle

`PublicRule[DroitVoteInput]` indique le type d'entrée : l'IDE et mypy savent que `algo_input` est un `DroitVoteInput`.

```python
class DroitVote(PublicRule[DroitVoteInput]):
    def compute(self, algo_input: DroitVoteInput) -> AlgoResult:
        eligible = (
            algo_input.age >= 18
            and algo_input.nationalite_francaise
            and algo_input.capacite_civique
        )
        return self.result(eligible, algo_input)
```

Le fichier `metadata.json` est lu à côté du fichier qui définit la règle (`DroitVote`).

### 3. Exécuter

```python
resultat = DroitVote().compute(
    DroitVoteInput(
        age=35,
        nationalite_francaise=True,
        capacite_civique=True,
        reference_date=date(2026, 1, 1),
    )
)

print(resultat.value)            # True
print(resultat.algo_id)          # 'droit-vote'
print(resultat.inputs_snapshot)
# {'age': 35, 'nationalite_francaise': True, 'capacite_civique': True,
#  'reference_date': '2026-01-01'}
```

Les données sont validées à la construction de `DroitVoteInput` : un âge négatif ou un champ manquant lève une `ValidationError` avant même l'appel à `compute()`.

Le schéma des entrées, utilisé pour générer le simulateur et la documentation, est disponible directement :

```python
DroitVoteInput.input_schema()  # JSON Schema
```

### 4. Brancher une source de données

Les données réelles ne sont pas déjà au format de l'algorithme (date de naissance plutôt qu'âge, code pays plutôt qu'un booléen…). Un **modèle source** porte les données brutes et sait les projeter vers l'`AlgoInput` de l'algorithme, en calculant les champs dérivés.

```python
from typing import Any

from pydantic import BaseModel
from regalgo import compute_age


class Demandeur(BaseModel):
    birth_date: date
    nationality: str          # ISO 3166-1 alpha-2
    civil_rights_intact: bool

    def to_algo_input(self, context: dict[str, Any] | None = None) -> DroitVoteInput:
        reference_date = (context or {}).get("reference_date") or date.today()
        return DroitVoteInput(
            age=compute_age(self.birth_date, reference_date),
            nationalite_francaise=self.nationality.upper() == "FR",
            capacite_civique=self.civil_rights_intact,
            reference_date=reference_date,
        )


demandeur = Demandeur(birth_date="2010-03-02", nationality="FR", civil_rights_intact=True)
algo_input = demandeur.to_algo_input({"reference_date": date(2026, 1, 1)})

DroitVote().compute(algo_input).value  # False (15 ans)
```

Tout objet qui expose `to_algo_input()` respecte le contrat `InputSource`. La librairie fournit des sources prêtes à l'emploi, comme `FCPersonInput` (identité pivot FranceConnect), que vous pouvez compléter avec les données qu'elle ne couvre pas (nationalité, droits civiques…).
