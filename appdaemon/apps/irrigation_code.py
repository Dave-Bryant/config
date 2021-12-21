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
     self.reset_bucket = self.args["RESET_BUCKET"]  # signals to an irrigation instance to reset the bucket
     self.garden_run = self.args["GARDEN_RUN"] # signals to an irrigation instance to reset the garde watering cumulative total as this instance will water the garden
     self.no_of_schedules = self.args["NO_OF_SCHEDULES"]
     self.valve_lead_time = self.args["VALVE_LEAD_TIME"]
     self.master_valve_lead_time = self.args["MASTER_VALVE_LEAD_TIME"]


     self.run_daily(self.main_routine, self.start_time)
     # self.run_in(self.main_routine, 0)

  def main_routine(self, *args):
     if self.dayz[datetime.datetime.today().weekday()] in self.start_days:

         self.stations = {
                    self.args["STATION_1"]:{'self.number': '1','self.station_weight':self.args["STATION_1_WEIGHT"],'self.window': str(self.args["STATION_1_WINDOW"]), 'self.window_start':str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"]),
                                    'self.station_running_time': ''
                                    },
                    self.args["STATION_2"]:{'self.number': '2','self.station_weight':self.args["STATION_2_WEIGHT"],'self.window': str(self.args["STATION_2_WINDOW"]), 'self.window_start': str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"] + self.args["STATION_1_WINDOW"]),
                                    'self.station_running_time': ''
                                    },
                    self.args["STATION_3"]:{'self.number': '3','self.station_weight':self.args["STATION_3_WEIGHT"],'self.window': str(self.args["STATION_3_WINDOW"]), 'self.window_start': str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"] + self.args["STATION_1_WINDOW"] + self.args["STATION_2_WINDOW"]),
                                    'self.station_running_time': ''
                                    },
                    self.args["STATION_4"]:{'self.number': '4','self.station_weight':self.args["STATION_4_WEIGHT"],'self.window': str(self.args["STATION_4_WINDOW"]), 'self.window_start': str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"] + self.args["STATION_1_WINDOW"] + self.args["STATION_2_WINDOW"] + self.args["STATION_3_WINDOW"]),
                                    'self.station_running_time': ''
                                    },
                    self.args["STATION_5"]:{'self.number': '5','self.station_weight':self.args["STATION_5_WEIGHT"],'self.window': str(self.args["STATION_5_WINDOW"]), 'self.window_start': str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"] + self.args["STATION_1_WINDOW"] + self.args["STATION_2_WINDOW"] + self.args["STATION_3_WINDOW"] + self.args["STATION_4_WINDOW"]),
                                    'self.station_running_time': ''
                                    },
                    self.args["STATION_6"]:{'self.number': '6','self.station_weight':self.args["STATION_6_WEIGHT"],'self.window': str(self.args["STATION_6_WINDOW"]), 'self.window_start': str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"] + self.args["STATION_1_WINDOW"] + self.args["STATION_2_WINDOW"] + self.args["STATION_3_WINDOW"] + self.args["STATION_4_WINDOW"] + self.args["STATION_5_WINDOW"]),
                                    'self.station_running_time': ''
                                    },
                    self.args["STATION_7"]:{'self.number': '7','self.station_weight':self.args["STATION_7_WEIGHT"],'self.window': str(self.args["STATION_7_WINDOW"]), 'self.window_start': str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"] + self.args["STATION_1_WINDOW"] + self.args["STATION_2_WINDOW"] + self.args["STATION_3_WINDOW"] + self.args["STATION_4_WINDOW"] + self.args["STATION_5_WINDOW"] + self.args["STATION_6_WINDOW"]  ),
                                    'self.station_running_time': ''
                                    }
                     }


         # if API is down then use base calculation
         if self.render_template("{{states('sensor.high_temperature_today') | int}}") == 0:
             self.running_time = self.render_template("{{states('sensor.smart_irrigation_base_schedule_index') | int}}")
             self.log("WU API is down, using Base Calculation")
         else:
             self.running_time = self.render_template("{{states('sensor.smart_irrigation_daily_adjusted_run_time') | int}}")

         # set up all the variables
         self.chance_of_precipitation = self.render_template("{{states('sensor.precip_chance_today') | int}}")
         self.chance_of_precipitation_48hrs = self.render_template("{{states('sensor.precip_chance_today') | int}}")
         self.precipitation = self.render_template("{{states('sensor.daily_rain_rate_2') | int}}")
         self.hourly_adjusted_running_time = int(self.get_state('sensor.smart_irrigation_hourly_adjusted_run_time_2'))

         # Find first switch then remove master valve times from all other switches
         for i in self.stations:
             if i[:6] == 'switch':
                 self.firstswitch = self.stations[i]['self.number']
                 break
         for i in self.stations:
             if int(self.stations[i]['self.number']) != int(self.firstswitch):
                self.stations[i]['self.window_start'] = int(self.stations[i]['self.window_start']) - int(self.master_valve_lead_time)

         # print report to log
         self.log(f"Daily is: {self.running_time} seconds. Hourly is: {self.hourly_adjusted_running_time} seconds. Probability of Rain: {self.chance_of_precipitation}%. Probability of Rain 24hrs: {self.chance_of_precipitation_48hrs}%. Watering Threshold: {self.watering_threshold}sec. Precipitation: {self.precipitation}mm. ")

         # conditions to proceed
         if self.hourly_adjusted_running_time > 0 and self.running_time > self.watering_threshold and self.chance_of_precipitation <= self.precipitation_threshold and self.chance_of_precipitation_48hrs <= self.precipitation_threshold_48 and self.precipitation == 0:

             # allocate run time across schedules
             self.running_time = self.running_time / self.no_of_schedules
             self.garden_running_time = self.render_template("{{states('input_number.garden_watering_time') | int}}")

             # If Garden Run then set garden run time, else store run time for gardens
             if self.garden_run:
                 for i in self.stations:
                     if i[0:8] != 'noswitch':
                         self.stations[i]['self.station_running_time'] = self.garden_running_time

                 self.set_value("input_number.garden_watering_time", 0)
                 self.log(f"Reset Cumulative Garden Run Time to zero")
             else:
                 self.cumulative_total = round(self.running_time + self.render_template("{{states('input_number.garden_watering_time') | int}}"),0)
                 self.set_value("input_number.garden_watering_time",self.cumulative_total) # store persistently
                 self.log(f"Cumulative Garden Run Time: {self.cumulative_total}secs")


             self.log(f"Starting Irrigation. ")

             # weight the running time & remove excess time for missing stations
             for i in self.stations:
                 if i[0:8] != 'noswitch':
                     self.stations[i]['self.station_running_time'] = self.running_time*self.stations[i]['self.station_weight']
                     self.avaiable_time = int(str(self.stations[i]['self.window']))-int(self.valve_lead_time)
                     if int(self.stations[i]['self.station_running_time']) >= self.avaiable_time :
                         self.stations[i]['self.station_running_time'] = self.avaiable_time
                         self.log(f"{i} has maxed out")
                 else:   # remove all the window of time from the schedule for the missing stations
                     self.stations[i]['self.station_running_time'] = 0.0001
                     for j in self.stations:
                         if int(self.stations[j]['self.number']) > int(self.stations[i]['self.number']):
                               self.stations[j]['self.window_start'] = int(self.stations[j]['self.window_start']) - int(self.stations[i]['self.window'])

             # print report to log
             for i in self.stations:
                  self.converted_time = self.convert_seconds(float(self.stations[i]['self.station_running_time']))
                  self.converted_time = self.converted_time.split('.', 1)[0]
                  if i != 'noswitch': self.log(f"Station running times (minutes): Station {self.stations[i]['self.number']}: {self.converted_time}")

             # update lovelace fields
             for i in self.stations:
                  if i[0:8] != 'noswitch': self.set_textvalue("input_text." + str(i)[7:] + "_run_duration",self.stations[i]['self.station_running_time'])

             # make sure all valves are off
             for i in self.stations:
                 if i[0:8] != 'noswitch': self.turn_off(i)

             # Turn on stations after waiting window seconds
             for i in self.stations:  # the station variable assigned e.g. switch.frlawneast
                 if i[0:8] != 'noswitch' and float(self.stations[i]['self.station_running_time']) > 0.0001:
                      self.running_time = int(self.stations[i]['self.window_start'])
                      # self.log(f" Station: {i} will start in {self.running_time} secs")
                      self.run_in(self.turn_on_station_cb, self.running_time, current_station = i)
                      self.running_time = round(float(self.stations[i]['self.station_running_time']) + float(self.running_time))
                      # self.log(f" Station: {i} will stop in {self.running_time} secs")
                      self.run_in(self.turn_off_station_cb, self.running_time, current_station = i)
                 # else: self.stations[i]['self.window_start'] = 0

             if self.reset_bucket:
                 self.call_service("smart_irrigation/smart_irrigation_reset_bucket", entityid = "sensor.smart_irrigation_bucket")
                 self.call_service("smart_irrigation/smart_irrigation_disable_force_mode") # in case FORCE mode is on
                 self.log("Reset complete")

             self.log("Irrigation schedule set")

         else:
             self.log("Irrigation not needed")
             self.set_value("input_number.garden_watering_time", 0)
             self.log(f"Reset Cumulative Garden Run Time to zero")
     else:
         self.log("Wrong day")
# Methods

  def turn_on_station_cb(self, kwargs): # run in decorator for run_in
      self.turn_on_station(kwargs["current_station"])
  def turn_on_station(self, current_station):
      if self.get_state(current_station) == 'off':
          if self.precipitation == 0:
              self.turn_on(current_station)
              self.log("Started Station watering: %s Valve is on", current_station)
              self.set_textvalue("input_text." + current_station[7:] + "_run_date",datetime.datetime.today().strftime("%d/%m"))
              self.set_textvalue("input_text." + current_station[7:] + "_run_time",datetime.datetime.today().strftime("%H:%M"))
          else:
              self.log("%s is not needed as raining already", current_station)
      else:
          self.log("%s is already on...could be an error", current_station)


  def turn_off_station_cb(self, kwargs): # run in decorator for run_in
      self.turn_off_station(kwargs["current_station"])
  def turn_off_station(self, current_station):
      if self.get_state(current_station) == 'on':
          self.turn_off(current_station)
      else:
          self.log("%s is already off...could be an error or could have rained", current_station)
      self.log("Stopped Station watering: %s Valve is off", current_station)

  def convert_seconds(self,n):
      return str(datetime.timedelta(seconds = n))
