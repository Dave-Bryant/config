import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, time

#
# Auto Crappy Internet Rebooter
# Developed by @UbhiTS on GitHub
#
# Args:
#internet_health_monitor:
#  module: auto_internet_rebooter
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
#  schedule:
#    - "04:00:00"
#    - "16:00:00"
#  notify:
#    alexa: media_player.upper_big_bedroom_alexa
#    start_time: "08:00:00"
#    end_time: "21:30:00"
#  debug: false


class AutoInternetRebooter(hass.Hass):

  def initialize(self):

    self.debug = True;
    self.counter = 0
    self.delay = float(self.args["delay"])
    self.sensor_download = self.args["internet"]["download"]
    self.sensor_upload = self.args["internet"]["upload"]
    self.sensor_ping = self.args["internet"]["ping"]
    self.switch = self.args["internet"]["switch"]

    self.threshold_download = float(self.args["thresholds"]["download_mbps"])
    self.threshold_upload = float(self.args["thresholds"]["upload_mbps"])
    self.threshold_ping = float(self.args["thresholds"]["ping_ms"])

    self.schedule = self.args["schedule"]

    self.notify = False

    if "notify" in self.args:
      self.notify = True
      self.google = self.args["notify"]["google"]
      self.notify_start_time = datetime.strptime(self.args["notify"]["start_time"], '%H:%M:%S').time()
      self.notify_end_time = datetime.strptime(self.args["notify"]["end_time"], '%H:%M:%S').time()

    for schedule in self.schedule:
      time = datetime.strptime(schedule, '%H:%M:%S').time()
      self.run_daily(self.run_speedtest, time)

    # we just need to monitor ping as ping has a precision of 3 (20.943 ms)
    # highly unlikely that 2 tests will result in same ping speed
    self.listen_handle = self.listen_state(self.evaluate_internet_health, self.sensor_ping, attribute = "state")
    #self.listen_handle_unavail = self.listen_state(self.evaluate_internet_health, self.sensor_ping, attribute = "state", new = "unavailable")

    self.debug_log(f"\n**** INIT - AUTO 'CRAPPY INTERNET' REBOOTER ****\n  D/L  {self.threshold_download}\n  U/L   {self.threshold_upload}\n  PING {self.threshold_ping}")

    self.debug = bool(self.args["debug"]) if "debug" in self.args else self.debug


  async def run_speedtest(self, kwargs):
    self.debug_log("INTERNET SPEED TEST IN PROGRESS")
    self.call_service("homeassistant/update_entity", entity_id = "sensor.speedtest_ping")


  def evaluate_internet_health(self, entity, attribute, old, new, kwargs):

    speed_download = self.threshold_download
    speed_upload = self.threshold_upload
    speed_ping = self.threshold_ping

    try:
      speed_download = float(self.get_state(self.sensor_download))
      speed_upload = float(self.get_state(self.sensor_upload))
      speed_ping = float(self.get_state(self.sensor_ping))
    except ValueError:
      self.debug_log("UNAVAILABLE")
    except:
      self.debug_log("PASSED")
      pass

    d = speed_download < self.threshold_download
    u = speed_upload < self.threshold_upload
    p = speed_ping > self.threshold_ping
    v = (self.get_state(self.sensor_ping) == 'unavailable')

    if d or u or p or v:

      log = []
      if d: log += [f"D/L {self.threshold_download}|{speed_download}"]
      if u: log += [f"U/L {self.threshold_upload}|{speed_upload}"]
      if p: log += [f"PING {self.threshold_ping}|{speed_ping}"]
      if v: log += [f"INTERNET UNAVAILABLE"]
      self.log("INTERNET HEALTH ERROR, ROUTER WILL BE RECYCLED: " + ", ".join(log))
      self.debug_log("INTERNET POWER CYCLE SOON")

      if self.notify and self.is_time_okay(self.notify_start_time, self.notify_end_time):
        self.call_service("tts/google_translate_say",
                           entity_id = self.google,
                           message = "Your attention please Wendy, internet connection has been lost. The router will be recycled!"
                            )
        pass

      self.counter = self.counter + 1
      self.cancel_listen_state(self.listen_handle) # stop listening during the delay
      #self.cancel_listen_state(self.listen_handle_unavail)

      if self.counter == 1:                # on the first pass recycle Router
          self.debug_log("PASS 1 RECYCLING ROUTER")
          self.run_in(self.turn_off_switch, 30)
          self.run_in(self.turn_on_switch, 45)
      else:                                 # on the second pass recycle Router every delay minutes
          self.debug_log(f"PASS {self.counter} RECYCLING ROUTER, WILL START IN: {((30+self.delay)/60)} Minutes" )
          self.run_in(self.turn_off_switch, (30+self.delay))
          self.run_in(self.turn_on_switch, (45+self.delay))


    else:
      #self.debug_log("INTERNET SPEED TEST IS OK")
      self.counter = 0


  def turn_off_switch(self, kwargs):
    self.debug_log("INTERNET RESET : TURN OFF")
    #self.call_service("light/turn_off", entity_id = self.switch)
    if self.get_state(self.switch) == 'on':
        self.turn_off(entity_id=self.switch)
        if self.get_state(self.switch) == 'on': # making sure it works
            self.turn_off(entity_id=self.switch)
            if self.get_state(self.switch) == 'on': # making sure it works
                self.turn_off(entity_id=self.switch)
    else:
        self.debug_log("ERROR ROUTER ALREADY OFF")


  def turn_on_switch(self, kwargs):
    self.debug_log("INTERNET RESET : TURN ON")

    if self.counter >= 1:  #Start listening again
        self.listen_handle = self.listen_state(self.evaluate_internet_health, self.sensor_ping, attribute = "state")
        #self.listen_handle_unavail = self.listen_state(self.evaluate_internet_health, self.sensor_ping, attribute = "state", new = "unavailable")

    if self.get_state(self.switch) == 'off':
        self.turn_on(entity_id=self.switch)
        if self.get_state(self.switch) == 'off':   # making sure it works
            self.turn_on(entity_id=self.switch)
    else:
        self.debug_log("ERROR ROUTER ALREADY ON")

  def is_time_okay(self, start, end):
    current_time = datetime.now().time()
    if (start < end):
      return start <= current_time and current_time <= end
    else:
      return start <= current_time or current_time <= end


  def debug_log(self, message):
    if self.debug:
      self.log(message)
