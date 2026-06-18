from sbs_utils.mast.label import label
from sbs_utils.procedural.execution import AWAIT, END, get_variable, set_variable, task_schedule
from sbs_utils.procedural.gui import gui_hide, gui_represent, gui_row, gui_show, gui_text
from sbs_utils.procedural.signal import signal_register
from sbs_utils.procedural.timers import delay_app

from data.missions.common.gui_color_scheme import color_text, color_text_secondary, color_background

from model_game_setup_data import signal_game_setup_is_scramble_changed
from controller_game_setup_data import get_game_setup_data

# ----- creation -----

def create_scramble_console_selection_description_text():
    gui_row(style="row-height:24px;")
    primary_text = gui_text("Scramble! Scramble! Scramble!", style=f"font:gui-3;justify:center;color:{color_text()};background:{color_background()};")
    gui_row(style="row-height:22px;")
    secondary_text = gui_text("The invasion siren has sounded! Quick, pick a ship, any ship, and defend this sector!", style=f"font:gui-2;justify:center;color:{color_text_secondary()};background:{color_background()};")
    
    _set_scramble_console_selection_description_text(primary_text, secondary_text)
    
    signal_register(signal_game_setup_is_scramble_changed(), _scramble_console_selection_description_text_on_is_scramble_changed, is_temporary=True)
    
    task_schedule(_scramble_console_selection_description_text_update_after_delay)

@label()
def _scramble_console_selection_description_text_update_after_delay():
    # If an element is hidden prior to it being presented for the first time,
    # then it will never show again.
    # https://github.com/artemis-sbs/LegendaryMissions/issues/513#issuecomment-3931007180
    # So work around this by adding a short delay before hiding the element,
    # so that the element will (hopefully) have been presented already by the
    # time gui_hide is called.
    yield AWAIT(delay_app(0))
    
    GAME_SETUP_DATA = get_game_setup_data()
    primary_text, secondary_text = _get_scramble_console_selection_description_text()
    
    if not GAME_SETUP_DATA.is_scramble:
        gui_hide(primary_text)
        gui_hide(secondary_text)
        gui_represent(primary_text)
        gui_represent(secondary_text)
    
    yield END()

@label()
def _scramble_console_selection_description_text_on_is_scramble_changed():
    is_scramble = get_variable("IS_SCRAMBLE")
    primary_text, secondary_text = _get_scramble_console_selection_description_text()
    
    if is_scramble:
        gui_show(primary_text)
        gui_show(secondary_text)
    else:
        gui_hide(primary_text)
        gui_hide(secondary_text)
    gui_represent(primary_text)
    gui_represent(secondary_text)
    
    yield END()

# ----- setter/getter wrappers -----

def _get_scramble_console_selection_description_text():
    gui_elements = get_variable(SCRAMBLE_CONSOLE_SELECTION_DESCRIPTION_TEXT_VAR_NAME)
    return gui_elements[0], gui_elements[1]

def _set_scramble_console_selection_description_text(primary_text, secondary_text):
    set_variable(SCRAMBLE_CONSOLE_SELECTION_DESCRIPTION_TEXT_VAR_NAME, (primary_text, secondary_text))

SCRAMBLE_CONSOLE_SELECTION_DESCRIPTION_TEXT_VAR_NAME = "_scramble_console_selection_description_text"
