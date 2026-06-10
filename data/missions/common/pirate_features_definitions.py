"""
For definitions fundamental to features that are (traditionally) for pirates.
Expect these to be referenced by many different places in the code.
"""
from sbs_utils.procedural.execution import get_shared_variable
from sbs_utils.procedural.inventory import get_inventory_value, set_inventory_value
from sbs_utils.procedural.query import to_space_object
from sbs_utils.procedural.roles import has_role

# ----- looting -----

def can_loot(player_ship_id):
    return is_pirate(player_ship_id) or is_civilian_air_patrol(player_ship_id)

def loot_rendezvous_radius():
    return 500

def is_looted(ship_id):
    """ Returns True if the ship has already had its loot taken, otherwise False """
    return get_inventory_value(ship_id, _inventory_key_is_looted())

def set_looted(ship_id):
    """ Call this to indicate that the ship is having its loot taken """
    set_inventory_value(ship_id, _inventory_key_is_looted(), True)

def _inventory_key_is_looted():
    return "is_looted"

def looting_comms_messages_color():
    return get_shared_variable("surrender_color", "#ff0")

def set_auto_looting(player_ship_id, auto_loot):
    set_inventory_value(player_ship_id, _inventory_key_is_not_auto_looting(), not auto_loot)

def is_auto_looting(player_ship_id):
    return not get_inventory_value(player_ship_id, _inventory_key_is_not_auto_looting())

def _inventory_key_is_not_auto_looting():
    return "is_not_auto_looting"

# ----- "side" definitions -----
# TODO update implementations when ship sides get more fleshed out in vanilla?

def is_raider(ship_id):
    """ Excludes enemies that have surrendered """
    return has_role(ship_id, "raider")

def is_pirate(ship_id):
    origin = get_origin(ship_id)
    return origin == "pirate"

# It would be nice if shipData.yaml supported a field for military vs. civilian.
# But it doesn't have one, so use these lists of ship type keys instead.

def is_pirate_civilian(ship_id):
    if not is_pirate(ship_id):
        return False
    ship_type_key = get_ship_type_key(ship_id)
    pirate_civilian_ship_type_keys = {
        "pirate_shuttle_ef",
        "pirate_cargo_ef",
        "pirate_science_ef",
        "starbase_pirate_market_civil_ef"
    }
    return ship_type_key in pirate_civilian_ship_type_keys

def is_pirate_military(ship_id):
    if not is_pirate(ship_id):
        return False
    ship_type_key = get_ship_type_key(ship_id)
    pirate_military_ship_type_keys = {
        "pirate_fighter_ef",
        "pirate_bomber_ef",
        "pirate_strongbow_ef",
        "pirate_brigantine_ef",
        "pirate_longbow_ef",
        "pirate_advanced_longbow_ef",
        "pirate_toranado_ef",
        "pirate_ximni_graybeards_ghost_ef"
    }
    return ship_type_key in pirate_military_ship_type_keys

def is_neutral_civilian(ship_id):
    # Stub for now
    # TODO designate some station types that return True later
    return False

def is_tsn(ship_id):
    origin = get_origin(ship_id)
    return origin == "tsn"

def is_tsn_civilian(ship_id):
    if not is_tsn(ship_id):
        return False
    ship_type_key = get_ship_type_key(ship_id)
    civilian_tsn_ship_type_keys = {
        "starbase_civil",
        "starbase_industry",
        "starbase_science",
        "tsn_shuttle",
        "transport_ship",
        "luxury_liner",
        "cargo_ship",
        "science_ship"
    }
    return ship_type_key in civilian_tsn_ship_type_keys

def is_tsn_military(ship_id):
    if not is_tsn(ship_id):
        return False
    ship_type_key = get_ship_type_key(ship_id)
    military_tsn_ship_type_keys = {
        "starbase_command",
        "tsn_light_cruiser",
        "tsn_fighter",
        "tsn_bomber",
        "tsn_battle_cruiser",
        "tsn_carrier",
        "tsn_light_carrier",
        "tsn_battleship",
        "tsn_mine_layer",
        "tsn_warpster",
        "tsn_juggernaut",
        "tsn_missile_cruiser",
        "tsn_destroyer",
        "tsn_dreadnought",
        "tsn_escort",
        "tsn_heavy_cruiser",
        "tsn_scout"
    }
    return ship_type_key in military_tsn_ship_type_keys

def is_ximni(ship_id):
    origin = get_origin(ship_id)
    return origin == "ximni"

def is_civilian_air_patrol(ship_id):
    return get_origin(ship_id) == "cap"

# There may be other cases too besides the above
# e.g. apparently players can play as arvonian ships now?
# And custom missions might put player ships on custom sides too

# ----- helpers -----

def get_origin(ship_id):
    ship_object = to_space_object(ship_id)
    if ship_object is None:
        return None
    else:
        return ship_object.origin

def get_ship_type_key(ship_id):
    """ Get this ship's ship type key (the one used in shipData.yaml) """
    ship_object = to_space_object(ship_id)
    if ship_object is None:
        return None
    else:
        return ship_object.art_id
