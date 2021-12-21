import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Home Irrigation Force
#
#                             THIS HASNT BEEN TESTED

class Home_Irrigation_Force(hass.Hass):
  def initialize(self):
     self.log("Starting Home Irrigation Force")
     self.listen_state(self.schedule_the_force, "input_boolean.force_irrigation", new = "on")

  def schedule_the_force(self, entity, attribute, old, new, kwargs):
     self.log("FORCE started")
     self.run_in(self.turn_it_off, 3)
     self.call_service("smart_irrigation/smart_irrigation_enable_force_mode")
     self.log("FORCE completed")

  def turn_it_off(self,kwargs):
      self.turn_off("input_boolean.force_irrigation")
