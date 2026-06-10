
from sbs_utils.procedural.roles import has_role

from data.missions.common.pirate_features_definitions import is_neutral_civilian, is_pirate, is_tsn

# ================================
#  Pirates
# ================================

# _lib/procedural_terrain.py

def color_map_pirate_station():
    return "#036910"

def color_map_neutral_civilian_station():
    return "#15f"

# prefabs/pirate_npc_noncombat.mast

def color_map_pirate_npc():
    return "#036910"

# ================================
#  Misc
# ================================

def get_comms_message_title_color(npc_id):
    if is_tsn(npc_id):
        if has_role(npc_id, "station"):
            # from preferences.json
            # "gui-color-friendly-station": "#15f",
            return "#15f"
        else:
            # from preferences.json
            # "gui-color-friendly-ship": "#0ff",
            return "#0ff"
    elif is_pirate(npc_id):
        if has_role(npc_id, "station"):
            return color_map_pirate_station()
        else:
            return color_map_pirate_npc()
    elif is_neutral_civilian(npc_id):
        return color_map_neutral_civilian_station()
    else:
        return None
