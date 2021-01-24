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
     self.test(argument1 ="viola", match = self.entities.switch.frlawnwest.state)

  def test(self, argument1, match, **kwargs):
      self.station5_running_time = 300
      self.STATION_5 = 'switch.frlawnwest'
      # self.STATION_5 = "input_text." + self.STATION_5[7:] + "_run_date"
      # self.log(self.STATION_5)


      # self.set_textvalue("input_text." + self.STATION_5[7:] + "_run_date",datetime.datetime.today().strftime("%d/%m/%Y"))
      # self.set_textvalue("input_text." + self.STATION_5[7:] + "_run_time",datetime.datetime.today().strftime("%H:%M"))
      # self.set_textvalue("input_text." + self.STATION_5[7:] + "_run_duration",self.station5_running_time/60)
      #
      # self.log("input_text.frlawnwest_run_date is: %s", self.render_template("{{states('input_text.frlawnwest_run_date') }}"))
      # self.log("input_text.frlawnwest_run_time is: %s", self.render_template("{{states('input_text.frlawnwest_run_time') }}"))
      # self.log("input_text.frlawnwest_run_duration is: %s", self.render_template("{{states('input_text.frlawnwest_run_duration') }}"))

      if self.render_template("{{states('sensor.samsung_q80_series_65_media_playback_status') | int}}") == 0:
          self.log("it is %s", self.render_template("{{states('sensor.samsung_q80_series_65_media_playback_status') | int}}"))
      # self.log("input_text.frlawnwest_run_time is: %s", self.render_template("{{states('input_text.frlawnwest_run_time') }}"))
      # self.log("Hello from test function %s and %s", argument1, match)
      
