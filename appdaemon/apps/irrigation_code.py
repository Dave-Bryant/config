import appdaemon.plugins.hass.hassapi as hass
#
#
class Home_Irrigation(hass.Hass):

  def initialize(self):
     self.start_time = self.args["START_TIME"]
     self.reset_backet = self.args["RESET_BUCKET"]
     self.no_of_schedules = self.args["NO_OF_SCHEDULES"]
     self.master_valve_lead_time = self.args["MASTER_VALVE_LEAD_TIME"]
     self.valve_lead_time = self.args["VALVE_LEAD_TIME"]
     self.station1 = self.args["STATION_1"]
     self.station2 = self.args["STATION_2"]
     self.station3 = self.args["STATION_3"]
     self.station4 = self.args["STATION_4"]
     self.station1_weight = self.args["STATION_1_WEIGHT"]
     self.station2_weight = self.args["STATION_2_WEIGHT"]
     self.station3_weight = self.args["STATION_3_WEIGHT"]
     self.station4_weight = self.args["STATION_4_WEIGHT"]
     self.window1 = self.args["STATION_1_WINDOW"]
     self.window2 = self.args["STATION_2_WINDOW"]
     self.window3 = self.args["STATION_3_WINDOW"]

     self.run_daily(self.main_routine, self.start_time)
     #self.run_in(self.main_routine, 0)

  def main_routine(self, *args):     # change daily to > 60 to stop small runs
     self.running_time = self.render_template("{{states('sensor.smart_irrigation_daily_adjusted_run_time') | int}}")
     self.log(f"Daily is: {self.running_time} seconds. Hourly is: {int(self.get_state('sensor.smart_irrigation_hourly_adjusted_run_time_2'))} seconds. ")
     if int(self.get_state('sensor.smart_irrigation_hourly_adjusted_run_time_2')) > 0 and self.running_time > 0:
         self.running_time = self.running_time / self.no_of_schedules
         self.log(f"Starting Irrigation. Running time is: {self.running_time/60:.2f} minutes")
         self.station1_running_time = self.running_time*self.station1_weight
         self.station2_running_time = self.running_time*self.station2_weight
         self.station3_running_time = self.running_time*self.station3_weight
         self.station4_running_time = self.running_time*self.station4_weight
         self.log(f"Station running times (minutes): Station 1: {self.station1_running_time/60:.2f} Station 2: {self.station2_running_time/60:.2f} Station3: {self.station3_running_time/60:.2f} Station4: {self.station4_running_time/60:.2f}")
         # make sure all valves are off
         self.turn_off(self.station1)
         self.turn_off(self.station2)
         self.turn_off(self.station3)
         self.turn_off(self.station4)

         # Turn on first station after waiting self.master_valve_lead_time seconds
         self.run_in(self.turn_on_station_cb, self.master_valve_lead_time, current_station = self.station1)
         self.running_time = self.station1_running_time + self.master_valve_lead_time
         self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station1)

         self.running_time = self.window1 + self.valve_lead_time
         self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station2)
         self.running_time = self.station2_running_time + self.running_time
         self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station2)

         self.running_time = self.window1 + self.window2 + self.valve_lead_time
         self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station3)
         self.running_time = self.station3_running_time + self.running_time
         self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station3)

         self.running_time = self.window1 + self.window2 + self.window3 + self.valve_lead_time
         self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station4)
         self.running_time = self.station4_running_time + self.running_time
         self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station4)

         if self.reset_backet:
             self.call_service("smart_irrigation/smart_irrigation_reset_bucket", entityid = "sensor.smart_irrigation_bucket")
         self.log("Irrigation schedule set")

     else:
         self.log("Irrigation not needed")         

# Methods

  def turn_on_station_cb(self, kwargs): # run in decorator for run_in
      self.turn_on_station(kwargs["current_station"])
  def turn_on_station(self, current_station):
      if self.get_state(current_station) == 'off':  # check for none
          self.turn_on(current_station)
      else:
          self.log("%s is already on...could be an error", current_station)
      self.log("Started Station watering: %s Valve is on", current_station)

  def turn_off_station_cb(self, kwargs): # run in decorator for run_in
      self.turn_off_station(kwargs["current_station"])
  def turn_off_station(self, current_station):
      if self.get_state(current_station) == 'on':  # check for none
          self.turn_off(current_station)
      else:
          self.log("%s is already off...could be an error", current_station)
      self.log("Stopped Station watering: %s Valve is off", current_station)

  # def transition_station_cb(self, kwargs): # run in decorator for run_in
  #     self.transition_station(kwargs["current_station"],kwargs["next_station"])
  # def transition_station(self, current_station, next_station):
  #     if self.get_state(entity_id = current_station) == 'on':  # check for none
  #          self.turn_off(current_station)
  #          self.log("Finished a Station watering: %s Valve is off", current_station)
  #     else:
  #          self.log("Station already off..possible error")
  #     if next_station is '':
  #         self.log("Finishing...")
  #     elif self.get_state(entity_id = next_station) == 'off':
  #         self.turn_on(next_station)
  #         self.log("Started Station watering: %s Valve is on", next_station)
  #     else:
  #         self.log("Station already on ... posible error")
