from datetime import date

from pydantic import Field,BaseModel
from regalgo import AlgoInput, AlgoResult, PublicRule, compute_age
from typing import Any


# Définitions des données

class DroitVoteInput(AlgoInput):
    age: int = Field(ge=0)
    nationalite_francaise: bool
    capacite_civique: bool
    reference_date: date  # date utilisée pour calculer l'âge (traçabilité)

class Demandeur(BaseModel):
    birth_date: date
    nationality: str
    civil_rights_intact: bool

    def to_algo_input(self, context: dict[str, Any] | None = None) -> DroitVoteInput:
        reference_date = (context or {}).get("reference_date") or date.today()
        return DroitVoteInput(
            age=compute_age(self.birth_date, reference_date),
            nationalite_francaise=self.nationality.upper() == "FR",
            capacite_civique=self.civil_rights_intact,
            reference_date=reference_date,
        )

demandeur_mineur = Demandeur(birth_date="2010-03-02", nationality="FR", civil_rights_intact=True)
algo_input_mineur = demandeur_mineur.to_algo_input({"reference_date": date(2026, 1, 1)})
demandeur_majeur = Demandeur(birth_date="2000-03-02", nationality="FR", civil_rights_intact=True)
algo_input_majeur = demandeur_majeur.to_algo_input({"reference_date": date(2026, 1, 1)})

# Définitions de la règle

class DroitVote(PublicRule[DroitVoteInput]):
    def compute(self, algo_input: DroitVoteInput) -> AlgoResult:
        eligible = (
            algo_input.age >= 18
            and algo_input.nationalite_francaise
            and algo_input.capacite_civique
        )
        return self.result(eligible, algo_input)


# Exécution :

# -- Demandeur mineur

resultat = DroitVote().compute(algo_input_mineur)

print(resultat)
print(resultat.value)
print(resultat.inputs_snapshot)

# -- Demandeur majeur

resultat = DroitVote().compute(algo_input_majeur)

print(resultat)
print(resultat.value)
print(resultat.inputs_snapshot)
