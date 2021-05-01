import appdaemon.plugins.hass.hassapi as hass
import random as random
#
#
class Light_Timer(hass.Hass):

  def initialize(self):
     self.run_at_sunset(self.before_sunset_cb, offset=+900) #15 minutes after sunset
     # self.run_at(self.before_sunset_cb, "09:05:00") test
  def before_sunset_cb(self, kwargs):
     if self.get_state('group.bryant_family') == 'not_home':
         self.log("Starting Light_Timer")
         self.Target_Light = self.args["LIGHT_SWITCH"]
         self.log("Starting %s", self.Target_Light)
         self.flashing_light('dummy') # function needs an argument for entity_id but I cant pass it as the iteration will blank it out
     else:
         self.sleep(120)
         self.log("Everyone is home")
         exit
  def flashing_light(self, *args):
     if self.render_template("{{ is_state('sun.sun', 'below_horizon') }}") == True and self.get_state('group.bryant_family') == 'not_home':
         self.duration_of_light = random.randint(3, 9) * 600 # 30-90 minutes
         self.toggle(entity_id = self.Target_Light)
         self.log('Light is %s for %s minutes.', self.get_state(entity_id = self.Target_Light), self.duration_of_light/60)
         self.run_in(self.flashing_light, self.duration_of_light)
     else:
         if self.get_state(entity_id = self.Target_Light) == 'on': self.turn_off(entity_id = self.Target_Light)
         self.log("%s has finished", self.Target_Light)
         if self.get_state('group.bryant_family') == 'home':
             self.toggle(entity_id = self.Target_Light) # turn on light if finished because I came home
             self.log("%s has been turned on as someone has arrived home", self.Target_Light)
