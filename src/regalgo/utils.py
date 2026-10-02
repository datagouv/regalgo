from datetime import date

def compute_age(birth_date: date, reference_date: date) -> int:
    """Âge révolu à `reference_date` (déterministe, pas de date.today() ici)."""
    return reference_date.year - birth_date.year - (
        (reference_date.month, reference_date.day)
        < (birth_date.month, birth_date.day)
    )