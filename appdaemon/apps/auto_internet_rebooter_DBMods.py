from datetime import datetime, time

import appdaemon.plugins.hass.hassapi as hass

#
# Auto Crappy Internet Rebooter
# Developed by @UbhiTS on GitHub
# Modified by DB
# Args:
# internet_health_monitor:
#  module: auto_internet_rebooter_DBMods
#  class: AutoInternetRebooter
#  internet:
#    download: sensor.speedtest_download
#    upload: sensor.speedtest_upload
#    ping: sensor.speedtest_ping
#    switch: switch.garage_internet_switch
#  thresholds:
#    download_mbps: 50.0
#    upload_mbps: 3.5
#    ping_ms: 75
#  notify:
#    alexa: media_player.upper_big_bedroom_alexa
#    start_time: "08:00:00"
#    end_time: "21:30:00"
#  debug: false


class AutoInternetRebooter(hass.Hass):
    def initialize(self):

        self.debug = True
        self.counter = 0
        self.unavailable_count = 0
        self.unavailable_threshold = float(
            self.args["thresholds"]["unavailable_threshold"]
        )
        self.delay = float(self.args["delay"])
        self.sensor_download = self.args["internet"]["download"]
        self.sensor_upload = self.args["internet"]["upload"]
        self.sensor_ping = self.args["internet"]["ping"]
        self.switch = self.args["internet"]["switch"]

        self.threshold_download = float(self.args["thresholds"]["download_mbps"])
        self.threshold_upload = float(self.args["thresholds"]["upload_mbps"])
        self.threshold_ping = float(self.args["thresholds"]["ping_ms"])

        self.notify = False

        if "notify" in self.args:
            self.notify = True
            self.google = self.args["notify"]["google"]
            self.notify_start_time = datetime.strptime(
                self.args["notify"]["start_time"], "%H:%M:%S"
            ).time()
            self.notify_end_time = datetime.strptime(
                self.args["notify"]["end_time"], "%H:%M:%S"
            ).time()

        # we just need to monitor ping as ping has a precision of 3 (20.943 ms )
        # highly unlikely that 2 tests will result in same ping speed
        self.listen_handle = self.listen_state(
            self.evaluate_internet_health, self.sensor_ping, attribute="state"
        )

        self.debug_log(
            f"\n**** INIT - AUTO 'CRAPPY INTERNET' REBOOTER ****  D/L  {self.threshold_download}  U/L   {self.threshold_upload}  PING {self.threshold_ping}"
        )

        self.debug = bool(self.args["debug"]) if "debug" in self.args else self.debug

    def evaluate_internet_health(self, *args):
        speed_download = self.threshold_download
        speed_upload = self.threshold_upload
        speed_ping = self.threshold_ping

        try:
            speed_download = float(self.get_state(self.sensor_download))
            speed_upload = float(self.get_state(self.sensor_upload))
            speed_ping = float(self.get_state(self.sensor_ping))
        except ValueError:
            self.debug_log("UNAVAILABLE")  # will check again
            self.unavailable_count += 1
            self.call_service(
                "homeassistant/update_entity", entity_id="sensor.speedtest_ping"
            )
            if self.get_state(self.sensor_ping) != "unavailable":
                return
        except:
            self.debug_log("PASSED")
            pass

        d = speed_download < self.threshold_download
        u = speed_upload < self.threshold_upload
        p = speed_ping > self.threshold_ping
        v = self.get_state(self.sensor_ping) == "unavailable"

        if d or u or p or v:

            log = []
            if d:
                log += [f"D/L {self.threshold_download}|{speed_download}"]
            if u:
                log += [f"U/L {self.threshold_upload}|{speed_upload}"]
            if p:
                log += [f"PING {self.threshold_ping}|{speed_ping}"]
            if v:
                log += [f"INTERNET UNAVAILABLE"]

            if self.unavailable_count > 1:
                pass # looping through unavailable loop
            else:
                self.log(
                    "INTERNET HEALTH ERROR, ROUTER WILL BE RECYCLED: " + ", ".join(log)
                )
                self.debug_log("INTERNET POWER CYCLE SOON")

            if self.unavailable_count <= self.unavailable_threshold:
                pass # no messages while checking unavailability
            else:
                if self.notify and self.is_time_okay(
                    self.notify_start_time, self.notify_end_time
                ):
                    self.call_service(
                        "tts/google_translate_say",
                        entity_id=self.google,
                        message="Your attention please Wendy, internet connection has been lost. The router will be recycled!",
                    )

            self.counter = self.counter + 1
            if self.unavailable_count > 1:
                pass  # looping through unavailable loop
            else:
                self.cancel_listen_state(
                    self.listen_handle
                )  # stop listening during the delay

            if self.counter == 1:  # on the first pass recycle Router
                self.debug_log("PASS 1 RECYCLING ROUTER")
                self.run_in(self.turn_off_switch, 30)
                self.run_in(self.turn_on_switch, 45)
            else:  # on the second pass recycle Router every delay minutes
                self.debug_log(
                    f"PASS {self.counter} RECYCLING ROUTER, WILL START IN: {((30+self.delay)/60)} Minutes"
                )
                self.run_in(self.turn_off_switch, (30 + self.delay))
                self.run_in(self.turn_on_switch, (45 + self.delay))
        else:
            #self.debug_log("INTERNET SPEED TEST IS OK")
            if self.get_state(self.switch) == "off":
                self.turn_on(
                    entity_id=self.switch
                )  # in case the switch doesnt respone to turn of function
            self.counter = 0
            self.unavailable_count = 0

    def turn_off_switch(self, kwargs):
        if self.unavailable_count <= self.unavailable_threshold:
            self.debug_log(f"TURN OFF UNAVAILABLE PASS Number {self.unavailable_count}")
            return
        self.debug_log("INTERNET RESET : TURN OFF")
        # self.call_service("light/turn_off", entity_id = self.switch)
        if self.get_state(self.switch) == "on":
            self.turn_off(entity_id=self.switch)
            if self.get_state(self.switch) == "on":  # making sure it works
                self.turn_off(entity_id=self.switch)
                if self.get_state(self.switch) == "on":  # making sure it works
                    self.turn_off(entity_id=self.switch)
        else:
            self.debug_log("ERROR ROUTER ALREADY OFF")

    def turn_on_switch(self, kwargs):
        if self.unavailable_count <= self.unavailable_threshold:
            self.debug_log(f"TURN ON UNAVAILABLE PASS Number {self.unavailable_count}")
            # unavailable so need to cycle through without Listen trigger
            if self.get_state(self.sensor_ping) == "unavailable":
                self.run_in(self.evaluate_internet_health, 0)
            else:
                self.log(f"NO LONGER UNAVAILABLE BACK TO NORMAL")
                self.listen_handle = self.listen_state(
                    self.evaluate_internet_health, self.sensor_ping, attribute="state"
                )
        else:
            self.unavailable_count = 0
            self.debug_log("INTERNET RESET : TURN ON")
            if self.counter >= 1:  # Start listening again
                self.listen_handle = self.listen_state(
                    self.evaluate_internet_health, self.sensor_ping, attribute="state"
                )

            if self.get_state(self.switch) == "off":
                self.turn_on(entity_id=self.switch)
                if self.get_state(self.switch) == "off":  # making sure it works
                    self.turn_on(entity_id=self.switch)
                self.log(f"RESET COMPLETE: BACK TO NORMAL")
            else:
                self.debug_log("ERROR ROUTER ALREADY ON")

    def is_time_okay(self, start, end):
        current_time = datetime.now().time()
        if start < end:
            return start <= current_time and current_time <= end
        else:
            return start <= current_time or current_time <= end

    def debug_log(self, message):
        if self.debug:
            self.log(message)
