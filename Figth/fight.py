# Figth/fight.py
from __future__ import annotations
from typing import List, Optional
import random
import math

def _crit_threshold_for_player(player_type: str) -> int:
    """
    Umbral de crítico según clase del jugador.
    - Paladin / Wizard: crit con 18, 19, 20  → umbral 18
    - Archer:           crit con 14..20      → umbral 14
    """
    t = (player_type or "").strip().lower()
    if t == "archer":
        return 14
    # paladin y wizard comparten umbral 18
    return 18

def _player_base_damage(player, enemy) -> float:
    """
    Daño base (antes de crítico) según clase.
    - Paladin: usa ATK
    - Wizard:  usa MAGE * 1.4
    - Archer:  usa ACCURACY * 1.2 (mantengo tu regla previa)
    """
    t = (player.type or "").strip().lower()
    if t == "wizard":
        return max(1.0, (player.mage  * 1.4- enemy.defense))
    if t == "archer":
        return max(1.0, (player.accuracy * 1.2 - enemy.defense))
    # paladin (default)
    return max(1.0, (player.atk - enemy.defense))

def _player_attack_once(player, enemy, log: List[str], rng: Optional[random.Random] = None) -> None:
    """
    Un solo golpe del jugador al enemigo.
    - Determina crítico según clase.
    - Redondea daño a int.
    - Loguea el resultado.
    """
    r = rng or random
    roll = r.randint(1, 20)
    crit_threshold = _crit_threshold_for_player(player.type)
    base = _player_base_damage(player, enemy)

    if roll >= crit_threshold:
        dmg = int(max(1, round(base * 2)))
        enemy.vida -= dmg
        log.append(f"¡{player.name} mete CRÍTICO! ({dmg} de daño).")
    else:
        dmg = int(max(1, round(base)))
        enemy.vida -= dmg
        log.append(f"{player.name} ataca e inflige {dmg} de daño.")

def _enemy_attack_once(enemy, player, log: List[str], rng: Optional[random.Random] = None) -> None:
    """
    Un solo golpe del enemigo al jugador.
    - Crítico del enemigo si tirada >= 19 (como venías usando).
    """
    r = rng or random
    roll = r.randint(1, 20)
    base = max(1, enemy.atk - player.defense)
    if roll >= 19:
        dmg = int(max(1, base * 2))
        player.vida -= dmg
        log.append(f"{enemy.name} asesta un CRÍTICO ({dmg}) sobre {player.name}.")
    else:
        dmg = int(max(1, base))
        player.vida -= dmg
        log.append(f"{enemy.name} golpea por {dmg} de daño.")

def resolve_turn(player_battle, enemy, log: List[str], rng: Optional[random.Random] = None) -> None:
    """
    Resuelve un 'turno' completo de combate:
    - Orden de prioridad (como tu regla): si enemy.SPD <= player.ACCURACY, pega primero el jugador.
    - Si el defensor sobrevive, responde.
    - Usa la tabla de daño y críticos pedida (Paladin / Wizard / Archer).
    - Mutación in-place de vida y log (sin devolver nada).
    """
    r = rng or random

    # ¿Quién pega primero?
    player_first = (enemy.spd <= player_battle.accuracy)

    if player_first:
        _player_attack_once(player_battle, enemy, log, r)
        if enemy.vida > 0:
            _enemy_attack_once(enemy, player_battle, log, r)
    else:
        _enemy_attack_once(enemy, player_battle, log, r)
        if player_battle.vida > 0:
            _player_attack_once(player_battle, enemy, log, r)
