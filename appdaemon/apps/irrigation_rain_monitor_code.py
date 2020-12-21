import appdaemon.plugins.hass.hassapi as hass
import datetime

#
# Home Irrigation rain monitor
#
# Args: Rain Threshold in mm
#

class Home_Irrigation_rain_monitor(hass.Hass):

  def initialize(self):
     self.log("Starting Home Irrigation rain monitor")
     self.precipitation_threshold = self.args["PRECIPITATION_THRESHOLD"]

     runtime = datetime.time(0, 0, 0)
     self.run_hourly(self.main_routine, runtime)
     # self.run_in(self.main_routine, 0)

  def main_routine(self, *args):

      if self.render_template("{{states('sensor.wupws_preciptotal') | int}}") >= self.precipitation_threshold:
           self.set_value("input_number.garden_watering_time", 0)

      Garden_watering_time = self.render_template("{{states('input_number.garden_watering_time') | int}}")
      Precipitation = self.render_template("{{states('sensor.wupws_preciptotal') | int}}")

      self.log(f"Precipitation is: {Precipitation} mms. Garden_watering_time is: {Garden_watering_time} seconds.")
