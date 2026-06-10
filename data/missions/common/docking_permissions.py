"""
Rules for where player ships can dock to resupply.
Also includes closely related permissions such as whether the player can
resupply heavy ordinance or order specific ordinance types to be manufactured.
Does not include anything about single-seat craft docking permissions.
"""
from random import choice

from sbs_utils.procedural.comms import comms_broadcast, comms_message
from sbs_utils.procedural.execution import get_shared_variable
from sbs_utils.procedural.inventory import get_inventory_value, set_inventory_value
from sbs_utils.procedural.query import to_space_object
from sbs_utils.procedural.roles import all_roles, role

from data.missions.common.distance_utils import get_space_objects_within_radius
from data.missions.common.pirate_features_definitions import is_raider, is_pirate, is_tsn, is_ximni, is_civilian_air_patrol, is_pirate_civilian, is_pirate_military, is_neutral_civilian, is_tsn_civilian, is_tsn_military

# ----- Gameplay constants -----

# Consider tweaking these to affect gameplay balance

def _get_enemy_too_close_to_allow_docking_radius():
    difficulty = get_shared_variable("DIFFICULTY")
    # difficulty 1 means radius is 700
    # difficulty 5 means radius is 1500
    # difficulty 11 means radius is 2700
    return 500 + 200 * difficulty

# ----- Main docking permissions logic -----

def test_player_capital_ship_dock(player_ship_id, dock_object_id, ignore_enemy_nearby=False):
    """
    Determines what would happen if a captial player ship attempted to dock at
    a station or resupply ship. Does not actually perform the action of
    attempting to dock.
    
    Pirate player ships can only dock at TSN stations if they have killed
    at least one raider and have never killed a friendly TSN or civilian vessel.
    TSN, Ximni, and all other types of player ships can always dock at TSN stations.
    No player ship can dock at raider stations.
    If a raider is too close to a TSN station, that TSN station temporarily
    disables docking (regardless of whether the player ship is otherwise allowed
    to dock). How close is too close is defined by
    _get_enemy_too_close_to_allow_docking_radius()
    
    Args:
        player_ship_id (int): the id of the captial player ship that would be
            attempting to dock
        dock_object_id (int): the id of the station or resupply ship that the
            player ship would be attempting to dock at
        ignore_enemy_nearby (bool | None): Optional, default False. Pass True to
            ignore whether docking would be temporarily disabled due to an enemy
            being too close. Useful for priority docking, weapon build requests,
            comms hails, maybe etc. When this is True, then
            dock_attempt_result_disallowed_enemy_near() never gets returned.
    
    Returns:
        What would happen if the player ship attempted to dock,
        in the form of a value returned by one of the following functions:
        (This is essentially an enum that's mast-compatible)
        dock_attempt_result_allowed_always_welcome()
        dock_attempt_result_allowed_pirate_uneasy_alliance()
        dock_attempt_result_disallowed_enemy_near()
        dock_attempt_result_disallowed_piracy()
        dock_attempt_result_disallowed_pirate_killed_tsn()
        dock_attempt_result_disallowed_always_hostile()
        dock_attempt_result_disallowed_military_unwelcome()
        dock_attempt_result_disallowed_civilian_unwelcome()
    """
    if is_raider(dock_object_id):
        static_perms = dock_attempt_result_disallowed_always_hostile()
    
    elif is_tsn(player_ship_id):
        if is_tsn(dock_object_id):
            static_perms = dock_attempt_result_allowed_always_welcome()
        elif is_pirate(dock_object_id):
            static_perms = test_player_capital_tsn_ship_dock_at_pirate(player_ship_id, dock_object_id, skip_is_tsn_check=True)
        elif is_neutral_civilian(dock_object_id):
            if is_tsn_civilian(player_ship_id):
                return dock_attempt_result_allowed_always_welcome()
            elif is_tsn_military(player_ship_id):
                return dock_attempt_result_disallowed_military_unwelcome()
            else:
                # Should never happen, tsn should be either civilian or military
                return dock_attempt_result_allowed_always_welcome()
        else:
            # Should never happen, stations should be tsn, pirate, or market civilian
            static_perms = dock_attempt_result_allowed_always_welcome()
    
    elif is_pirate(player_ship_id):
        if is_pirate(dock_object_id) or is_neutral_civilian(dock_object_id):
            static_perms = dock_attempt_result_allowed_always_welcome()
        elif is_tsn(dock_object_id):
            static_perms = test_player_capital_pirate_ship_dock_at_tsn(player_ship_id, skip_is_pirate_check=True)
        else:
            # Should never happen, stations should be tsn, pirate, or market civilian
            return dock_attempt_result_allowed_always_welcome()
    
    elif is_civilian_air_patrol(player_ship_id):
        static_perms = dock_attempt_result_allowed_always_welcome()
    
    elif is_ximni(player_ship_id):
        static_perms = dock_attempt_result_allowed_always_welcome()
    
    else:
        # Catch-all backup for weird edge cases, e.g. Arvonian player ships
        static_perms = dock_attempt_result_allowed_always_welcome()
    
    # Don't give the "enemy too close" response unless the player would otherwise
    # be allowed to dock
    if not ignore_enemy_nearby and is_dock_attempt_result_allowed(static_perms) and is_enemy_too_close_to_allow_docking(dock_object_id):
        return dock_attempt_result_disallowed_enemy_near()
    else:
        return static_perms

def can_player_capital_ship_dock(player_ship_id, dock_object_id, ignore_enemy_nearby=False):
    """
    Returns True if the player ship can dock, otherwise False.
    This is otherwise identical to test_player_capital_ship_dock().
    """
    return is_dock_attempt_result_allowed(test_player_capital_ship_dock(player_ship_id, dock_object_id, ignore_enemy_nearby=ignore_enemy_nearby))

def is_enemy_too_close_to_allow_docking(dock_object_id):
    """
    Returns True if at least one enemy is close enough to the given station or
    resupply ship that docking with it is temporarily disabled, otherwise False """
    dock_object = to_space_object(dock_object_id)
    if dock_object is None:
        return False
    
    too_close_radius = _get_enemy_too_close_to_allow_docking_radius()
    # 0x10 is bitmask value for NPCs
    nearby_npc_space_objects = get_space_objects_within_radius(dock_object.pos, too_close_radius, 0x10)
    
    for npc_space_object in nearby_npc_space_objects:
        if is_raider(npc_space_object.id):
            return True
    return False

def test_player_capital_pirate_ship_dock_at_tsn(player_ship_id, skip_is_pirate_check=False):
    """
    Determines what would happen if a captial player pirate ship attempted to
    dock at TSN stations or resupply ships in general.
    Does not actually perform the action of attempting to dock.
    Does not focus on any particular tsn station or resupply ship.
    Args:
        player_ship_id (int): the id of the captial player pirate ship that
            would be attempting to dock
        skip_is_pirate_check (bool | None): Optional, default False. Pass True if
            the player ship has already been verified to be a pirate.
    Returns:
        If the player ship is not a pirate, returns None.
        Otherwise, returns what would happen if the player ship attempted to dock,
        in the form of a value returned by one of the following functions:
        (This is essentially an enum that's mast-compatible)
        dock_attempt_result_allowed_pirate_uneasy_alliance()
        dock_attempt_result_disallowed_piracy()
        dock_attempt_result_disallowed_pirate_killed_tsn()
    """
    # This is dependent on code in /damage/destroy.mast
    # where set_killed_tsn and set_killed_raider are called
    if not skip_is_pirate_check and not is_pirate(player_ship_id):
        return None
    elif has_killed_tsn(player_ship_id):
        return dock_attempt_result_disallowed_pirate_killed_tsn()
    elif has_killed_raider(player_ship_id):
        return dock_attempt_result_allowed_pirate_uneasy_alliance()
    else:
        return dock_attempt_result_disallowed_piracy()

def test_player_capital_tsn_ship_dock_at_pirate(player_ship_id, dock_object_id, skip_is_tsn_check=False):
    """
    Determines what would happen if a captial player TSN ship attempted to
    dock at a pirate station or resupply ship.
    Does not actually perform the action of attempting to dock.
    Ignores whether docking would be temporarily disabled due to an enemy
    being too close.
    Args:
        player_ship_id (int): the id of the captial player tsn ship that
            would be attempting to dock
        dock_object_id (int): the id of the pirate station or resupply ship that
            the player ship would be attempting to dock at
        skip_is_tsn_check (bool | None): Optional, default False. Pass True if
            the player ship has already been verified to be TSN.
    Returns:
        If the player ship is not TSN, returns None.
        Otherwise, returns what would happen if the player ship attempted to dock,
        in the form of a value returned by one of the following functions:
        (This is essentially an enum that's mast-compatible)
        dock_attempt_result_allowed_always_welcome()
        dock_attempt_result_disallowed_military_unwelcome()
        dock_attempt_result_disallowed_civilian_unwelcome()
    """
    if not skip_is_tsn_check and not is_tsn(player_ship_id):
        return None
    
    elif is_pirate_civilian(dock_object_id):
        if is_tsn_civilian(player_ship_id):
            return dock_attempt_result_allowed_always_welcome()
        elif is_tsn_military(player_ship_id):
            return dock_attempt_result_disallowed_military_unwelcome()
        else:
            # Should never happen, tsn should be either civilian or military
            return dock_attempt_result_allowed_always_welcome()
            
    elif is_pirate_military(dock_object_id):
        if is_tsn_civilian(player_ship_id):
            return dock_attempt_result_disallowed_civilian_unwelcome()
        elif is_tsn_military(player_ship_id):
            return dock_attempt_result_allowed_always_welcome()
        else:
            # Should never happen, tsn should be either civilian or military
            return dock_attempt_result_allowed_always_welcome()
    
    else:
        # Should never happen, pirate should be either civilian or military
        return dock_attempt_result_allowed_always_welcome()

# ----- ordinance permissions -----

def can_command_to_build_weapons(player_ship_id, dock_object_id):
    """
    Returns True if the player ship can command the docking station (or
    resupply ship) to build ordinance types for them, otherwise False
    """
    return can_player_capital_ship_dock(player_ship_id, dock_object_id, ignore_enemy_nearby=True)

def can_give_nukes(player_ship_id, dock_object_id):
    """
    Returns True if the player ship can resupply Nukes from the docking
    station (or resupply ship), otherwise False
    """
    if is_tsn(player_ship_id):
        return is_tsn(dock_object_id)
    
    elif is_pirate(player_ship_id):
        return is_pirate(dock_object_id)
    
    elif is_ximni(player_ship_id):
        return True
    
    else:
        # Catch-all, e.g. Arvonian player ships
        return True

def can_give_mines(player_ship_id, dock_object_id):
    """
    Returns True if the player ship can resupply Mines from the docking
    station (or resupply ship), otherwise False
    """
    # Tentative; this might be different from nukes at some point
    return can_give_nukes(player_ship_id, dock_object_id)

# ----- Comms messages -----

# Also see docking.mast === docking_check_permissions ===

def get_docking_permissions_status_message(hypothetical_dock_attempt_result):
    """
    Returns a short message describing a player ship's docking permissions,
    given the hypothetical result of a dock attempt.
    Args:
        hypothetical_dock_attempt_result (quasi-enum): the value returned from
            test_player_capital_ship_dock() (or equivalent/similar function) that
            represents what would happen if the player ship attempted to dock.
            This should not be dock_attempt_result_disallowed_enemy_near().
    Returns:
        (str) Short message describing the docking permissions.
    """
    if hypothetical_dock_attempt_result == dock_attempt_result_allowed_always_welcome():
        return "You have full docking privileges."
    elif hypothetical_dock_attempt_result == dock_attempt_result_allowed_pirate_uneasy_alliance():
        return "You currently have docking privileges."
    # dock_attempt_result_disallowed_enemy_near shouldn't apply
    elif hypothetical_dock_attempt_result == dock_attempt_result_disallowed_piracy():
        return "You do NOT have docking privileges."
    elif hypothetical_dock_attempt_result == dock_attempt_result_disallowed_pirate_killed_tsn() or hypothetical_dock_attempt_result == dock_attempt_result_disallowed_always_hostile():
        return "You do NOT have docking privileges, and you never will."
    elif hypothetical_dock_attempt_result == dock_attempt_result_disallowed_military_unwelcome():
        return "You do NOT have docking privileges. Military vessels are not welcome here."
    elif hypothetical_dock_attempt_result == dock_attempt_result_disallowed_civilian_unwelcome():
        return "You do NOT have docking privileges. Civilians vessels are not welcome here."
    else:
        # This should never happen
        return "ERROR - Docking clearance records not found"

def get_ordinance_permissions_status_message(player_ship_id, dock_object_id):
    """
    Returns a short message describing what, if any, types of ordinance a player
    ship is not allowed to resupply from a docking station (or resupply ship).
    Args:
        player_ship_id (int): the id of the captial player ship that would be
            attempting to dock
        dock_object_id (int): the id of the station or resupply ship that the
            player ship would be attempting to dock at
    Returns:
        (str) Short message describing which ordinance types the player cannot
            resupply, or the empty string if there are no ordinance types that
            are off-limits.
    """
    nukes_ok = can_give_nukes(player_ship_id, dock_object_id)
    mines_ok = can_give_mines(player_ship_id, dock_object_id)
    if not nukes_ok and not mines_ok:
        return "We are not authorized to give you Nukes or Mines."
    elif not nukes_ok:
        return "We are not authorized to give you Nukes."
    elif not mines_ok:
        return "We are not authorized to give you Mines."
    else:
        return ""

def send_tsn_admin_comms_message(player_ship_id, message_title, message_body):
    """
    Sends a message from the TSN Administrator to a player ship.
    If there are no TSN stations (or resupply ships), then nothing happens.
    Args:
        player_ship_id (int): the player ship recieving the message
        message_title (str): The message summarized into a few words.
            This is both the title of the comms message and the text that's
            broadcast to all consoles on the ship.
        message_body (str): The full message. This is the body of the comms
            message.
    """
    tsn_station_ids = all_roles("tsn, station")
    if len(tsn_station_ids) == 0:
        # deep strike resupply ship is basically a station for these purposes
        tsn_station_ids = role("resupply_tanker")
        if len(tsn_station_ids) == 0:
            return
    random_docking_station_id = choice(list(tsn_station_ids))
    
    # copied from peacetime.mast
    admiral_face = "ter #964b00 8 1;ter #968b00 3 0;ter #968b00 4 0;ter #968b00 1 2;ter #fff 4 4;ter #964b00 8 4;"
    
    comms_broadcast(player_ship_id, message_title)
    comms_message(message_body, random_docking_station_id, player_ship_id, title=message_title, face=admiral_face, from_name="TSN Administrator")

# ----- Simple setters/getters -----

def set_killed_raider(player_ship_id):
    set_inventory_value(player_ship_id, _INVENTORY_KEY_HAS_KILLED_RAIDER, True)

def has_killed_raider(player_ship_id):
    return get_inventory_value(player_ship_id, _INVENTORY_KEY_HAS_KILLED_RAIDER) is True

_INVENTORY_KEY_HAS_KILLED_RAIDER = "killed_raider"

def set_killed_tsn(player_ship_id):
    set_inventory_value(player_ship_id, _INVENTORY_KEY_HAS_KILLED_TSN, True)

def has_killed_tsn(player_ship_id):
    return get_inventory_value(player_ship_id, _INVENTORY_KEY_HAS_KILLED_TSN) is True

_INVENTORY_KEY_HAS_KILLED_TSN = "killed_tsn"

# ----- Quasi-enum for possible results of a dock attempt -----

# Use functions to allow these to be easily accessed from MAST code
def dock_attempt_result_allowed_always_welcome():
    return 1
def dock_attempt_result_allowed_pirate_uneasy_alliance():
    return 2
def dock_attempt_result_disallowed_enemy_near():
    return 3
def dock_attempt_result_disallowed_piracy():
    return 4
def dock_attempt_result_disallowed_pirate_killed_tsn():
    return 5
def dock_attempt_result_disallowed_always_hostile():
    return 6
def dock_attempt_result_disallowed_military_unwelcome():
    return 7
def dock_attempt_result_disallowed_civilian_unwelcome():
    return 8

def is_dock_attempt_result_allowed(dock_attempt_result):
    """
    Returns True if the given dock attempt result is successful.
    Returns False if the given dock attempt result is a failure.
    """
    return dock_attempt_result in {dock_attempt_result_allowed_always_welcome(), dock_attempt_result_allowed_pirate_uneasy_alliance()}
