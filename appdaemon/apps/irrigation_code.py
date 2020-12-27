import appdaemon.plugins.hass.hassapi as hass
import datetime
#
class Home_Irrigation(hass.Hass):

  def initialize(self):
     self.start_time = self.args["START_TIME"]
     self.start_days = self.args["START_DAYS"].split(",") # split up supplied days list
     self.dayz = ('mon','tue','wed','thu','fri','sat','sun')  # work out todays date
     self.precipitation_threshold = self.args["PRECIPITATION_THRESHOLD"] # the rain chance probability after which irrigating will occur
     self.precipitation_threshold_48 = self.args["PRECIPITATION_THRESHOLD_48"]
     self.watering_threshold = self.args["WATERING_THRESHOLD"]  # the daily watering point where irrigating will occur
     self.reset_backet = self.args["RESET_BUCKET"]  # signals to an irrigation instance to rest the bucket
     self.no_of_schedules = self.args["NO_OF_SCHEDULES"]
     self.master_valve_lead_time = self.args["MASTER_VALVE_LEAD_TIME"]
     self.valve_lead_time = self.args["VALVE_LEAD_TIME"]
     self.station1 = self.args["STATION_1"]
     self.station2 = self.args["STATION_2"]
     self.station3 = self.args["STATION_3"]
     self.station4 = self.args["STATION_4"]
     self.station5 = self.args["STATION_5"]
     self.station6 = self.args["STATION_6"]
     self.station7 = self.args["STATION_7"]
     self.station1_weight = self.args["STATION_1_WEIGHT"]
     self.station2_weight = self.args["STATION_2_WEIGHT"]
     self.station3_weight = self.args["STATION_3_WEIGHT"]
     self.station4_weight = self.args["STATION_4_WEIGHT"]
     self.station5_weight = self.args["STATION_5_WEIGHT"]
     self.station6_weight = self.args["STATION_6_WEIGHT"]
     self.station7_weight = self.args["STATION_7_WEIGHT"]
     self.window1 = self.args["STATION_1_WINDOW"] # window of the WaterMe irrigation cycle
     self.window2 = self.args["STATION_2_WINDOW"]
     self.window3 = self.args["STATION_3_WINDOW"]
     self.window4 = self.args["STATION_4_WINDOW"]
     self.window5 = self.args["STATION_5_WINDOW"]
     self.window6 = self.args["STATION_6_WINDOW"]
     self.window7 = self.args["STATION_7_WINDOW"]

     self.run_daily(self.main_routine, self.start_time)
     # self.run_in(self.main_routine, 0)

  def main_routine(self, *args):
     if self.dayz[datetime.datetime.today().weekday()] in self.start_days:
         # self.log(f"Yes, found {self.dayz[datetime.datetime.today().weekday()]} in List: {self.start_days}")

         self.running_time = self.render_template("{{states('sensor.smart_irrigation_daily_adjusted_run_time') | int}}")
         self.chance_of_precipitation = self.render_template("{{states('sensor.precip_chance') | int}}")
         self.chance_of_precipitation_48hrs = self.render_template("{{states('sensor.wupws_precip_chance_2d') | int}}")

         self.log(f"Daily is: {self.running_time} seconds. Hourly is: {int(self.get_state('sensor.smart_irrigation_hourly_adjusted_run_time'))} seconds. Probability of Rain: {self.chance_of_precipitation}%. Probability of Rain 24hrs: {self.chance_of_precipitation_48hrs}%. Watering Threshold: {self.watering_threshold}sec. ")

         if int(self.get_state('sensor.smart_irrigation_hourly_adjusted_run_time')) > 0 and self.running_time > self.watering_threshold and self.chance_of_precipitation < self.precipitation_threshold and self.chance_of_precipitation_48hrs < self.precipitation_threshold_48:

             if self.station1 != '':  # If not Garden Run then add to cumulative garden run time
                 self.cumulative_total = round(self.render_template("{{states('sensor.smart_irrigation_daily_adjusted_run_time') | int}}") / self.no_of_schedules + self.render_template("{{states('input_number.garden_watering_time') | int}}"),0) #store run time for gardens
                 self.set_value("input_number.garden_watering_time",self.cumulative_total) # store persistently
                 self.log(f"Cumulative Garden Run Time: {self.cumulative_total}secs")

             self.running_time = self.running_time / self.no_of_schedules
             self.garden_running_time = self.render_template("{{states('input_number.garden_watering_time') | int}}")

             self.log(f"Starting Irrigation. ")
             if self.station1 != '': self.station1_running_time = self.running_time*self.station1_weight
             else: self.station1_running_time = 0.0001
             # check if calculated time fits into window
             if self.station1_running_time >= (self.window1-self.master_valve_lead_time-self.valve_lead_time): self.station1_running_time = self.window1-self.master_valve_lead_time-self.valve_lead_time

             if self.station2 != '': self.station2_running_time = self.running_time*self.station2_weight
             else: self.station2_running_time = 0.0001
             if self.station2_running_time >= (self.window2-self.master_valve_lead_time-self.valve_lead_time): self.station2_running_time = self.window2-self.master_valve_lead_time-self.valve_lead_time

             if self.station3 != '': self.station3_running_time = self.running_time*self.station3_weight
             else: self.station3_running_time = 0.0001
             if self.station3_running_time >= (self.window3-self.master_valve_lead_time-self.valve_lead_time): self.station3_running_time = self.window3-self.master_valve_lead_time-self.valve_lead_time

             if self.station4 != '': self.station4_running_time = self.running_time*self.station4_weight
             else: self.station4_running_time = 0.0001
             if self.station4_running_time >= (self.window4-self.master_valve_lead_time-self.valve_lead_time): self.station4_running_time = self.window4-self.master_valve_lead_time-self.valve_lead_time

             if self.station5 != '': self.station5_running_time = self.garden_running_time*self.station5_weight
             else: self.station5_running_time = 0.0001
             if self.station5_running_time >= (self.window5-self.master_valve_lead_time-self.valve_lead_time): self.station5_running_time = self.window5-self.master_valve_lead_time-self.valve_lead_time

             if self.station6 != '': self.station6_running_time = self.garden_running_time*self.station6_weight
             else: self.station6_running_time = 0.0001
             if self.station6_running_time >= (self.window6-self.master_valve_lead_time-self.valve_lead_time): self.station6_running_time = self.window6-self.master_valve_lead_time-self.valve_lead_time

             if self.station7 != '': self.station7_running_time = self.running_time*self.station4_weight
             else: self.station7_running_time = 0.0001
             if self.station7_running_time >= (self.window7-self.master_valve_lead_time-self.valve_lead_time): self.station7_running_time = self.window7-self.master_valve_lead_time-self.valve_lead_time

             self.log(f"Station running times (minutes): Station 1: {self.station1_running_time/60:.2f} Station 2: {self.station2_running_time/60:.2f} Station 3: {self.station3_running_time/60:.2f} Station 4: {self.station4_running_time/60:.2f} Station 5: {self.station5_running_time/60:.2f} Station 6: {self.station6_running_time/60:.2f} Station 7: {self.station7_running_time/60:.2f}")
             # make sure all valves are off
             if self.station1 != '': self.turn_off(self.station1)
             if self.station2 != '': self.turn_off(self.station2)
             if self.station3 != '': self.turn_off(self.station3)
             if self.station4 != '': self.turn_off(self.station4)
             if self.station5 != '': self.turn_off(self.station5)
             if self.station6 != '': self.turn_off(self.station6)
             if self.station7 != '': self.turn_off(self.station7)


             # Turn on first station after waiting self.master_valve_lead_time seconds
             if self.station1 != '' and self.station1_running_time > 0.0001:
                 self.running_time = self.master_valve_lead_time
                 self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station1)
                 self.running_time = self.station1_running_time + self.running_time
                 self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station1)
             else: self.window1 = 0
              # Turn on second station after waiting self.master_valve_lead_time + first window seconds
             if self.station2 != '' and self.station2_running_time > 0.0001:
                 self.running_time = self.window1 + self.valve_lead_time
                 self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station2)
                 self.running_time = self.station2_running_time + self.running_time
                 self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station2)
             else: self.window2 = 0

             if self.station3 != '' and self.station3_running_time > 0.0001:
                 self.running_time = self.window1 + self.window2 + self.valve_lead_time
                 self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station3)
                 self.running_time = self.station3_running_time + self.running_time
                 self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station3)
             else: self.window3 = 0

             if self.station4 != ''  and self.station4_running_time > 0.0001:
                 self.running_time = self.window1 + self.window2 + self.window3 + self.valve_lead_time
                 self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station4)
                 self.running_time = self.station4_running_time + self.running_time
                 self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station4)
             else: self.window4 = 0

             if self.station5 != '' and self.station5_running_time > 0.0001:
                 self.running_time = self.window1 + self.window2 + self.window3 + self.window4 + self.valve_lead_time
                 self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station5)
                 self.running_time = self.station5_running_time + self.running_time
                 self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station5)
             else: self.window5 = 0

             if self.station6 != ''  and self.station6_running_time > 0.0001:
                 self.running_time = self.window1 + self.window2 + self.window3 + self.window4 + self.window5 + self.valve_lead_time
                 self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station6)
                 self.running_time = self.station6_running_time + self.running_time
                 self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station6)
                 self.set_value("input_number.garden_watering_time", 0)  # reset cumulative garden running time
             else: self.window6 = 0

             if self.station7 != ''  and self.station7_running_time > 0.0001:
                 self.running_time = self.window1 + self.window2 + self.window3 + self.window4 + self.window5 + self.window6 + self.valve_lead_time
                 self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station7)
                 self.running_time = self.station7_running_time + self.running_time
                 self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station7)
             else: self.window7 = 0

             if self.reset_backet:
                 self.call_service("smart_irrigation/smart_irrigation_reset_bucket", entityid = "sensor.smart_irrigation_bucket")
                 self.log("Reset complete")

             self.log("Irrigation schedule set")

         else:
             self.log("Irrigation not needed")
     else:
         self.log("Wrong day")
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
