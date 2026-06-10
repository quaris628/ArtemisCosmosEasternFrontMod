from enum import Enum
from random import choice, getrandbits, uniform
from math import tau, sin, cos

from sbs_utils.vec import Vec3
from sbs_utils.procedural.comms import comms_broadcast, comms_receive
from sbs_utils.procedural.execution import set_variable
from sbs_utils.procedural.inventory import get_inventory_value, set_inventory_value
from sbs_utils.procedural.roles import add_role
from sbs_utils.procedural.ship_data import get_ship_data_for

from data.missions.common.spawn_wreck import spawn_wreck

def spawn_wrecks_and_derelicts_around(station_position, station_id, is_lethal_terrain_enabled):
    
    # Mine ring can spawn between 1200 and 1500 away (sbs_utils/procedural/terrain.py or _lib/procedural_terrain.py)
    # Friendly ships can spawn between 3500 and 5300 away (fleets/map_common.mast)
    # Hypothetically, the closest two stations could get is ~4545
    # (Max possible station count is 22, and that gives a minimum
    # Z-axis separation of 100000/22 = ~4545)
    # So put wrecks/derelicts in the unoccupied ring between mines (if applicable)
    # and friendly ships, to prevent overlapping with already-occupied space.
    
    if is_lethal_terrain_enabled:
        min_radius = 2000
        hullpoints_target = 30
        wrecks_count_target = 15
    else:
        min_radius = 1200
        hullpoints_target = 50
        wrecks_count_target = 20
    
    hullpoints = 0
    wrecks_count = 0
    for radius in range(min_radius, 3000, 110):
        wreck_position = get_random_position_in_cylinder_around(station_position, radius, 300)
        
        if hullpoints < hullpoints_target:
            try_spawn_derelict_ship = True
        if wrecks_count < wrecks_count_target:
            try_spawn_wreck = True
        
        if try_spawn_derelict_ship and try_spawn_wreck:
            try_spawn_derelict_ship = getrandbits(1)
            try_spawn_wreck = not try_spawn_derelict_ship
            
        if try_spawn_derelict_ship:
            wreck_spawn_data = spawn_random_derelict_tsn_ship(wreck_position)
        elif try_spawn_wreck:
            wreck_spawn_data = spawn_random_tsn_wreck(wreck_position)
        else:
            break
        
        set_owned_by_station_id(wreck_spawn_data.id, station_id)

def get_random_position_in_cylinder_around(position, horizontal_radius, max_vertical_offset):
    angle_radians = uniform(0, tau)
    x = position.x + cos(angle_radians) * horizontal_radius
    y = position.y + uniform(-max_vertical_offset, max_vertical_offset)
    z = position.z + sin(angle_radians) * horizontal_radius
    return Vec3(x, y, z)

def spawn_random_derelict_tsn_ship(position):
    origin = "tsn"
    ship_type_key = f"derelict_{get_random_tsn_ship_type_key()}_ef"
    ship_type_data = get_ship_data_for(ship_type_key)
    original_hullpoints = ship_type_data.get("hullpoints", 1)
    name = ship_type_data.get("name", "Derelict TSN Ship")
    
    wreck_spawn_data = spawn_wreck(position, origin, original_hullpoints, ship_type_key, name=name)
    
    # Use role to differentiate derelict ships from other types of wrecks
    add_role(wreck_spawn_data.id, derelict_tsn_role_key())
    
    return wreck_spawn_data

def spawn_random_tsn_wreck(position):
    origin = "tsn"
    ship_type_key = get_random_tsn_ship_type_key()
    ship_type_data = get_ship_data_for(ship_type_key)
    original_hullpoints = ship_type_data.get("hullpoints", 1)
    
    wreck_spawn_data = spawn_wreck(position, origin, original_hullpoints)
    
    return wreck_spawn_data

def get_random_tsn_ship_type_key():
    return choice([
        "tsn_light_cruiser",
        "tsn_shuttle",
        "tsn_fighter",
        "tsn_bomber",
        "tsn_battle_cruiser",
        "tsn_carrier",
        "tsn_light_carrier",
        "tsn_battleship",
        "tsn_warpster",
        "tsn_missile_cruiser",
        "tsn_destroyer",
        "tsn_escort",
        "tsn_heavy_cruiser",
        "tsn_scout",
        "transport_ship",
        "luxury_liner",
        "cargo_ship",
        "science_ship",
    ])

def on_salvage_yard_property_destroyed(responsible_player_ship_id, owner_station_object):
    old_reputation = _get_local_salvage_yard_reputation(responsible_player_ship_id, owner_station_object.id)
    old_global_reputation = _get_global_salvage_yard_reputation(responsible_player_ship_id)
    
    new_reputation = _worsen_local_salvage_yard_reputation(responsible_player_ship_id, owner_station_object.id)
    new_global_reputation = _get_global_salvage_yard_reputation(responsible_player_ship_id)
    
    is_transition_to_ban = old_reputation != SalvageYardReputationLevel.BANNED and new_reputation == SalvageYardReputationLevel.BANNED
    is_transition_to_global_ban = old_global_reputation != SalvageYardReputationLevel.BANNED and new_global_reputation == SalvageYardReputationLevel.BANNED
    
    _send_comms_response_to_property_destroyed(responsible_player_ship_id, owner_station_object, is_transition_to_ban, is_transition_to_global_ban)
    
    # Idea for later: have each wreck's destruction decrease the station's
    # production speeds? Would require triggering on-destroyed function even
    # if no player is responsible and affecting the weapon building behavior
    # in a way that handles currently-being-produced ordinance gracefully.

def _send_comms_response_to_property_destroyed(responsible_player_ship_id, owner_station_object, is_transition_to_ban, is_transition_to_global_ban):
    set_variable("COMMS_ORIGIN_ID", responsible_player_ship_id)
    set_variable("COMMS_SELECTED_ID", owner_station_object.id)
    
    reputation = _get_local_salvage_yard_reputation(responsible_player_ship_id, owner_station_object.id)
    if reputation == SalvageYardReputationLevel.FIRST_WARNING:
        comms_receive("Hey, why are you blowing up our stock?! Stop destroying our property!", title="Stop vandalizing!")
    elif reputation == SalvageYardReputationLevel.SECOND_WARNING:
        comms_receive("That ship hull still had usable air recyclers! Last warning before I permanently ban you from this establishment.", title="Stop vandalizing!")
    elif reputation == SalvageYardReputationLevel.BANNED:
        if is_transition_to_global_ban:
            comms_receive("Word has spread of your crimes. You are no longer welcome at any Salvage Yards!", title="Banned from all Salvage Yards")
            comms_broadcast(responsible_player_ship_id, "Banned from all Salvage Yards")
        elif is_transition_to_ban:
            comms_receive("You are hereby banned from docking at this shipyard, vandal!", title="Banned")
            comms_broadcast(responsible_player_ship_id, f"Banned from {owner_station_object.name}")
        else: # Player was already banned, and is still vandalizing
            comms_receive("Stop blowing up our shipswrecks!!!", title="Stop vandalizing!")

# Reputation level

class SalvageYardReputationLevel(Enum):
    FIRST_WARNING = 1
    SECOND_WARNING = 2
    BANNED = 3

def _get_worse_reputation_level_between(reputation_1, reputation_2):
    if reputation_1 is None:
        return reputation_2
    elif reputation_2 is None:
        return reputation_1
    elif reputation_1.value < reputation_2.value:
        return reputation_2
    else: # reputation_2.value =< reputation_1.value
        return reputation_1

def _get_worse_reputation_by_one_level(reputation):
    if reputation == SalvageYardReputationLevel.BANNED:
        return SalvageYardReputationLevel.BANNED
    elif reputation == SalvageYardReputationLevel.SECOND_WARNING:
        return SalvageYardReputationLevel.BANNED
    elif reputation == SalvageYardReputationLevel.FIRST_WARNING:
        return SalvageYardReputationLevel.SECOND_WARNING
    else: # reputation is None, i.e. OK
        return SalvageYardReputationLevel.FIRST_WARNING

# Player's Local reputation

def is_banned_from_salvage_yard(player_ship_id, station_id):
    """
    Returns True if the player ship is banned from docking at this salvage
    yard station, otherwise False
    """
    reputation = _get_local_salvage_yard_reputation(player_ship_id, station_id)
    
    # For some reason that I can't fathom, this was always returning false,
    # even when reputation is actually equal to BANNED.
    #is_banned = reputation == SalvageYardReputationLevel.BANNED
    # In the same situations, this check was working fine, so use it instead.
    is_banned = reputation is not None and reputation.value == 3
    
    return is_banned

def _inventory_key_salvage_yard_reputation_local(station_id):
    return f"slvRepLoc{station_id}"

def _get_local_salvage_yard_reputation(player_ship_id, station_id):
    # Local reputation cannot be better than global reputation
    local_reputation = get_inventory_value(player_ship_id, _inventory_key_salvage_yard_reputation_local(station_id))
    global_reputation = _get_global_salvage_yard_reputation(player_ship_id)
    return _get_worse_reputation_level_between(local_reputation, global_reputation)

def _worsen_local_salvage_yard_reputation(player_ship_id, station_id):
    old_reputation = _get_local_salvage_yard_reputation(player_ship_id, station_id)
    new_reputation = _get_worse_reputation_by_one_level(old_reputation)
    set_inventory_value(player_ship_id, _inventory_key_salvage_yard_reputation_local(station_id), new_reputation)
    if old_reputation == SalvageYardReputationLevel.SECOND_WARNING:
        _worsen_global_salvage_yard_reputation(player_ship_id)
    return new_reputation
    

# Player's Global reputation

_INVENTORY_KEY_SALVAGE_YARD_REPUTATION_GLOBAL = "slvRepGlb"

def _get_global_salvage_yard_reputation(player_ship_id):
    return get_inventory_value(player_ship_id, _INVENTORY_KEY_SALVAGE_YARD_REPUTATION_GLOBAL)

def _worsen_global_salvage_yard_reputation(player_ship_id):
    old_reputation = _get_global_salvage_yard_reputation(player_ship_id)
    new_reputation = _get_worse_reputation_by_one_level(old_reputation)
    set_inventory_value(player_ship_id, _INVENTORY_KEY_SALVAGE_YARD_REPUTATION_GLOBAL, new_reputation)

# Wreck's Owned-by station

_INVENTORY_KEY_OWNED_BY_STATION_ID = "jnk_own"

def get_owned_by_station_id(wreck_object_id):
    return get_inventory_value(wreck_object_id, _INVENTORY_KEY_OWNED_BY_STATION_ID)

def set_owned_by_station_id(wreck_object_id, owned_by_station_id):
    set_inventory_value(wreck_object_id, _INVENTORY_KEY_OWNED_BY_STATION_ID, owned_by_station_id)

# Misc

def derelict_tsn_role_key():
    return "derelict"

def salvage_yard_ship_type_key():
    return "starbase_salvage_yard_industry_ef"
