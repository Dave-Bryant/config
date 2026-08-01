import appdaemon.plugins.hass.hassapi as hass

# App to send a message when tyres are due for realignment
#

class mercedes_tyre_check(hass.Hass):
  def initialize(self):
    self.log("Hello from Mercedes") 
    self.percent_tolerance = self.args["percent_tolerance"]
    self.distance_before = self.args["distance_before"]
    self.msg_sent = False           
        
    #self.run_every(self.main_routine,"now", 15)
    
    self.run_daily(self.main_routine, "9:00:00")

  def Check_Kilometers(self, kms, limit, multiple): #  odometer, Percent tolerance , distance before notice      
    kms = str(round(kms/multiple,3)).split('.', 1)[1]  #  The remainder after division    
    if len(kms) == 1: kms = int(kms) * 100   # make sure the number is 3 digits
    elif len(kms) == 2: kms = int(kms) * 10
    elif len(kms) == 3: kms = int(kms) 
    limit = limit / 1000 * multiple  # calc percentage of multiple    
    return abs(kms - 1000) <= int(limit)   
    

  def main_routine(self, *args):
    if self.get_state(self.args["ODOMETER"]) is None:
        self.log("Mercedes Addon is down")
        return
    self.ODOMETER = int(self.get_state(self.args["ODOMETER"]))
    self.log(f"Daily check on Odometer:  {self.ODOMETER}")
    self.tyre_check_switch = self.get_state(self.args["tyre_check_switch"])
    self.log(f"Switch is {self.tyre_check_switch}")
    self.log(f"Check is: {self.Check_Kilometers(self.ODOMETER, self.percent_tolerance, self.distance_before)}")    
        
            
    if self.tyre_check_switch == 'on' and self.Check_Kilometers(self.ODOMETER, self.percent_tolerance, self.distance_before):
      self.notify("Get tyres checked", title = "Tyre Alignment", name = "notify")      
      self.log("Get tyres checked")
    elif self.tyre_check_switch == 'off' and self.Check_Kilometers(self.ODOMETER, self.percent_tolerance, self.distance_before):  
      self.turn_on(entity_id="input_boolean.check_odometer")
      self.log("Odometer Switch turned on")
    elif self.tyre_check_switch == 'on' and not self.Check_Kilometers(self.ODOMETER, self.percent_tolerance, self.distance_before):
      self.turn_off(entity_id="input_boolean.check_odometer")
      self.log("Odometer Switch turned off")
    else:
      self.log("No Tyre action")
      
    
      
      
