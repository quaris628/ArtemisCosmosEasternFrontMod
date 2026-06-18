from sbs_utils.mast.label import label
from sbs_utils.procedural.execution import AWAIT, END, get_variable, set_variable, task_schedule
from sbs_utils.procedural.gui import gui_hide, gui_input, gui_message, gui_represent, gui_show, gui_sub_section, gui_text
from sbs_utils.procedural.signal import signal_register
from sbs_utils.procedural.timers import delay_app

from data.missions.common.gui_color_scheme import color_text, color_text_secondary

from model_game_setup_data import signal_game_setup_is_scramble_changed, signal_game_setup_scramble_start_delay_seconds_changed
from controller_game_setup_data import get_game_setup_data

# ----- creation -----

def create_scramble_start_delay_input():
    GAME_SETUP_DATA = get_game_setup_data()
    
    # $text is necessary in order to display a colon
    # https://github.com/artemis-sbs/LegendaryMissions/issues/566#issuecomment-4291760757
    label_text = gui_text("$text:Player Start Delay (s):;", style=f"font:gui-3;col-width:295px;padding:0,3px;color:{color_text_secondary()};")
    
    # sub-section is necessary to work around gui_input's font size not being respected (for some !@#$%^& reason)
    # https://github.com/artemis-sbs/LegendaryMissions/issues/664
    with gui_sub_section():
        set_variable(_START_DELAY_INPUT_INITIAL_VALUE_VAR_NAME, str(GAME_SETUP_DATA.scramble_start_delay_seconds))
        start_delay_input = gui_input("", var=_START_DELAY_INPUT_INITIAL_VALUE_VAR_NAME, style=f"font:gui-3;col-width:96px;color:{color_text()};")
    
    _set_scramble_start_delay_gui_elements(label_text, start_delay_input)
    
    gui_message(start_delay_input, _scramble_start_delay_input_typed_in)
    
    signal_register(signal_game_setup_scramble_start_delay_seconds_changed(), _scramble_start_delay_input_on_start_delay_changed)
    signal_register(signal_game_setup_is_scramble_changed(), _scramble_start_delay_input_on_is_scramble_changed)
    
    task_schedule(_scramble_start_delay_input_update_after_delay)

@label()
def _scramble_start_delay_input_update_after_delay():
    # If an element is hidden prior to it being presented for the first time,
    # then it will never show again.
    # https://github.com/artemis-sbs/LegendaryMissions/issues/513#issuecomment-3931007180
    # So work around this by adding a short delay before hiding the element,
    # so that the element will (hopefully) have been presented already by the
    # time gui_hide is called.
    yield AWAIT(delay_app(0))
    
    GAME_SETUP_DATA = get_game_setup_data()
    label_text, start_delay_input = _get_scramble_start_delay_gui_elements()
    
    if not GAME_SETUP_DATA.is_scramble:
        gui_hide(label_text)
        gui_hide(start_delay_input)
        gui_represent(label_text)
        gui_represent(start_delay_input)
    
    yield END()

@label()
def _scramble_start_delay_input_typed_in():
    GAME_SETUP_DATA = get_game_setup_data()
    label_text, start_delay_input = _get_scramble_start_delay_gui_elements()
    
    input_value_as_integer = int(start_delay_input.value) if start_delay_input.value.isdecimal() else 0
    if GAME_SETUP_DATA.scramble_start_delay_seconds != input_value_as_integer:
        GAME_SETUP_DATA.scramble_start_delay_seconds = input_value_as_integer
    
    yield END()

@label()
def _scramble_start_delay_input_on_start_delay_changed():
    start_delay_seconds = get_variable("SCRAMBLE_START_DELAY_SECONDS")
    label_text, start_delay_input = _get_scramble_start_delay_gui_elements()
    
    input_value_as_integer = int(start_delay_input.value) if start_delay_input.value.isdecimal() else 0
    if input_value_as_integer != start_delay_seconds:
        start_delay_input.value = str(start_delay_seconds)
        gui_represent(start_delay_input)
    
    yield END()

@label()
def _scramble_start_delay_input_on_is_scramble_changed():
    is_scramble = get_variable("IS_SCRAMBLE")
    label_text, start_delay_input = _get_scramble_start_delay_gui_elements()
    
    if is_scramble:
        gui_show(label_text)
        gui_show(start_delay_input)
    else:
        gui_hide(label_text)
        gui_hide(start_delay_input)
    gui_represent(label_text)
    gui_represent(start_delay_input)
    
    yield END()

# ----- misc -----

_START_DELAY_INPUT_INITIAL_VALUE_VAR_NAME = "_start_delay_input_initial_value"

# ----- setter/getter wrappers -----

def _get_scramble_start_delay_gui_elements():
    gui_elements = get_variable(_START_DELAY_INPUT_GUI_ELEMENTS_VAR_NAME)
    return gui_elements[0], gui_elements[1]

def _set_scramble_start_delay_gui_elements(label_text, start_delay_input):
    set_variable(_START_DELAY_INPUT_GUI_ELEMENTS_VAR_NAME, (label_text, start_delay_input))

_START_DELAY_INPUT_GUI_ELEMENTS_VAR_NAME = "_start_delay_input_gui_elements"
