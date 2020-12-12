import appdaemon.plugins.hass.hassapi as hass

#
# Hellow World App
#
# Args:
#

class HelloWorld(hass.Hass):

  def initialize(self):
     self.log("Hello from AppDaemon")

     self.log("here comes the global var %s", self.config["global_irrigation_cumulative_daily_adjusted_run_time"] )

     # self.config["global_irrigation_cumulative_daily_adjusted_run_time"] = 0

     self.log("here comes the global var %s", self.config["global_irrigation_cumulative_daily_adjusted_run_time"] )

     self.test(argument1 ="viola", match = self.entities.switch.frlawnwest.state)

  def test(self, argument1, match, **kwargs):
      self.log("argument1 is: %s", argument1)
      self.log("Hello from test function %s and %s", argument1, match)
      self.station1_running_time = 0.0001
      self.log(f"Testing running times (minutes): Tester 1: {self.station1_running_time/60:.2f}")
      #if self.entities.switch.tasmota.state == 'off':  # check for none
          #self.turn_on('switch.tasmota')
      self.chance_of_precipitation = self.render_template("{{states('sensor.wupws_precip_chance_1d') | int}}")
      self.log("Chance of precipitation: %s", self.chance_of_precipitation)
      # self.set_value("input_number.garden_watering_time", 400)
      self.log("garden_watering_time: %s", self.render_template("{{states('input_number.garden_watering_time') | int}}"))
