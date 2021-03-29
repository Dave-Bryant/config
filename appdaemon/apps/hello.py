import appdaemon.plugins.hass.hassapi as hass
import datetime

# Hellow World App
#
# Args:
#


class HelloWorld(hass.Hass):

  def initialize(self):
     self.log("Hello from AppDaemon")

     self.run_in(self.main_routine, 0)

  def main_routine(self, *args):
      self.log("Hello from main main_routine")
