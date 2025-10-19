# Figth/fight.py
from __future__ import annotations
from typing import List, Optional
import random

# En el launcher, cuando el usuario elige “Atacar”, se llama:
#   resolve_turn(player_battle, combat_enemy, combat_log)
# y después el launcher chequea si alguien murió (Control_vida).


def _crit_threshold_for_player(player_type: str): #Funcion de Criticosv
    """
    Umbral de crítico según clase del jugador.
    - Paladin / Wizard: crit con 18, 19, 20 → umbral 18
    - Archer:           crit con 14..20     → umbral 14

    """
    # Sirve para analizar que probabilidad de critico tiene el personaje
    t = (player_type).strip().lower() # Toma el tipo del personaje
    if t == "archer":
        return 14
    # paladin y wizard comparten umbral 18
    return 18

def _player_base_damage(player, enemy):
    """
    Daño base (antes de crítico) según clase.
    - Paladin: usa ATK * 1
    - Wizard:  usa MAGE * 1.4 
    - Archer:  usa ACCURACY * 1.2 

    También se resta DEF del enemigo (clásico).
    Siempre devolvemos al menos 1.0 de daño base.
    """
    t = (player.type).strip().lower()
    if t == "wizard":
        return max(1.0, (player.mage  * 1.4 - enemy.defense))
    if t == "archer":
        return max(1.0, (player.accuracy * 1.2 - enemy.defense))
    # paladin (default)
    return max(1.0, (player.atk - enemy.defense))

# Log = detalles de la batalla, rng = Dado 
def _player_attack_once(player, enemy, log: List[str], rng: Optional[random.Random] = None):
    """
    Un solo golpe del jugador al enemigo (no decide orden, solo ejecuta el golpe).
    - Tira un d20 para ver si es crítico usando el umbral por clase.
    - Si es crítico: daño base * 2.
    - Redondeo y clamp a int >= 1.
    - Baja la vida del enemigo y anota en el log.
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
    Un solo golpe del enemigo al jugador (misma idea que el del jugador).
    - Crítico del enemigo si tirada >= 19 (como venías usando).
    - Daño base = max(1, enemy.atk - player.defense)
    - Si crítico, *2.
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
    - Orden de prioridad : si enemy.SPD <= player.ACCURACY, pega primero el jugador.
    - Si el defensor sobrevive, responde (o sea, pueden pegar ambos en un turno).
    - Usa las reglas de daño y críticos pedidas:
        * Paladin: daño con ATK; crit 18+
        * Wizard:  daño con MAGE*1.4; crit 18+
        * Archer:  daño con ACC*1.2; crit 14+
      Enemigo: crit 19+
    - Mutación in-place de vida y log (no retorna nada, deja todo listo
      para que el launcher luego llame a Control_vida(...) y salte de nodo si corresponde).

    Llamado desde: launcher.run_game(), dentro del bloque de combate,
    cuando el jugador elige “Atacar” y confirma con Enter.
    """
    r = rng or random

    # Quién pega primero
    player_first = (enemy.spd <= player_battle.accuracy)

    if player_first:
        _player_attack_once(player_battle, enemy, log, r)
        if enemy.vida > 0:
            _enemy_attack_once(enemy, player_battle, log, r)
    else:
        _enemy_attack_once(enemy, player_battle, log, r)
        if player_battle.vida > 0:
            _player_attack_once(player_battle, enemy, log, r)
