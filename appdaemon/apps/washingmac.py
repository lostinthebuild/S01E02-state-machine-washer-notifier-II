import appdaemon.plugins.hass.hassapi as hass
from enum import Enum

from libs.statemachine import Machine, ANY, StateIs, Timeout


class States(Enum):
    IDLE = 1
    MAYBE_IDLE = 10
    MAYBE_WASHING = 11
    WASHING = 2
    SPINNING = 3
    MAYBE_DONE = 40
    DONE = 4
    ERROR = 9
    MAYBE_ERROR = 90

# saves me a few keystrokes :) 
IDLE = States.IDLE
MAYBE_IDLE = States.MAYBE_IDLE
MAYBE_WASHING = States.MAYBE_WASHING
WASHING = States.WASHING
SPINNING = States.SPINNING
DONE = States.DONE
MAYBE_DONE = States.MAYBE_DONE
MAYBE_ERROR = States.MAYBE_ERROR
ERROR = States.ERROR

VIBRATION_SENSOR = "sensor.washing_machine_vibration"
OUTPUT_ENTITY = "sensor.washing_machine"
NOTIFIER = "notify.all_house_residents"


class VibrationState(StateIs):
    def __init__(self, name):
        super().__init__(VIBRATION_SENSOR, self.test_predicate)
        self.name = name

    def __str__(self):
        return self.name

    def test_predicate(self, new):
        return new.lower() == self.name.lower()


state_is_idle = lambda: VibrationState("idle")
state_is_washing = lambda: VibrationState("washing")
state_is_spinning = lambda: VibrationState("spinning")


class WashingMachine(hass.Hass):
    def initialize(self):
        machine = Machine(self, States, initial=IDLE, entity=OUTPUT_ENTITY)
        machine.add_transitions(IDLE, [state_is_washing(), state_is_spinning()], MAYBE_WASHING)
        machine.add_transitions(ERROR, [state_is_washing(), state_is_spinning()], MAYBE_WASHING)
        machine.add_transitions(DONE, [state_is_washing(), state_is_spinning()], MAYBE_WASHING)

        machine.add_transitions(MAYBE_WASHING, Timeout(60), WASHING)
        machine.add_transitions(MAYBE_WASHING, state_is_idle(), MAYBE_IDLE)

        machine.add_transitions(MAYBE_IDLE, Timeout(5 * 60), IDLE)
        machine.add_transitions(
            MAYBE_IDLE, [state_is_washing(), state_is_spinning()], MAYBE_WASHING
        )

        machine.add_transitions(WASHING, state_is_spinning(), SPINNING)
        machine.add_transitions(WASHING, state_is_idle(), MAYBE_ERROR)

        machine.add_transitions(SPINNING, state_is_idle(), MAYBE_DONE)
        machine.add_transitions(SPINNING, state_is_washing(), WASHING)

        machine.add_transitions(MAYBE_DONE, state_is_washing(), WASHING)
        machine.add_transitions(MAYBE_DONE, state_is_spinning(), SPINNING)
        machine.add_transitions(MAYBE_DONE, Timeout(8 * 60), DONE)

        machine.add_transitions(MAYBE_ERROR, state_is_washing(), WASHING)
        machine.add_transitions(MAYBE_ERROR, state_is_spinning(), SPINNING)
        machine.add_transitions(MAYBE_ERROR, Timeout(75 * 60), ERROR)

        # output the state machine diagram as a dot diagram thingy url 
        # pretty cool feature this
        machine.log_graph_link()

        machine.on_transition(self.on_state_change)
        self.listen_state(self._state_callback, VIBRATION_SENSOR)
        self.machine = machine

    def on_state_change(self, from_state, to_state):
        self.log("Washer State Change {} -> {}".format(from_state, to_state))

        # trigger notification
        if to_state == DONE:
            self.notify("Laundy Done", "Laundry is complete. You may take the clothes")
        # elif to_state == ERROR:
        #     self.notify(
        #         "Possible problem with Laundry",
        #         "There might be a problem with the laundry. Your attention is required",
        #     )

    def _state_callback(self, unused_entity, unused_attribute, unused_old, new, unused_kwargs):
        self.log(
            "{}: {} [state: {}]".format(VIBRATION_SENSOR, new, self.machine.current_state.name)
        )

    def notify(self, title, message):
        self.call_service(NOTIFIER.replace(".", "/"), message=message, title=title)

