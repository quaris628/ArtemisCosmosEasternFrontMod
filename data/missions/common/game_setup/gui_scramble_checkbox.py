from sbs_utils.mast.label import label
from sbs_utils.procedural.execution import END, get_variable, set_variable
from sbs_utils.procedural.gui import gui_checkbox, gui_message, gui_represent
from sbs_utils.procedural.signal import signal_register

from data.missions.common.gui_color_scheme import color_text

from model_game_setup_data import signal_game_setup_is_scramble_changed
from controller_game_setup_data import get_game_setup_data

# ----- creation -----

def create_scramble_checkbox():
    GAME_SETUP_DATA = get_game_setup_data()
    
    checkbox = gui_checkbox("Scramble!", style=f"font:gui-3;col-width:170px;color:{color_text()};")
    checkbox.value = GAME_SETUP_DATA.is_scramble
    
    _set_scramble_checkbox(checkbox)
    
    gui_message(checkbox, _scramble_checkbox_on_click)
    
    signal_register(signal_game_setup_is_scramble_changed(), _scramble_checkbox_on_is_scramble_changed, is_temporary=True)

@label()
def _scramble_checkbox_on_click():
    GAME_SETUP_DATA = get_game_setup_data()
    checkbox = _get_scramble_checkbox()
    
    if GAME_SETUP_DATA.is_scramble != checkbox.value:
        GAME_SETUP_DATA.is_scramble = checkbox.value
    
    yield END()

@label()
def _scramble_checkbox_on_is_scramble_changed():
    is_scramble = get_variable("IS_SCRAMBLE")
    checkbox = _get_scramble_checkbox()
    
    if checkbox.value != is_scramble:
        checkbox.value = is_scramble
        gui_represent(checkbox)
    
    yield END()

# ----- setter/getter wrappers -----

def _get_scramble_checkbox():
    return get_variable(_SCRAMBLE_CHECKBOX_VAR_NAME)

def _set_scramble_checkbox(checkbox):
    set_variable(_SCRAMBLE_CHECKBOX_VAR_NAME, checkbox)

_SCRAMBLE_CHECKBOX_VAR_NAME = "_scramble_checkbox"
