import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Hellow World App
#
# Args:
#

class HelloWorld(hass.Hass):

  def initialize(self):
     self.log("Hello from AppDaemon")

     self.log("here comes the global var %s", self.config["global_irrigation_cumulative_daily_adjusted_run_time"] )

     self.test(argument1 ="viola", match = self.entities.switch.frlawnwest.state)

  def test(self, argument1, match, **kwargs):
      self.log("argument1 is: %s", argument1)
      self.log("Hello from test function %s and %s", argument1, match)
