import random as random

import appdaemon.plugins.hass.hassapi as hass

class Light_Timer(hass.Hass):
    def initialize(self):

        self.run_in(self.delay_for_person_monitor, 180)

    def delay_for_person_monitor(self, kwargs):
        self.log("started %s", self.args["LIGHT_SWITCH"])
        self.run_at_sunset(
            self.before_sunset_cb, offset=+900
        )  # 15 minutes after sunset
        self.first_pass = True
        # if home assistant restarts during the night
        if self.now_is_between(
            "sunset + 00:15:00", "sunrise - 00:15:00"
        ):  # 15 minutes after sunset
            self.before_sunset_cb("offset=+900")  # kwarg not used

        # self.run_at(self.before_sunset_cb, "09:05:00") test

    def before_sunset_cb(self, kwargs):
        if self.get_state("group.bryant_family") == "not_home":
            # self.log("Starting Light_Timer")
            self.Target_Light = self.args["LIGHT_SWITCH"]
            self.log("Starting %s", self.Target_Light)
            self.flashing_light(
                "dummy"
            )  # function needs an argument for entity_id but I cant pass it as the iteration will blank it out
        else:
            # self.sleep(120)
            self.log("Everyone is home")
            exit

    def flashing_light(self, *args):
        if (
            self.get_state("sun.sun") == "below_horizon"
            and self.get_state("group.bryant_family") == "not_home"
        ):
            self.duration_of_light = random.randint(3, 9) * 600  # 30-90 minutes
            self.toggle(entity_id=self.Target_Light)
            self.first_pass = True
            self.log(
                "Light is %s for %s minutes.",
                self.get_state(entity_id=self.Target_Light),
                self.duration_of_light / 60,
            )
            self.run_in(self.flashing_light, self.duration_of_light)
        else:
            if self.get_state("sun.sun") == "above_horizon":
                if self.get_state(entity_id=self.Target_Light) == "on":
                    self.turn_off(entity_id=self.Target_Light)
                self.log("%s has finished naturally", self.Target_Light)
            if (
                self.get_state("sun.sun") == "above_horizon"
                and self.get_state("group.bryant_family") == "home"
            ):
                if self.first_pass:  # first pass
                    if self.get_state(entity_id=self.Target_Light) == "off":
                        self.turn_on(entity_id=self.Target_Light)
                    self.duration_of_light = 1800
                    self.first_pass = False
                    self.log(
                        "%s first pass has started as someone arrived home",
                        self.Target_Light,
                    )
                    self.run_in(self.flashing_light, self.duration_of_light)
                else:
                    if self.get_state(entity_id=self.Target_Light) == "on":
                        self.turn_off(entity_id=self.Target_Light)
                    self.log(
                        "%s has finished 30 mins after someone has arrived home",
                        self.Target_Light,
                    )
