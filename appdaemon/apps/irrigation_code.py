import datetime

import appdaemon.plugins.hass.hassapi as hass


#
class Home_Irrigation(hass.Hass):

  def initialize(self):
     self.start_time = self.args["START_TIME"]
     self.start_days = self.args["START_DAYS"].split(",") # split up supplied days list
     self.dayz = ('mon','tue','wed','thu','fri','sat','sun')  # work out todays date
     self.precipitation_threshold = self.args["PRECIPITATION_THRESHOLD"] # the rain chance probability after which irrigating will occur
     self.precipitation_threshold_48 = self.args["PRECIPITATION_THRESHOLD_48"]
     self.watering_threshold = self.args["WATERING_THRESHOLD"]  # the daily watering point where irrigating will occur
     #self.reset_bucket = self.args["RESET_BUCKET"]  # signals to an irrigation instance to reset the bucket
     self.garden_run = self.args["GARDEN_RUN"] # signals to an irrigation instance to reset the garde watering cumulative total as this instance will water the garden
     self.no_of_schedules = self.args["NO_OF_SCHEDULES"]
     self.valve_lead_time = self.args["VALVE_LEAD_TIME"]
     self.master_valve_lead_time = self.args["MASTER_VALVE_LEAD_TIME"]

     self.start_time = self.parse_time(self.start_time, aware=False) # Tried aware =True and got an error TypeError: can't compare offset-naive and offset-aware datetimes. Changed to false to see how it goes.
     self.run_daily(self.main_routine, self.start_time)  #####
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

         # if API is down then set variables to zero and 100 to ensure Irrigation not needed
         if self.get_state("sensor.high_temperature_today") == 0:
            self.running_time = 0.0
            # set up all the variables
            self.chance_of_precipitation = 100.0
            self.chance_of_precipitation_48hrs = 100.0
            self.precipitation = 10.0
            # self.hourly_adjusted_running_time =  0.0
            self.log("WU API is down, set variables to zero and 100 to ensure Irrigation not needed")
         else:
            self.running_time = float(self.get_state('input_number.lawn_watering_time'))
            # set up all the variables
            self.chance_of_precipitation = float(self.get_state('sensor.precip_chance_today'))
            self.chance_of_precipitation_48hrs = float(self.get_state('sensor.precip_chance_tomorrow'))
            self.precipitation = float(self.get_state('sensor.dailyrain'))
            # self.hourly_adjusted_running_time =  float(self.get_state('sensor.smart_irrigation_hourly_netto_precipitation'))

         # Find first switch then remove master valve times from all other switches
         for i in self.stations:
             if i[:6] == 'switch':
                 self.firstswitch = self.stations[i]['self.number']
                 break
         for i in self.stations:
             if int(self.stations[i]['self.number']) != int(self.firstswitch):
                self.stations[i]['self.window_start'] = int(self.stations[i]['self.window_start']) - int(self.master_valve_lead_time)

         # print report to log
         self.log(f"Daily is: {self.running_time} seconds. Probability of Rain: {self.chance_of_precipitation}%. Probability of Rain 24hrs: {self.chance_of_precipitation_48hrs}%. Watering Threshold: {self.watering_threshold}sec. Precipitation: {self.precipitation}mm. Garden Watering time: {self.get_state('input_number.garden_watering_time')} sec.")

         # conditions to proceed
         if self.running_time <= self.watering_threshold: self.select_option("input_select.irrigation_status", "Irrigation run time too small")
         if int(self.running_time) == 0: self.select_option("input_select.irrigation_status", "No moisture lost yesterday")
         # if self.hourly_adjusted_running_time <= 0: self.select_option("input_select.irrigation_status", "It has rained")
         if self.chance_of_precipitation > self.precipitation_threshold: self.select_option("input_select.irrigation_status", "Rain is coming")
         if self.chance_of_precipitation_48hrs > self.precipitation_threshold_48: self.select_option("input_select.irrigation_status", "Rain is coming")
         if self.precipitation != 0: self.select_option("input_select.irrigation_status", "It has rained")

         if self.running_time > self.watering_threshold and self.chance_of_precipitation <= self.precipitation_threshold and self.chance_of_precipitation_48hrs <= self.precipitation_threshold_48 and self.precipitation == 0:

             # allocate run time across schedules
             self.running_time = self.running_time / self.no_of_schedules
             self.garden_running_time = float(self.get_state('input_number.garden_watering_time'))

             # If Garden Run then set garden run time, else store run time for gardens
             if self.garden_run:
                 for i in self.stations:
                     if i[0:8] != 'noswitch':
                         self.stations[i]['self.station_running_time'] = self.garden_running_time

                 self.set_value("input_number.garden_watering_time", 0)
                 self.log(f"Reset Cumulative Garden Run Time to zero")
             else:
                 self.cumulative_total = round(self.running_time + float(self.get_state('input_number.garden_watering_time')),0)
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
                      self.running_time = float(self.stations[i]['self.window_start'])
                      # self.log(f" Station: {i} will start in {self.running_time} secs")
                      self.run_in(self.turn_on_station_cb, self.running_time, current_station = i)
                      self.running_time = round(float(self.stations[i]['self.station_running_time']) + float(self.running_time))
                      # self.log(f" Station: {i} will stop in {self.running_time} secs")
                      self.run_in(self.turn_off_station_cb, self.running_time, current_station = i)
                 # else: self.stations[i]['self.window_start'] = 0

            #  if self.reset_bucket:
            #      self.call_service("smart_irrigation/reset_all_buckets") 
            #      # self.call_service("smart_irrigation/smart_irrigation_disable_force_mode") # in case FORCE mode is on
            #      # reset Watering System so daily calaculation is set to zero                 
            #      self.log("Reset complete")

             self.log("Irrigation schedule set")

             # update irrigation status for Lovelace
             self.select_option("input_select.irrigation_status", "Normal")

         else:
             self.log("Irrigation not needed")
             if self.precipitation != 0:            # the rain monitor should do this but this caters for rain within the hour
                self.set_value("input_number.garden_watering_time", 0)
                self.log(f"Reset Cumulative Garden Run Time to zero as it has rained")

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
