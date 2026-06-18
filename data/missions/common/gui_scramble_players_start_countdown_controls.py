from sbs_utils.mast.label import label
from sbs_utils.procedural.execution import AWAIT, END, get_variable, set_variable, gui_sub_task_schedule
from sbs_utils.procedural.gui import gui_blank, gui_button, gui_hide, gui_message, gui_represent, gui_row, gui_text
from sbs_utils.procedural.signal import signal_register
from sbs_utils.procedural.timers import delay_app, delay_sim

from data.missions.common.gui_color_scheme import color_text, color_text_secondary, color_background

from data.missions.common.scramble import scramble_players_start_delay_timer_add_time, scramble_start_players_now, get_scramble_players_start_delay_seconds_remaining, is_scramble_players_start_delay_in_progress, signal_scramble_start_players

def create_scramble_players_start_countdown_controls():
    if not is_scramble_players_start_delay_in_progress():
        return
    
    gui_row("row-height:32px;")
    gui_blank()
    add_30s_button = gui_button("+30s", style=f"font:gui-3;col-width:75px;color:{color_text()};")
    # $text is necessary in order to display a colon
    # https://github.com/artemis-sbs/LegendaryMissions/issues/566#issuecomment-4291760757
    time_remaining_text = gui_text("$text:--:--;", style=f"font:gui-3;justify:right;col-width:100px;padding:10px,3px;color:{color_text()};background:{color_background()};")
    time_remaining_label_text = gui_text("until players start", style=f"font:gui-3;justify:left;col-width:250px;padding:5px,3px;color:{color_text_secondary()};background:{color_background()};")
    scramble_now_button = gui_button("Scramble now!", style=f"font:gui-3;col-width:200px;color:{color_text()};")
    gui_blank()
    
    _set_scramble_players_start_countdown_controls(add_30s_button, time_remaining_text, time_remaining_label_text, scramble_now_button)
    
    add_30s_button.data = {"TIME_REMAINING_TEXT": time_remaining_text}
    gui_message(add_30s_button, _scramble_players_start_countdown_controls_on_add_30s_button_clicked)
    gui_message(scramble_now_button, _scramble_players_start_countdown_controls_on_scramble_now_button_clicked)
    
    signal_register(signal_scramble_start_players(), _scramble_players_start_countdown_controls_on_start_players, is_temporary=True)
    
    gui_sub_task_schedule(_scramble_players_start_countdown_controls_refresh_countdown_task, data={"TIME_REMAINING_TEXT": time_remaining_text})

@label()
def _scramble_players_start_countdown_controls_on_start_players():
    add_30s_button, time_remaining_text, time_remaining_label_text, scramble_now_button = _get_scramble_players_start_countdown_controls()
    
    gui_hide(add_30s_button)
    gui_hide(time_remaining_text)
    gui_hide(time_remaining_label_text)
    gui_hide(scramble_now_button)
    
    gui_represent(add_30s_button)
    gui_represent(time_remaining_text)
    gui_represent(time_remaining_label_text)
    gui_represent(scramble_now_button)
    
    yield END()

@label()
def _scramble_players_start_countdown_controls_refresh_countdown_task():
    time_remaining_text = get_variable("TIME_REMAINING_TEXT")
    
    yield AWAIT(delay_app(0))
    
    seconds_remaining_on_current_display = None
    while is_scramble_players_start_delay_in_progress():
        seconds_remaining = get_scramble_players_start_delay_seconds_remaining()
        # A simple await delay_sim(1) might not quite line up with the
        # instant the countdown timer's seconds count ticks down.
        # So instead, check at 0.9s, 1.0s, 1.1s, 1.2s, etc. until
        # we see the seconds count tick down.
        if seconds_remaining_on_current_display != seconds_remaining:
            seconds_remaining_on_current_display = seconds_remaining
            refresh_countdown_display(time_remaining_text, seconds_remaining)
            yield AWAIT(delay_sim(0.9))
        else:
            yield AWAIT(delay_sim(0.1))
    
    yield END()

def refresh_countdown_display(time_remaining_text, seconds_remaining):
    minutes_part, seconds_part = divmod(seconds_remaining, 60)
    # $text is necessary in order to display a colon
    # https://github.com/artemis-sbs/LegendaryMissions/issues/566#issuecomment-4291760757
    time_remaining_text.value = f"$text:{minutes_part}:{seconds_part:02d};"
    gui_represent(time_remaining_text)

@label()
def _scramble_players_start_countdown_controls_on_add_30s_button_clicked():
    time_remaining_text = get_variable("TIME_REMAINING_TEXT")
    
    scramble_players_start_delay_timer_add_time(seconds=30)
    
    seconds_remaining = get_scramble_players_start_delay_seconds_remaining()
    refresh_countdown_display(time_remaining_text, seconds_remaining)
    
    yield END()

@label()
def _scramble_players_start_countdown_controls_on_scramble_now_button_clicked():
    scramble_start_players_now()
    yield END()

# ----- setter/getter wrappers -----

def _get_scramble_players_start_countdown_controls():
    gui_elements = get_variable(_SCRAMBLE_PLAYERS_START_COUNTDOWN_CONTROLS_VAR_NAME)
    return gui_elements[0], gui_elements[1], gui_elements[2], gui_elements[3]

def _set_scramble_players_start_countdown_controls(add_30s_button, time_remaining_text, time_remaining_label_text, scramble_now_button):
    set_variable(_SCRAMBLE_PLAYERS_START_COUNTDOWN_CONTROLS_VAR_NAME, (add_30s_button, time_remaining_text, time_remaining_label_text, scramble_now_button))

_SCRAMBLE_PLAYERS_START_COUNTDOWN_CONTROLS_VAR_NAME = "_scramble_players_start_countdown_controls"
