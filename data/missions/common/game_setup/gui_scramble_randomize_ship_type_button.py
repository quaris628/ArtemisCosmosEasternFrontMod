from random import choice

from sbs_utils.mast.label import label
from sbs_utils.procedural.execution import AWAIT, END, get_variable, set_variable, task_schedule
from sbs_utils.procedural.gui import gui_button, gui_hide, gui_message, gui_represent, gui_show
from sbs_utils.procedural.signal import signal_register
from sbs_utils.procedural.timers import delay_app

from data.missions.common.controller_vessel_types_data import get_vessel_types_data
from data.missions.common.gui_color_scheme import color_text

from model_game_setup_data import signal_game_setup_is_scramble_changed, signal_game_setup_data_player_ship_availability_changed
from controller_game_setup_data import get_game_setup_data

# ----- creation -----

def create_scramble_randomize_ship_type_button(ship_number):
    button = gui_button("Randomize", style=f"font:gui-2;col-width:95px;color:{color_text()};", data={"SHIP_NUMBER": ship_number})
    
    _set_scramble_randomize_ship_type_button(ship_number, button)
    
    gui_message(button, _scramble_randomize_ship_type_button_clicked)
    
    signal_register(signal_game_setup_data_player_ship_availability_changed(ship_number), _scramble_randomize_ship_type_buttons_on_player_ship_availability_changed, is_temporary=True)
    
    task_schedule(_scramble_randomize_ship_type_button_update_after_delay, data={"BUTTON": button, "SHIP_NUMBER": ship_number})

@label()
def _scramble_randomize_ship_type_button_update_after_delay():
    
    # If an element is hidden prior to it being presented for the first time,
    # then it will never show again.
    # https://github.com/artemis-sbs/LegendaryMissions/issues/513#issuecomment-3931007180
    # So work around this by adding a short delay before hiding the element,
    # so that the element will (hopefully) have been presented already by the
    # time gui_hide is called.
    yield AWAIT(delay_app(0))
    
    GAME_SETUP_DATA = get_game_setup_data()
    button = get_variable("BUTTON")
    ship_number = get_variable("SHIP_NUMBER")
    
    if not GAME_SETUP_DATA.is_scramble or GAME_SETUP_DATA.player_ship_count < ship_number:
        
        gui_hide(button)
        gui_represent(button)
    
    yield END()

@label()
def _scramble_randomize_ship_type_button_clicked():
    ship_number = get_variable("SHIP_NUMBER")
    VESSEL_TYPES_DATA = get_vessel_types_data()
    GAME_SETUP_DATA = get_game_setup_data()
    
    random_ship_type_key = choice(list(VESSEL_TYPES_DATA.get_all_ship_type_keys()))
    
    player_ship_setup_data = GAME_SETUP_DATA.get_player_ship_by_number(ship_number)
    player_ship_setup_data.ship_type_key = random_ship_type_key
    
    yield END()

@label()
def _scramble_randomize_ship_type_buttons_on_player_ship_availability_changed():
    ship = get_variable("SHIP")
    is_available = get_variable("IS_AVAILABLE")
    GAME_SETUP_DATA = get_game_setup_data()
    button = _get_scramble_randomize_ship_type_button(ship.number)
    
    if not GAME_SETUP_DATA.is_scramble or not is_available:
        gui_hide(button)
    else:
        gui_show(button)
    gui_represent(button)
    
    yield END()

def register_signals_for_randomize_ship_type_buttons():
    signal_register(signal_game_setup_is_scramble_changed(), _scramble_randomize_ship_type_buttons_on_is_scramble_changed, is_temporary=True)

@label()
def _scramble_randomize_ship_type_buttons_on_is_scramble_changed():
    is_scramble = get_variable("IS_SCRAMBLE")
    GAME_SETUP_DATA = get_game_setup_data()
    
    if not is_scramble:
        for ship_number in range(1, GAME_SETUP_DATA.player_ship_count + 1):
            button = _get_scramble_randomize_ship_type_button(ship_number)
            gui_hide(button)
    else:
        for ship_number in range(1, GAME_SETUP_DATA.player_ship_count + 1):
            button = _get_scramble_randomize_ship_type_button(ship_number)
            gui_show(button)
    gui_represent(button)
    
    yield END()

# ----- misc -----

_START_DELAY_INPUT_INITIAL_VALUE_VAR_NAME = "_start_delay_input_initial_value"

# ----- setter/getter wrappers -----

def _get_scramble_randomize_ship_type_button(ship_number):
    ship_number_to_button_dict = get_variable(_SCRAMBLE_SHIP_NUMBER_TO_RANDOMIZE_SHIP_TYPE_BUTTON_DICT_VAR_NAME)
    return ship_number_to_button_dict[ship_number]

def _set_scramble_randomize_ship_type_button(ship_number, button):
    ship_number_to_button_dict = get_variable(_SCRAMBLE_SHIP_NUMBER_TO_RANDOMIZE_SHIP_TYPE_BUTTON_DICT_VAR_NAME)
    if ship_number_to_button_dict is None:
        ship_number_to_button_dict = {}
    ship_number_to_button_dict[ship_number] = button
    set_variable(_SCRAMBLE_SHIP_NUMBER_TO_RANDOMIZE_SHIP_TYPE_BUTTON_DICT_VAR_NAME, ship_number_to_button_dict)

_SCRAMBLE_SHIP_NUMBER_TO_RANDOMIZE_SHIP_TYPE_BUTTON_DICT_VAR_NAME = "_scramble_ship_number_to_randomize_ship_type_button_dict"
