from random import shuffle

from sbs_utils.mast.label import label
from sbs_utils.procedural.execution import AWAIT, END, get_variable, set_variable, task_schedule
from sbs_utils.procedural.gui import gui_button, gui_hide, gui_message, gui_represent, gui_show
from sbs_utils.procedural.signal import signal_register
from sbs_utils.procedural.timers import delay_app

from data.missions.common.controller_vessel_types_data import get_vessel_types_data
from data.missions.common.gui_color_scheme import color_text

from model_game_setup_data import signal_game_setup_is_scramble_changed
from controller_game_setup_data import get_game_setup_data

# ----- creation -----

def create_scramble_randomize_all_ship_types_button():
    
    button = gui_button("Randomize All", style=f"font:gui-2;col-width:120px;padding:0,0,0,8px;color:{color_text()};")
    
    _set_scramble_randomize_all_ship_types_button(button)
    
    gui_message(button, _scramble_randomize_all_ship_types_button_clicked)
    
    signal_register(signal_game_setup_is_scramble_changed(), _scramble_randomize_all_ship_types_button_on_is_scramble_changed)
    
    task_schedule(_scramble_randomize_all_ship_types_button_update_after_delay)

@label()
def _scramble_randomize_all_ship_types_button_update_after_delay():
    # If an element is hidden prior to it being presented for the first time,
    # then it will never show again.
    # https://github.com/artemis-sbs/LegendaryMissions/issues/513#issuecomment-3931007180
    # So work around this by adding a short delay before hiding the element,
    # so that the element will (hopefully) have been presented already by the
    # time gui_hide is called.
    yield AWAIT(delay_app(0))
    
    GAME_SETUP_DATA = get_game_setup_data()
    button = _get_scramble_randomize_all_ship_types_button()
    
    if not GAME_SETUP_DATA.is_scramble:
        gui_hide(button)
        gui_represent(button)
    
    yield END()

@label()
def _scramble_randomize_all_ship_types_button_clicked():
    VESSEL_TYPES_DATA = get_vessel_types_data()
    GAME_SETUP_DATA = get_game_setup_data()
    
    random_ship_type_keys = list(VESSEL_TYPES_DATA.get_all_ship_type_keys())
    shuffle(random_ship_type_keys)
    
    for ship_number in range(1, GAME_SETUP_DATA.player_ship_count + 1):
        player_ship_setup_data = GAME_SETUP_DATA.get_player_ship_by_number(ship_number)
        player_ship_setup_data.ship_type_key = random_ship_type_keys[ship_number - 1]
    
    yield END()

@label()
def _scramble_randomize_all_ship_types_button_on_is_scramble_changed():
    is_scramble = get_variable("IS_SCRAMBLE")
    button = _get_scramble_randomize_all_ship_types_button()
    
    if is_scramble:
        gui_show(button)
    else:
        gui_hide(button)
    gui_represent(button)
    
    yield END()

# ----- misc -----

_START_DELAY_INPUT_INITIAL_VALUE_VAR_NAME = "_start_delay_input_initial_value"

# ----- setter/getter wrappers -----

def _get_scramble_randomize_all_ship_types_button():
    return get_variable(_SCRAMBLE_RANDOMIZE_ALL_SHIP_TYPES_BUTTON_VAR_NAME)

def _set_scramble_randomize_all_ship_types_button(button):
    set_variable(_SCRAMBLE_RANDOMIZE_ALL_SHIP_TYPES_BUTTON_VAR_NAME, button)

_SCRAMBLE_RANDOMIZE_ALL_SHIP_TYPES_BUTTON_VAR_NAME = "_scramble_randomize_all_ship_types_button"
