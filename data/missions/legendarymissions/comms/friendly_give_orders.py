from data.missions.common.docking_permissions import test_player_capital_pirate_ship_dock_at_tsn, dock_attempt_result_allowed_pirate_uneasy_alliance
from data.missions.common.pirate_features_definitions import is_pirate, is_tsn

def is_npc_ship_compliant(npc_ship_id, player_ship_id):
    """
    Returns True if the NPC ship will follow orders given by the player ship.
    Otherwise, returns False.
    """
    if is_pirate(npc_ship_id):
        # Pirate npcs will comply with CAP and ximni players (in addition to pirate players)
        return not is_tsn(player_ship_id)
    elif is_tsn(npc_ship_id):
        if is_pirate(player_ship_id):
            docking_permissions = test_player_capital_pirate_ship_dock_at_tsn(player_ship_id, skip_is_pirate_check=True)
            return docking_permissions == dock_attempt_result_allowed_pirate_uneasy_alliance()
        else:
            # TSN npcs will always comply with CAP, Ximni, and (obviously) TSN players
            return True
    else: # npc is ximni or something else
        return True
