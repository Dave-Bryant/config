import appdaemon.plugins.hass.hassapi as hass
from influxdb import InfluxDBClient
from eto import ETo, datasets
import pandas as pd
import numpy as np

 
class ET_Calculation(hass.Hass):

    def initialize(self):
        self.log("Start ET Calculation")
        self.debug = False
        self.debug_extra = False

        self.ET = self.args["EVAPOTRANSPIRATION"]
        self.run_time = self.args["IRRIGATIONRUNTIME"]
            
        self.z_msl = 430 # elevation these are for ETo
        self.lat = -35.282001
        self.lon = 149.128998
        self.TZ_lon = 143
        self.freq = 'H'

        self.start_time = self.args["ETCALCSTARTTIME"]
        self.area = self.args["AREA"]
        self.sprinkler_number = self.args["SPRINKLERNUMBER"]
        self.sprinkler_half_circle_rate = self.args["SPRINKLERHALFCIRCLERATE"]
        self.max_run_time = self.args["SPRINKLERMAXRUNTIME"]

        #self.run_daily(self.main_routine, self.start_time)  #####
        self.run_in(self.main_routine, 0)

    def main_routine(self, *args):   
        self.ET = self.Calculate_ET_for_the_day(self.ET, self.z_msl,self.lat,self.lon,self.TZ_lon,self.freq)        
        self.log(f"ET is: {self.ET}") 
        self.set_value("input_number.daily_et", self.ET)       
        self.run_time = self.Calculate_run_time(self.ET,self.area,self.sprinkler_number,self.sprinkler_half_circle_rate,self.max_run_time)
        self.log(f"run time is: {self.run_time/60} mins")
        self.set_value("input_number.lawn_watering_time", int(self.run_time))   

    # METHODS
  
    def Calculate_ET_for_the_day(self,*kwarg):
    # Connect to History Database
        try:
            self.conn = InfluxDBClient("10.0.0.55", 8086, "homeassistant", "david", "homeassistant")   
            self.log("Connection to influxdb was succesfull")  

            # Execute the query and return a table
            self.table = self.conn.query(
                    query="SELECT mean(\"value\") FROM \"°C\" WHERE (\"entity_id\"::tag = 'temp') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)"
                    )   
            self.dat = self.table.raw['series'][0]['values']   
            self.df1 = pd.DataFrame(self.dat, columns=[ 'time', 'T_mean'])  
                    
            if self.debug: self.log(self.df1.head())

            self.table = self.conn.query(
                    query="SELECT mean(\"value\") FROM \"%\" WHERE (\"entity_id\"::tag = 'humidity') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)"
                    )   
            self.dat = self.table.raw['series'][0]['values']   
            self.df2 = pd.DataFrame(self.dat, columns=[ 'time', 'RH_mean'])
            
            if self.debug:self.log(self.df2.head())

            self.table = self.conn.query(
                    query="SELECT mean(\"value\") FROM \"°C\" WHERE (\"entity_id\"::tag = 'low_temperature_per_hour') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)"
                    ) 
            
            self.dat = self.table.raw['series'][0]['values']   
            self.df3 = pd.DataFrame(self.dat, columns=[ 'time', 'T_min'])
            
            if self.debug:self.log(self.df3.head())

            self.table = self.conn.query(
                    query="SELECT mean(\"value\") FROM \"°C\" WHERE (\"entity_id\"::tag = 'high_temperature_per_hour') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)"
                    )   
            self.dat = self.table.raw['series'][0]['values']   
            self.df4 = pd.DataFrame(self.dat, columns=[ 'time', 'T_max'])
            
            if self.debug:self.log(self.df4.head())

            self.table = self.conn.query(
                    query="SELECT mean(\"value\") FROM  \"hPa\" WHERE (\"entity_id\"::tag = 'baromabs') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)"
                    )   
            self.dat = self.table.raw['series'][0]['values']   
            self.df5 = pd.DataFrame(self.dat, columns=[ 'time', 'P'])
            self.df5['P'] = self.df5['P']/10 # converting HPa to kPa

            if self.debug:self.log(self.df5)

            self.table = self.conn.query(
                    query="SELECT mean(\"value\") FROM \"°C\" WHERE (\"entity_id\"::tag = 'dewpoint') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)"
                    )   
            self.dat = self.table.raw['series'][0]['values']   
            self.df6 = pd.DataFrame(self.dat, columns=[ 'time', 'T_dew'])
            
            if self.debug:self.log(self.df6)

            self.table = self.conn.query(
                    query="SELECT mean(\"value\") FROM \"km/h\" WHERE (\"entity_id\"::tag = 'windspeed') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)"
                    )   
            self.dat = self.table.raw['series'][0]['values']   
            self.df7 = pd.DataFrame(self.dat, columns=[ 'time', 'U_z'])
            
            if self.debug:self.log(self.df7)

            self.df1 = pd.merge(self.df1, self.df2, on='time', how='outer')
            self.df1 = pd.merge(self.df1, self.df3, on='time', how='outer')
            self.df1 = pd.merge(self.df1, self.df4, on='time', how='outer')
            self.df1 = pd.merge(self.df1, self.df5, on='time', how='outer')
            self.df1 = pd.merge(self.df1, self.df6, on='time', how='outer')
            self.df1 = pd.merge(self.df1, self.df7, on='time', how='outer')

            self.df1.time = pd.to_datetime(self.df1.time)
            self.df1.set_index('time', inplace=True)

            if self.debug_extra:self.log(self.df1)

            self.et1 = ETo()
            
            self.et1.param_est(self.df1, self.freq, self.z_msl, self.lat, self.lon, self.TZ_lon)
                       
            if self.debug:self.log(self.et1.ts_param)
            
            self.eto1 = self.et1.eto_fao(interp='linear',maxgap=4)
            self.ET = self.eto1['ETo_FAO_interp_mm'].sum()
            self.log("ET sucessfully calculated")

            if self.debug_extra:self.log(self.eto1)      

        except: 
            self.log("Insufficient data, setting ET to 2")
            self.ET = 2
        finally:
            return self.ET

    def Calculate_run_time(self,*kwarg):
        self.throughput = self.sprinkler_number * self.sprinkler_half_circle_rate #m3/hr      
        self.precipitation_rate = self.throughput * 1000 / self.area # mm/hr 
        self.run_time = self.ET/self.precipitation_rate*3600  #seconds 
        if self.run_time > self.max_run_time: 
                self.run_time = 1800 
                self.log('Maximum run time set')
        return self.run_time
    


    









