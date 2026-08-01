import random
import appdaemon.plugins.hass.hassapi as hass


class Light_Timer(hass.Hass):
    """Simulate occupancy by toggling a light at random intervals after sunset.

    Activates only when nobody is home (PEOPLE_HOME count == 0). When someone
    returns, the light stays on for 30 minutes then turns off.

    Required app config keys:
        LIGHT_SWITCH  - entity_id of the light to control
        PEOPLE_HOME   - entity_id of a numeric sensor: 0 = nobody home, >0 = occupied
    """

    def initialize(self):
        # Delay startup so HA presence sensors have time to settle after a restart.
        self.run_in(self.delay_for_person_monitor, 180)

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def delay_for_person_monitor(self, kwargs):
        self.log("Started light timer for %s", self.args["LIGHT_SWITCH"])

        # Schedule the daily activation trigger 15 minutes after sunset.
        self.run_at_sunset(self.before_sunset_cb, offset=900)

        self.first_pass = True

        # Handle the case where HA restarts while we are already in the
        # active window (between 15 min after sunset and 15 min before sunrise).
        if self.now_is_between("sunset + 00:15:00", "sunrise - 00:15:00"):
            self.before_sunset_cb({})

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def nobody_home(self):
        """Return True when the people-home count sensor reads zero."""
        try:
            return int(self.get_state(self.people_home) or 0) == 0
        except (ValueError, TypeError):
            # Treat an unavailable sensor as occupied to avoid false activations.
            return False

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def before_sunset_cb(self, kwargs):
        """Triggered at sunset. Start the occupancy simulation if the house is empty."""
        self.people_home = self.args["PEOPLE_HOME"]
        self.Target_Light = self.args["LIGHT_SWITCH"]

        if self.nobody_home():
            self.log("House empty — starting occupancy simulation for %s", self.Target_Light)
            self.flashing_light()
        else:
            self.log("People home — occupancy simulation not needed for %s", self.Target_Light)

    def flashing_light(self, *args):
        """Toggle the light on a random 30–90 minute schedule while nobody is home.

        Stops naturally at sunrise. If someone arrives home during the night,
        leaves the light on for 30 minutes then turns it off.
        """
        self.people_home = self.args["PEOPLE_HOME"]
        sun = self.get_state("sun.sun")

        if sun == "below_horizon" and self.nobody_home():
            # House empty and it's night — toggle the light and schedule the next toggle.
            self.duration_of_light = random.randint(3, 9) * 600  # 30–90 minutes
            self.toggle(entity_id=self.Target_Light)
            self.log(
                "%s is now %s for %.0f minutes.",
                self.Target_Light,
                self.get_state(entity_id=self.Target_Light),
                self.duration_of_light / 60,
            )
            self.run_in(self.flashing_light, self.duration_of_light)

        elif sun == "above_horizon":
            # Sunrise — end the simulation and ensure the light is off.
            if self.get_state(entity_id=self.Target_Light) == "on":
                self.turn_off(entity_id=self.Target_Light)
            self.log("%s simulation ended at sunrise.", self.Target_Light)

        else:
            # It's still night but someone has come home.
            if self.first_pass:
                # First callback after arrival — turn the light on for 30 minutes.
                if self.get_state(entity_id=self.Target_Light) == "off":
                    self.turn_on(entity_id=self.Target_Light)
                self.duration_of_light = 1800  # 30 minutes
                self.first_pass = False
                self.log("%s: someone arrived home — light on for 30 minutes.", self.Target_Light)
                self.run_in(self.flashing_light, self.duration_of_light)
            else:
                # 30 minutes have elapsed since arrival — turn off and stop.
                if self.get_state(entity_id=self.Target_Light) == "on":
                    self.turn_off(entity_id=self.Target_Light)
                self.log("%s: 30-minute arrival window ended — light off.", self.Target_Light)
