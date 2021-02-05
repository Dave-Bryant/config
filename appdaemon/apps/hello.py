import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Hellow World App
#
# Args:
#

class HelloWorld(hass.Hass):

  def initialize(self):
     self.log("Hello from AppDaemon")

     # self.log("here comes the global var %s", self.config["global_irrigation_cumulative_daily_adjusted_run_time"] )
     # self.today = datetime.datetime.today()

     # dd/mm/YY
     # d1 = today.strftime("%d/%m/%Y")


     # self.test_total = d1
     # self.log("self.test_total is: %s", self.test_total)
     # self.test(argument1 ="viola", match = self.entities.switch.frlawnwest.state)
  #    self.listen_state(self.test, "input_boolean.force_irrigation", new = "on")
  #
  #
  # def test(self, entity, attribute, old, new, kwargs):
  #     self.log('it works')
  #     self.run_in(self.turn_it_off, 3)
  #
  # def turn_it_off(self,kwargs):
  #     self.turn_off("input_boolean.force_irrigation")

      # self.station5_running_time = 300
      # self.STATION_5 = 'switch.frlawnwest'
      # self.STATION_5 = "input_text." + self.STATION_5[7:] + "_run_date"
      # self.log(self.STATION_5)


      # self.set_textvalue("input_text." + self.STATION_5[7:] + "_run_date",datetime.datetime.today().strftime("%d/%m/%Y"))
      # self.set_textvalue("input_text." + self.STATION_5[7:] + "_run_time",datetime.datetime.today().strftime("%H:%M"))
      # self.set_textvalue("input_text." + self.STATION_5[7:] + "_run_duration",self.station5_running_time/60)
      #
      # self.log("input_text.frlawnwest_run_date is: %s", self.render_template("{{states('input_text.frlawnwest_run_date') }}"))
      # self.log("input_text.frlawnwest_run_time is: %s", self.render_template("{{states('input_text.frlawnwest_run_time') }}"))
      # self.log("input_text.frlawnwest_run_duration is: %s", self.render_template("{{states('input_text.frlawnwest_run_duration') }}"))

      # if self.render_template("{{states('sensor.samsung_q80_series_65_media_playback_status') | int}}") == 0:
      #     self.log("it is %s", self.render_template("{{states('sensor.samsung_q80_series_65_media_playback_status') | int}}"))
      # self.log("input_text.frlawnwest_run_time is: %s", self.render_template("{{states('input_text.frlawnwest_run_time') }}"))
      # self.log("Hello from test function %s and %s", argument1, match)

     self.Target_Light = "switch.spare_switch"
     if self.get_state(entity_id = self.Target_Light) == 'on': self.turn_off(entity_id = self.Target_Light)

 #
     self.window0 = 10
     self.window1 = 20# window of the WaterMe irrigation cycle
     self.window2 = 30
     self.window3 = 40
     self.station1 = 'switch.frlawnwest'
     self.station2 =  ''
     self.station3 =  'switch.frlawneast'
     self.station4 = 'switch.bklawnsouth'
     self.station1_running_time = 10
     self.station2_running_time = 20
     self.station3_running_time = 30

     self.stations = {
                self.station1:{'self.number': '1','self.station_weight':.75,'self.window': 900, 'self.window_start':20,
                                'self.station_running_time': '200'
                                },
                self.station2:{'self.number': '2','self.station_weight':1,'self.window': 900, 'self.window_start': 920,
                                'self.station_running_time': '1200'
                                },
                self.station3:{'self.number': '3','self.station_weight':1.5,'self.window': 1200, 'self.window_start': 1840,
                                'self.station_running_time': '400'
                                },
                self.station4:{'self.number': '4','self.station_weight':1.5,'self.window': 1200, 'self.window_start': 2600,
                                'self.station_running_time': '500'
                                }
                 }


     # nk = next_key(self.stations, self.station1)
     # self.log(nk)
     # self.log(self.stations['switch.frlawneast']['self.station_weight'])
     # self.log(self.stations['switch.frlawneast']['number'])
     # self.log(self.stations['switch.frlawneast']['self.window'])

     # for i in self.stations:  # the station variable assigned e.g. switch.frlawneast
     #     # self.log(i)
     #     if i != '' and float(self.stations[i]['self.station_running_time']) > 0.0001:
     #         self.x= self.next_key(self.stations, i)
     #         self.log(self.x)
     #         # self.log(float(self.stations[i]['self.station_running_time']))
     #         # self.running_time = self.stations[i]['self.window']
     #         # self.log('self.running_time is: %s', self.running_time)
     #         # self.running_time = round(float(self.stations[i]['self.station_running_time']) + float(self.running_time)
     #         # self.log('self.running_time is: %s', self.running_time)
     #     else: self.stations[i]['self.window'] = 0
     for i in self.stations:
          self.log(f" Station {self.stations[i]['self.number']}: window {self.stations[i]['self.window']} window_start: {self.stations[i]['self.window_start']} running time: {self.stations[i]['self.station_running_time'] } ")

     for i in self.stations:
         self.log(i[0:7])
         # if i[0:7] != 'noswitch': self.turn_off(i)

     # for i in self.stations:
     #      if i != '':
     #          if int(self.stations[i]['self.station_running_time']) >= self.stations[i]['self.window']: # maxed out
     #             self.log(f"Maxed out")
     #             self.stations[i]['self.station_running_time'] = self.stations[i]['self.window']
     #      else:
     #         missing_station = self.stations[i]['self.number']
     #         self.log(f"Missing station")
     #         for j in self.stations:
     #            if self.stations[j]['self.number'] > missing_station:
     #                self.stations[j]['self.window_start'] = self.stations[j]['self.window_start'] - self.stations[j]['self.window']
     #                self.log(f"{j} updated")
     #            self.log(f" Station {self.stations[j]['self.number']}: window {self.stations[j]['self.window']} window_start: {self.stations[j]['self.window_start']} running time: {self.stations[j]['self.station_running_time'] } ")
     # for i in self.stations:
     #      self.log(f" Station {self.stations[i]['self.number']}: window {self.stations[i]['self.window']} window_start: {self.stations[i]['self.window_start']} running time: {self.stations[i]['self.station_running_time'] } ")

     # for i in self.stations:
     #     if i != '': self.turn_off(i)


  def next_key(self, dict, thekey):
     self.dict_keys = list(dict.keys())
     try:
       return self.dict_keys[self.dict_keys.index(thekey) + 1]
     except IndexError:
       self.log('Item index does not exist')
       return -1

  def convert_seconds(self,n):
      return str(datetime.timedelta(seconds = n))

     # for i,runtime in self.stations.items():  # the station variable assigned e.g. switch.frlawneast
     #     for key in runtime:
     #         # if key != '': self.turn_off(key)
     #         self.log(key)
     #
     # for i,runtime in self.stations.items():  # the station running time variable assigned e.g. 10
     #     for key in runtime:
     #         self.log(runtime[key])




# for key, value in mydic.items() :
#     print (key, value)


# import appdaemon.plugins.hass.hassapi as hass
# import datetime
# #
# class Home_Irrigation(hass.Hass):
#
#   def initialize(self):
#      self.start_time = self.args["START_TIME"]
#      self.start_days = self.args["START_DAYS"].split(",") # split up supplied days list
#      self.dayz = ('mon','tue','wed','thu','fri','sat','sun')  # work out todays date
#      self.precipitation_threshold = self.args["PRECIPITATION_THRESHOLD"] # the rain chance probability after which irrigating will occur
#      self.precipitation_threshold_48 = self.args["PRECIPITATION_THRESHOLD_48"]
#      self.watering_threshold = self.args["WATERING_THRESHOLD"]  # the daily watering point where irrigating will occur
#      self.reset_backet = self.args["RESET_BUCKET"]  # signals to an irrigation instance to rest the bucket
#      self.no_of_schedules = self.args["NO_OF_SCHEDULES"]
#      self.valve_lead_time = self.args["VALVE_LEAD_TIME"]
#      self.station1 = self.args["STATION_1"]
#      self.station2 = self.args["STATION_2"]
#      self.station3 = self.args["STATION_3"]
#      self.station4 = self.args["STATION_4"]
#      self.station5 = self.args["STATION_5"]
#      self.station6 = self.args["STATION_6"]
#      self.station7 = self.args["STATION_7"]
#
#      # self.station1_weight = self.args["STATION_1_WEIGHT"]
#      # self.station2_weight = self.args["STATION_2_WEIGHT"]
#      # self.station3_weight = self.args["STATION_3_WEIGHT"]
#      # self.station4_weight = self.args["STATION_4_WEIGHT"]
#      # self.station5_weight = self.args["STATION_5_WEIGHT"]
#      # self.station6_weight = self.args["STATION_6_WEIGHT"]
#      # self.station7_weight = self.args["STATION_7_WEIGHT"]
#
#      self.master_valve_lead_time = self.args["MASTER_VALVE_LEAD_TIME"]  # must keep
#
#      # self.window1 = self.args["STATION_1_WINDOW"] + self.args["VALVE_LEAD_TIME"]# window of the WaterMe irrigation cycle
#      # self.window2 = self.args["STATION_2_WINDOW"] + self.args["VALVE_LEAD_TIME"]
#      # self.window3 = self.args["STATION_3_WINDOW"] + self.args["VALVE_LEAD_TIME"]
#      # self.window4 = self.args["STATION_4_WINDOW"] + self.args["VALVE_LEAD_TIME"]
#      # self.window5 = self.args["STATION_5_WINDOW"] + self.args["VALVE_LEAD_TIME"]
#      # self.window6 = self.args["STATION_6_WINDOW"] + self.args["VALVE_LEAD_TIME"]
#
#      self.stations = {
#                 self.station1:{'self.number': '1','self.station_weight':self.args["STATION_1_WEIGHT"],'self.window':str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"]),
#                                 'self.station_running_time': ''
#                                 },
#                 self.station2:{'self.number': '2','self.station_weight':self.args["STATION_2_WEIGHT"],'self.window': str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"] + self.args["STATION_1_WINDOW"]),
#                                 'self.station_running_time': ''
#                                 },
#                 self.station3:{'self.number': '3','self.station_weight':self.args["STATION_3_WEIGHT"],'self.window': str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"] + self.args["STATION_1_WINDOW"] + self.args["STATION_2_WINDOW"]),
#                                 'self.station_running_time': ''
#                                 },
#                 self.station4:{'self.number': '4','self.station_weight':self.args["STATION_4_WEIGHT"],'self.window': str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"] + self.args["STATION_1_WINDOW"] + self.args["STATION_2_WINDOW"] + self.args["STATION_3_WINDOW"]),
#                                 'self.station_running_time': ''
#                                 },
#                 self.station5:{'self.number': '5','self.station_weight':self.args["STATION_5_WEIGHT"],'self.window': str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"] + self.args["STATION_1_WINDOW"] + self.args["STATION_2_WINDOW"] + self.args["STATION_3_WINDOW"] + self.args["STATION_4_WINDOW"]),
#                                 'self.station_running_time': ''
#                                 },
#                 self.station6:{'self.number': '6','self.station_weight':self.args["STATION_6_WEIGHT"],'self.window': str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"] + self.args["STATION_1_WINDOW"] + self.args["STATION_2_WINDOW"] + self.args["STATION_3_WINDOW"] + self.args["STATION_4_WINDOW"] + self.args["STATION_5_WINDOW"]),
#                                 'self.station_running_time': ''
#                                 },
#                 self.station7:{'self.number': '7','self.station_weight':self.args["STATION_7_WEIGHT"],'self.window': str(self.args["VALVE_LEAD_TIME"] + self.args["MASTER_VALVE_LEAD_TIME"] + self.args["STATION_1_WINDOW"] + self.args["STATION_2_WINDOW"] + self.args["STATION_3_WINDOW"] + self.args["STATION_4_WINDOW"] + self.args["STATION_5_WINDOW"] + self.args["STATION_6_WINDOW"]  ),
#                                 'self.station_running_time': ''
#                                 }
#                  }
#
#      self.run_daily(self.main_routine, self.start_time)
#      # self.run_in(self.main_routine, 0)
#
#   def main_routine(self, *args):
#      if self.dayz[datetime.datetime.today().weekday()] in self.start_days:
#          # self.log(f"Yes, found {self.dayz[datetime.datetime.today().weekday()]} in List: {self.start_days}")
#
#          # if API is down then use base calculation
#          if self.render_template("{{states('sensor.high_temperature_today') | int}}") == 0:
#              self.running_time = self.render_template("{{states('sensor.smart_irrigation_base_schedule_index') | int}}")
#              self.log("WU API is down, using Base Calculation")
#          else:
#              self.running_time = self.render_template("{{states('sensor.smart_irrigation_daily_adjusted_run_time') | int}}")
#
#          self.chance_of_precipitation = self.render_template("{{states('sensor.precip_chance') | int}}")
#          self.chance_of_precipitation_48hrs = self.render_template("{{states('sensor.wupws_precip_chance_2d') | int}}")
#          self.precipitation = self.render_template("{{states('sensor.wupws_preciptotal') | int}}")
#          self.hourly_adjusted_running_time = int(self.get_state('sensor.smart_irrigation_hourly_adjusted_run_time'))
#
#          # for testing
#          self.hourly_adjusted_running_time = 500
#          self.running_time = 400
#          self.precipitation = 0
#
#          self.log(f"Daily is: {self.running_time} seconds. Hourly is: {self.hourly_adjusted_running_time} seconds. Probability of Rain: {self.chance_of_precipitation}%. Probability of Rain 24hrs: {self.chance_of_precipitation_48hrs}%. Watering Threshold: {self.watering_threshold}sec. Precipitation: {self.precipitation}mm. ")
#
#          if self.hourly_adjusted_running_time > 0 and self.running_time > self.watering_threshold and self.chance_of_precipitation <= self.precipitation_threshold and self.chance_of_precipitation_48hrs <= self.precipitation_threshold_48 and self.precipitation == 0:
#
#              if self.station1 != '':  # If not Garden Run then add to cumulative garden run time
#                  self.cumulative_total = round(self.hourly_adjusted_running_time / self.no_of_schedules + self.render_template("{{states('input_number.garden_watering_time') | int}}"),0) #store run time for gardens
#                  self.set_value("input_number.garden_watering_time",self.cumulative_total) # store persistently
#                  self.log(f"Cumulative Garden Run Time: {self.cumulative_total}secs")
#              else:
#                  self.set_value("input_number.garden_watering_time", 0)  # reset cumulative garden running time
#
#              self.running_time = self.running_time / self.no_of_schedules
#              self.garden_running_time = self.render_template("{{states('input_number.garden_watering_time') | int}}")
#
#
#              self.log(f"Starting Irrigation. ")
#              for i in self.stations:
#                  if i != '':
#                      self.stations[i]['self.station_running_time'] = self.running_time*self.stations[i]['self.station_weight']
#                      # self.log(f" Run Time is after weighting: {self.stations[i]['self.station_running_time']}secs")
#                      # self.log(f" Weight was : {self.stations[i]['self.station_weight']}")
#                      # check if calculated time fits into window
#                      # self.log(i)
#                      # self.the_next_station = self.next_key(self.stations, i)
#                      # if self.the_next_station == '': break
#                      # self.log(f"{self.the_next_station} is the key of next station")
#                      # self.log(f" Window is: {self.stations[self.the_next_station]['self.window']}secs")
#                      # self.log(f" Valve is: {int(self.valve_lead_time)}secs")
#                      # self.log(f" Running Time is: {int(self.stations[i]['self.station_running_time'])}secs")
#                      if int(self.stations[i]['self.station_running_time']) >= int(str(self.stations[i]['self.window']))-int(self.valve_lead_time) :
#                          self.stations[i]['self.station_running_time'] = int(self.stations[i]['self.window'])-int(self.valve_lead_time)
#                          self.log(f"{i} has maxed out")
#                  else: self.stations[i]['self.station_running_time'] = 0.0001
#
#
#              # if self.station2 != '':
#              #     self.station2_running_time = self.running_time*self.station2_weight
#              #     if self.station2_running_time >= (self.window2-self.valve_lead_time):
#              #         self.station2_running_time = self.window2-self.valve_lead_time
#              #         self.log(f"{self.station2} has maxed out")
#              # else: self.station2_running_time = 0.0001
#              #
#              #
#              # if self.station3 != '':
#              #     self.station3_running_time = self.running_time*self.station3_weight
#              #     if self.station3_running_time >= (self.window3-self.valve_lead_time):
#              #         self.station3_running_time = self.window3-self.valve_lead_time
#              #         self.log(f"{self.station3} has maxed out")
#              # else: self.station3_running_time = 0.0001
#              #
#              #
#              # if self.station4 != '':
#              #     self.station4_running_time = self.running_time*self.station4_weight
#              #     if self.station4_running_time >= (self.window4-self.valve_lead_time):
#              #         self.station4_running_time = self.window4-self.valve_lead_time
#              #         self.log(f"{self.station4} has maxed out")
#              # else: self.station4_running_time = 0.0001
#              #
#              #
#              # if self.station5 != '':
#              #     self.station5_running_time = self.garden_running_time*self.station5_weight
#              #     if self.station5_running_time >= (self.window5-self.valve_lead_time):
#              #         self.station5_running_time = self.window5-self.valve_lead_time
#              #         self.log(f"{self.station5} has maxed out")
#              # else: self.station5_running_time = 0.0001
#              #
#              #
#              # if self.station6 != '':
#              #     self.station6_running_time = self.garden_running_time*self.station6_weight
#              #     if self.station6_running_time >= (self.window6-self.valve_lead_time):
#              #         self.station6_running_time = self.window6-self.valve_lead_time
#              #         self.log(f"{self.station6} has maxed out")
#              # else: self.station6_running_time = 0.0001
#              #
#              #
#              # if self.station7 != '':
#              #     self.station7_running_time = self.running_time*self.station7_weight
#              #     if self.station7_running_time >= (self.window7-self.valve_lead_time):
#              #         self.station7_running_time = self.window7-self.valve_lead_time
#              #         self.log(f"{self.station7} has maxed out")
#              # else: self.station7_running_time = 0.0001
#
#              for i in self.stations:
#                  # self.log(i)
#                   # self.the_next_station = self.next_key(self.stations, i)
#                   # if self.the_next_station == '': break
#                  # self.log(self.stations[i]['self.station_running_time'])
#                   self.converted_time = self.convert_seconds(float(self.stations[i]['self.station_running_time']))
#                   self.converted_time = self.converted_time.split('.', 1)[0]
#                   if i != '': self.log(f"Station running times (minutes): Station {self.stations[i]['self.number']}: {self.converted_time}")
#
#              # self.log(f"Station running times (minutes): Station 1: {self.station1_running_time/60:.2f} Station 2: {self.station2_running_time/60:.2f} Station 3: {self.station3_running_time/60:.2f} Station 4: {self.station4_running_time/60:.2f} Station 5: {self.station5_running_time/60:.2f} Station 6: {self.station6_running_time/60:.2f} Station 7: {self.station7_running_time/60:.2f}")
#
#              # update lovelace fields
#              for i in self.stations:
#                   if i != '': self.set_textvalue("input_text." + str(i)[7:] + "_run_duration",self.stations[i]['self.station_running_time'])
#
#              # if self.station1 != '': self.set_textvalue("input_text." + self.station1[7:] + "_run_duration",self.station1_running_time)
#              # if self.station2 != '': self.set_textvalue("input_text." + self.station2[7:] + "_run_duration",self.station2_running_time)
#              # if self.station3 != '': self.set_textvalue("input_text." + self.station3[7:] + "_run_duration",self.station3_running_time)
#              # if self.station4 != '': self.set_textvalue("input_text." + self.station4[7:] + "_run_duration",self.station4_running_time)
#              # if self.station5 != '': self.set_textvalue("input_text." + self.station5[7:] + "_run_duration",self.station5_running_time)
#              # if self.station6 != '': self.set_textvalue("input_text." + self.station6[7:] + "_run_duration",self.station6_running_time)
#              # if self.station7 != '': self.set_textvalue("input_text." + self.station7[7:] + "_run_duration",self.station7_running_time)
#
#              # make sure all valves are off
#              for i in self.stations:
#                  if i != '': self.turn_off(i)
#
#
#              # if self.station1 != '': self.turn_off(self.station1)
#              # if self.station2 != '': self.turn_off(self.station2)
#              # if self.station3 != '': self.turn_off(self.station3)
#              # if self.station4 != '': self.turn_off(self.station4)
#              # if self.station5 != '': self.turn_off(self.station5)
#              # if self.station6 != '': self.turn_off(self.station6)
#              # if self.station7 != '': self.turn_off(self.station7)
#
#
#              # Turn on first station after waiting master_valve_lead_time (window0) seconds
#              self.first_iteration = True
#              for i in self.stations:  # the station variable assigned e.g. switch.frlawneast
#                  if i != '' and float(self.stations[i]['self.station_running_time']) > 0.0001:
#                       if self.first_iteration:
#                           self.running_time = self.master_valve_lead_time
#                       else:
#                           self.running_time = int(self.stations[i]['self.window'])
#                       self.first_iteration = False
#                       self.log(f" Station: {i} will start in {self.running_time} secs")
#                       self.run_in(self.turn_on_station_cb, self.running_time, current_station = i)
#                       self.running_time = round(float(self.stations[i]['self.station_running_time']) + float(self.running_time))
#                       self.log(f" Station: {i} will stop in {self.running_time} secs")
#                       self.run_in(self.turn_off_station_cb, self.running_time, current_station = i)
#                  else: self.stations[i]['self.window'] = 0
#
#              # if self.station1 != '' and self.station1_running_time > 0.0001:
#              #     self.running_time = self.window0
#              #     self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station1)
#              #     self.running_time = self.station1_running_time + self.running_time
#              #     self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station1)
#              # else: self.window1 = 0
#              #  # Turn on second station after waiting master_valve_lead_time + first window seconds
#              # if self.station2 != '' and self.station2_running_time > 0.0001:
#              #     self.running_time = self.window0 + self.window1
#              #     self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station2)
#              #     self.running_time = self.station2_running_time + self.running_time
#              #     self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station2)
#              # else: self.window2 = 0
#              #
#              # if self.station3 != '' and self.station3_running_time > 0.0001:
#              #     self.running_time = self.window0 + self.window1 + self.window2
#              #     self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station3)
#              #     self.running_time = self.station3_running_time + self.running_time
#              #     self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station3)
#              # else: self.window3 = 0
#              #
#              # if self.station4 != ''  and self.station4_running_time > 0.0001:
#              #     self.running_time = self.window0 + self.window1 + self.window2 + self.window3
#              #     self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station4)
#              #     self.running_time = self.station4_running_time + self.running_time
#              #     self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station4)
#              # else: self.window4 = 0
#              #
#              # if self.station5 != '' and self.station5_running_time > 0.0001:
#              #     self.running_time = self.window0 + self.window1 + self.window2 + self.window3 + self.window4
#              #     self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station5)
#              #     self.running_time = self.station5_running_time + self.running_time
#              #     self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station5)
#              # else: self.window5 = 0
#              #
#              # if self.station6 != ''  and self.station6_running_time > 0.0001:
#              #     self.running_time = self.window0 + self.window1 + self.window2 + self.window3 + self.window4 + self.window5
#              #     self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station6)
#              #     self.running_time = self.station6_running_time + self.running_time
#              #     self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station6)
#              #     self.set_value("input_number.garden_watering_time", 0)  # reset cumulative garden running time
#              # else: self.window6 = 0
#              #
#              # if self.station7 != ''  and self.station7_running_time > 0.0001:
#              #     self.running_time = self.window0 + self.window1 + self.window2 + self.window3 + self.window4 + self.window5 + self.window6
#              #     self.run_in(self.turn_on_station_cb, self.running_time, current_station = self.station7)
#              #     self.running_time = self.station7_running_time + self.running_time
#              #     self.run_in(self.turn_off_station_cb, self.running_time, current_station = self.station7)
#              # else: self.window7 = 0
#
#
#              if self.reset_backet:
#                  self.call_service("smart_irrigation/smart_irrigation_reset_bucket", entityid = "sensor.smart_irrigation_bucket")
#                  self.call_service("smart_irrigation/smart_irrigation_disable_force_mode") # in case FORCE mode is on
#                  self.log("Reset complete")
#
#              self.log("Irrigation schedule set")
#
#          else:
#              self.log("Irrigation not needed")
#      else:
#          self.log("Wrong day")
# # Methods
#
#   def turn_on_station_cb(self, kwargs): # run in decorator for run_in
#       self.turn_on_station(kwargs["current_station"])
#   def turn_on_station(self, current_station):
#       if self.get_state(current_station) == 'off':
#           if self.precipitation == 0:
#               self.turn_on(current_station)
#               self.log("Started Station watering: %s Valve is on", current_station)
#               self.set_textvalue("input_text." + current_station[7:] + "_run_date",datetime.datetime.today().strftime("%d/%m"))
#               self.set_textvalue("input_text." + current_station[7:] + "_run_time",datetime.datetime.today().strftime("%H:%M"))
#           else:
#               self.log("%s is not needed as raining already", current_station)
#       else:
#           self.log("%s is already on...could be an error", current_station)
#
#
#   def turn_off_station_cb(self, kwargs): # run in decorator for run_in
#       self.turn_off_station(kwargs["current_station"])
#   def turn_off_station(self, current_station):
#       if self.get_state(current_station) == 'on':
#           self.turn_off(current_station)
#       else:
#           self.log("%s is already off...could be an error or could have rained", current_station)
#       self.log("Stopped Station watering: %s Valve is off", current_station)
#
#   def convert_seconds(self,n):
#       return str(datetime.timedelta(seconds = n))
#
