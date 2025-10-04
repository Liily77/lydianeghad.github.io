# scripts/scraping/ingestion_state.py
# -------------------------------------------------------------------
# Petit module pour mémoriser l'état d'ingestion par hôtel :
# - on enregistre le dernier nb_avis_total vu
# - on le relit au prochain run pour ne scraper que la différence
# Le fichier d'état est stocké en JSON : data/state/ingestion_state.json
# -------------------------------------------------------------------

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, Any

STATE_PATH = Path("data/state/ingestion_state.json")


def load_state() -> Dict[str, Any]:
    """Charge l'état (JSON). Retourne {} si le fichier n'existe pas."""
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        return {}
    except json.JSONDecodeError:
        # Si le JSON est corrompu, on repart propre
        return {}


def save_state(state: Dict[str, Any]) -> None:
    """Écrit l'état de manière atomique (fichier temporaire + replace)."""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_PATH)


def get_prev_total(hotel_key: str) -> int:
    """Dernier nb_avis_total mémorisé pour l'hôtel (0 si inconnu)."""
    state = load_state()
    try:
        return int(state.get(hotel_key, {}).get("nb_avis_total", 0))
    except (TypeError, ValueError):
        return 0


def set_prev_total(hotel_key: str, nb_avis_total: int) -> None:
    """Met à jour le nb_avis_total courant pour l'hôtel."""
    state = load_state()
    state[hotel_key] = {
        **state.get(hotel_key, {}),
        "nb_avis_total": int(nb_avis_total),
    }
    save_state(state)


# (Optionnel) : petits helpers pour tracer les runs
def get_last_run(hotel_key: str) -> str | None:
    """Retourne un timestamp (str) du dernier run si présent."""
    return load_state().get(hotel_key, {}).get("last_run")


def set_last_run(hotel_key: str, ts: str) -> None:
    """Enregistre un timestamp (str) du dernier run."""
    state = load_state()
    state[hotel_key] = {
        **state.get(hotel_key, {}),
        "last_run": ts,
    }
    save_state(state)
