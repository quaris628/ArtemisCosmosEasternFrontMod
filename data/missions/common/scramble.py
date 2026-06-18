
from sbs_utils.mast.label import label
from sbs_utils.procedural.execution import AWAIT, END, get_shared_variable, task_schedule
from sbs_utils.procedural.signal import signal_emit
from sbs_utils.procedural.timers import clear_timer, delay_sim, get_time_remaining, is_timer_finished, is_timer_set, set_timer

@label()
def scramble_wait_for_players_start():
    SHARED = get_shared_variable("SHARED")
    
    # delay might be extended, or interrupted completely, but never decreased
    while is_scramble_players_start_delay_in_progress():
        seconds_remaining = get_scramble_players_start_delay_seconds_remaining()
        yield AWAIT(delay_sim(seconds_remaining))
    
    if not is_timer_set(SHARED, _SCRAMBLE_PLAYERS_START_DELAY_TIMER_KEY):
        # scramble_start_players_now already started the players
        yield END()
    
    signal_emit(signal_scramble_start_players())
    
    yield END()

# ----- setter/getter wrappers -----

def scramble_players_start_delay_timer_start(seconds):
    SHARED = get_shared_variable("SHARED")
    set_timer(SHARED, _SCRAMBLE_PLAYERS_START_DELAY_TIMER_KEY, seconds=seconds)
    task_schedule(scramble_wait_for_players_start)

def scramble_players_start_delay_timer_add_time(seconds=0):
    SHARED = get_shared_variable("SHARED")
    seconds += get_time_remaining(SHARED, _SCRAMBLE_PLAYERS_START_DELAY_TIMER_KEY)
    set_timer(SHARED, _SCRAMBLE_PLAYERS_START_DELAY_TIMER_KEY, seconds=seconds)

def scramble_start_players_now():
    SHARED = get_shared_variable("SHARED")
    clear_timer(SHARED, _SCRAMBLE_PLAYERS_START_DELAY_TIMER_KEY)
    signal_emit(signal_scramble_start_players())

def get_scramble_players_start_delay_seconds_remaining():
    SHARED = get_shared_variable("SHARED")
    return get_time_remaining(SHARED, _SCRAMBLE_PLAYERS_START_DELAY_TIMER_KEY)

def is_scramble_players_start_delay_in_progress():
    SHARED = get_shared_variable("SHARED")
    return is_timer_set(SHARED, _SCRAMBLE_PLAYERS_START_DELAY_TIMER_KEY) and not is_timer_finished(SHARED, _SCRAMBLE_PLAYERS_START_DELAY_TIMER_KEY)

_SCRAMBLE_PLAYERS_START_DELAY_TIMER_KEY = "_scramble_players_start_delay"

# ----- signals -----

# Note that player ships could have been destroyed, or (hypothetically)
# the game could have ended, by the time this signal is emitted
def signal_scramble_start_players():
    return "scramble_start_players"
