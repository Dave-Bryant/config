import appdaemon.plugins.hass.hassapi as hass

#
# Hellow World App
#
# Argss:
#

class HelloWorld(hass.Hass):

  def initialize(self):
     self.log("Hello from AppDaemon")
     self.log("You are now ready to run Apps!")
     my_global_var = self.config["global_var"]
     self.log("here comes the global var %s", my_global_var )
     self.config["global_var"] = "howzat"
     my_global_var = self.config["global_var"]
     self.log("here comes the global var %s", my_global_var )
     self.turn_off('switch.frlawnwest')
     self.test(argument1 ="viola", match = self.entities.switch.frlawnwest.state)

  def test(self, argument1, match, **kwargs):
      self.log("argument1 is: %s", argument1)
      self.log("Hello from test function %s and %s", argument1, match)
      self.station1_running_time = 0.0001
      self.log(f"Station running times (minutes): Station 1: {self.station1_running_time/60:.2f}")
      #if self.entities.switch.tasmota.state == 'off':  # check for none
          #self.turn_on('switch.tasmota')
      self.log("Testing 1 2 3: %s", self.entities.switch.frlawnwest.state )
