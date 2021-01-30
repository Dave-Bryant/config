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

     self.station1 = 'switch.frlawnwest'
     self.station2 =  'switch.frlawneast'
     self.station3 =  'switch.bklawnsouth'
     self.station1_running_time = 10
     self.station2_running_time = 20
     self.station3_running_time = 30

     self.stations = {'self.station1':{self.station1:self.station1_running_time}, 'self.station2':{self.station2:self.station2_running_time},'self.station3':{self.station3:self.station3_running_time}}

     for i in self.stations:  # the station variable e.g. self.station 2
         self.log(i)

     for i,runtime in self.stations.items():  # the station variable assigned e.g. switch.frlawneast
         for key in runtime:
             if key != '': self.turn_off(key)
             self.log(key)

     for i,runtime in self.stations.items():  # the station running time variable assigned e.g. 10
         for key in runtime:
             self.log(runtime[key])




# for key, value in mydic.items() :
#     print (key, value)
