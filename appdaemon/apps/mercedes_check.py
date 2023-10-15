import appdaemon.plugins.hass.hassapi as hass

# App to send a message when tyres are due for realignment
#

class mercedes_tyre_check(hass.Hass):
  def initialize(self):
    self.log("Hello from Mercedes") 
    self.percent_tolerance = self.args["percent_tolerance"]
    self.distance_before = self.args["distance_before"]
    self.msg_sent = False           
        
    # self.run_every(self.main_routine,"now", 15)
    
    self.run_daily(self.main_routine, "9:00:00")

  def Check_Kilometers(self, kms, limit, multiple): # odometer, Percent tolerance , distance before notice    
    kms = str(round(kms/multiple,2)).split('.', 1)[1]
    if int(kms) >= 100-limit:
        return True
    else:
        return False     

  def main_routine(self, *args):
    self.ODOMETER = int(self.get_state(self.args["ODOMETER"]))
    self.log(f"Daily check on Odometer:  {self.ODOMETER}")
    self.tyre_check_switch = self.get_state(self.args["tyre_check_switch"])
    self.log(f"Switch is {self.tyre_check_switch}")    
        
    if self.tyre_check_switch == 'on' and self.Check_Kilometers(self.ODOMETER, self.percent_tolerance, self.distance_before):
      self.notify("Reminder to get tyres checked", title = "Tyre Alignment", name = "notify")
      self.log ("Reminder to get tyres checked")
      self.msg_sent = True
    if self.tyre_check_switch == 'on' and not self.Check_Kilometers(self.ODOMETER, self.percent_tolerance, self.distance_before):
      self.turn_off(entity_id="input_boolean.check_odometer")      
      self.log("turned switch off as service not due")
    if self.tyre_check_switch == 'off' and not self.Check_Kilometers(self.ODOMETER, self.percent_tolerance, self.distance_before):
      self.log("no action")
    if self.tyre_check_switch == 'off' and self.Check_Kilometers(self.ODOMETER, self.percent_tolerance, self.distance_before):
      if not self.msg_sent: 
        self.turn_on(entity_id="input_boolean.check_odometer")
        self.msg_sent = True
        self.notify("Get tyres checked", title = "Tyre Alignment", name = "notify")      
        self.log("Get tyres checked")
      
      
