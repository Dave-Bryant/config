import appdaemon.plugins.hass.hassapi as hass
#import datetime

# import pymysql.cursors
# import sqlite3
# import os
# import json
from datetime import datetime
from datetime import timedelta
from statistics import mean
import pytz

from influxdb import InfluxDBClient
import math
from eto import ETo, datasets
import pandas as pd


# Hellow World App
#
# Args: xxxx
#




def psy_const(atmos_pres):
  """
  Calculate the psychrometric constant.

  This method assumes that the air is saturated with water vapour at the
  minimum daily temperature. This assumption may not hold in arid areas.

  Based on equation 8, page 95 in Allen et al (1998).

  :param atmos_pres: Atmospheric pressure [kPa]. Can be estimated using
      ``atm_pressure()``.
  :return: Psychrometric constant [kPa degC-1].
  :rtype: float
  """
  return 0.000665 * atmos_pres

def svp_from_t(t):
  """
  Estimate saturation vapour pressure (*es*) from air temperature.

  Based on equations 11 and 12 in Allen et al (1998).

  :param t: Temperature [deg C]
  :return: Saturation vapour pressure [kPa]
  :rtype: float
  """
  return 0.6108 * math.exp((17.27 * t) / (t + 237.3))

def delta_svp(t):
  """
  Estimate the slope of the saturation vapour pressure curve at a given
  temperature.

  Based on equation 13 in Allen et al (1998). If using in the Penman-Monteith
  *t* should be the mean air temperature.

  :param t: Air temperature [deg C]. Use mean air temperature for use in
      Penman-Monteith.
  :return: Saturation vapour pressure [kPa degC-1]
  :rtype: float
  """
  tmp = 4098 * (0.6108 * math.exp((17.27 * t) / (t + 237.3)))
  return tmp / math.pow((t + 237.3), 2)

def fao56_penman_monteith(net_rad, t, ws, svp, avp, delta_svp, psy, shf=0.0):
  """
  Estimate reference evapotranspiration (ETo) from a hypothetical
  short grass reference surface using the FAO-56 Penman-Monteith equation.

  Based on equation 6 in Allen et al (1998).

  :param net_rad: Net radiation at crop surface [MJ m-2 day-1]. If
      necessary this can be estimated using ``net_rad()``.
  :param t: Air temperature at 2 m height [deg Kelvin].
  :param ws: Wind speed at 2 m height [m s-1]. If not measured at 2m,
      convert using ``wind_speed_at_2m()``.
  :param svp: Saturation vapour pressure [kPa]. Can be estimated using
      ``svp_from_t()''.
  :param avp: Actual vapour pressure [kPa]. Can be estimated using a range
      of functions with names beginning with 'avp_from'.
  :param delta_svp: Slope of saturation vapour pressure curve [kPa degC-1].
      Can be estimated using ``delta_svp()``.
  :param psy: Psychrometric constant [kPa deg C]. Can be estimatred using
      ``psy_const_of_psychrometer()`` or ``psy_const()``.
  :param shf: Soil heat flux (G) [MJ m-2 day-1] (default is 0.0, which is
      reasonable for a daily or 10-day time steps). For monthly time steps
      *shf* can be estimated using ``monthly_soil_heat_flux()`` or
      ``monthly_soil_heat_flux2()``.
  :return: Reference evapotranspiration (ETo) from a hypothetical
      grass reference surface [mm day-1].
  :rtype: float
  """
  a1 = (0.408 * (net_rad - shf) * delta_svp /
        (delta_svp + (psy * (1 + 0.34 * ws))))
  a2 = (900 * ws / t * (svp - avp) * psy /
        (delta_svp + (psy * (1 + 0.34 * ws))))
  return a1 + a2


  
class HelloWorld(hass.Hass):
  def initialize(self):
     self.log("Hello from AppDaemon")
     #self.log(self.list_services(namespace="default"))
     #self.irrigation_entity = self.get_entity("sensor.smart_irrigation_garden")
     #self.irrigation_entity.call_service("smart_irrigation/reset_bucket")
     #self.call_service("smart_irrigation/reset_all_buckets") 
     #self.call_service("smart_irrigation/set_bucket", entityid = "sensor.smart_irrigation_garden", data = 2 )
     # self.log("Reset complete")

     #self.run_every(self.main_routine,"now", 15)
     
     self.run_in(self.load_dataframe1, 0)

  def load_dataframe1(self, *args):
      # Connect to History Database
      
      self.conn =InfluxDBClient("10.0.0.55", 8086, "homeassistant", "david", "homeassistant")
      
      self.log("Connection to influxdb was succesfull")

      # Execute the query and return an Arrow table
      self.table = self.conn.query(
            query="SELECT mean(\"value\") FROM \"°C\" WHERE time >= now() - 24h and time <= now() GROUP BY time(5m) fill(null)"
            )

      print("\n#### View Schema information\n")
      print(self.table)
      
      self.run_in(self.main_routine, 0)     
     
  
  def main_routine(self, *args):
     Te = float(self.get_state("sensor.temp"))
     P = float(self.get_state("sensor.baromabs"))
     SR = float(self.get_state("sensor.solarradiation"))
     ET = fao56_penman_monteith(SR, Te, 0, svp_from_t(Te), P, delta_svp(Te), psy_const(P), shf=0.0)
     self.log("ET:", ET, "Temp:", Te, "Press:", P, "Solar Rad:", SR)

     
     et1 = ETo()
    
  