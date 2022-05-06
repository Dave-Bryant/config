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
     self.precipitation_threshold = float(self.args["PRECIPITATION_THRESHOLD"])

     runtime = datetime.time(0, 0, 0)
     self.run_hourly(self.main_routine, runtime)
     # self.run_in(self.main_routine, 0)

  def main_routine(self, *args):

      if int(str(self.time())[:2]) < 22: # needs to stop while the irrigation program calculates new daily run time
          if isinstance(float(self.get_state("sensor.daily_rain_rate_2")), float):
              if float(self.get_state("sensor.daily_rain_rate_2")) >= self.precipitation_threshold:
                   # Reset Gardening run time
                   Garden_watering_time = float(self.get_state("input_number.garden_watering_time"))
                   Precipitation = float(self.get_state("sensor.daily_rain_rate_2"))
                   if  Garden_watering_time != 0:
                       self.set_value("input_number.garden_watering_time", 0)
                       self.log(f"Garden watering time set to zero. Prec: {Precipitation} mms. Gard time was: {Garden_watering_time} secs")
                   # reset Watering System so daily calaculation is set to zero
                   # self.call_service("smart_irrigation/smart_irrigation_reset_bucket", entityid = "sensor.smart_irrigation_bucket")
                   # self.log("Reset complete")
