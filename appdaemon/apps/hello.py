import appdaemon.plugins.hass.hassapi as hass

#
# Hellow World App
#
# Args:
#

class HelloWorld(hass.Hass):

  def initialize(self):
     self.log("Hello from AppDaemon")
     self.log("You are now ready to run Apps!")
     self.turn_off('switch.tasmota')
     self.test(argument1 ="viola", match = self.entities.switch.tasmota.state)

  def test(self, argument1, match, **kwargs):
      self.log("argument1 is: %s", argument1)
      self.log("Hello from test function %s and %s", argument1, match)
      #if self.entities.switch.tasmota.state == 'off':  # check for none
          #self.turn_on('switch.tasmota')
      self.log("Testing 1 2 3: %s", self.entities.switch.tasmota.state )
