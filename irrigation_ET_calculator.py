import appdaemon.plugins.hass.hassapi as hass
from influxdb import InfluxDBClient
from eto import ETo
import pandas as pd
import numpy as np


class ET_Calculation(hass.Hass):

    def initialize(self):
        self.log("Start ET Calculation...")
        self.debug = False
        self.debug_extra = False
        self.run_without_update = False   ###### FOR TESTING

        self.ET = self.convert_to_float_or_zero(self.get_state(self.args["EVAPOTRANSPIRATION"]))
        self.ET_calc = self.convert_to_float_or_zero(self.get_state(self.args["EVAPOTRANSPIRATIONCALC"]))
        self.run_time = self.convert_to_float_or_zero(self.get_state(self.args["IRRIGATIONRUNTIME"])) * 60
        self.rain_tracked = self.convert_to_float_or_zero(self.get_state(self.args["DAILYRAINEVENT"]))

        self.z_msl = 430
        self.lat = -35.282001
        self.lon = 149.128998
        self.TZ_lon = 143
        self.freq = 'H'

        self.start_time = self.args["ETCALCSTARTTIME"]
        self.area = self.args["AREA"]
        self.sprinkler_number = self.args["SPRINKLERNUMBER"]
        self.sprinkler_half_circle_rate = self.args["SPRINKLERHALFCIRCLERATE"]
        self.max_run_time = self.args["SPRINKLERMAXRUNTIME"]

        self.daily_rain = self.convert_to_float_or_zero(self.get_state(self.args["DAILYRAIN"]))
        self.event_rain = self.convert_to_float_or_zero(self.get_state(self.args["EVENTRAIN"]))
        self.max_bucket_size = self.args["MAXBUCKETSIZE"]

        # InfluxDB connection
        self.influxdb_host = self.args.get("INFLUXDB_HOST", "10.0.0.55")
        self.influxdb_port = self.args.get("INFLUXDB_PORT", 8086)
        self.influxdb_user = self.args.get("INFLUXDB_USER", "homeassistant")
        self.influxdb_password = self.args["INFLUXDB_PASSWORD"]
        self.influxdb_database = self.args.get("INFLUXDB_DATABASE", "homeassistant")

        # InfluxDB entity_id tags for weather station sensors
        self.tag_temperature = self.args["TAG_TEMPERATURE"]
        self.tag_humidity = self.args["TAG_HUMIDITY"]
        self.tag_pressure = self.args["TAG_PRESSURE"]
        self.tag_dewpoint = self.args["TAG_DEWPOINT"]
        self.tag_windspeed = self.args["TAG_WINDSPEED"]
        self.tag_solarradiation = self.args["TAG_SOLARRADIATION"]

        self.notify_target = self.args.get("NOTIFYTARGET", "mobile_app_david_bryants_iphone")

        self.PASS = 0

        if not self.run_without_update: self.run_daily(self.main_routine, self.start_time)
        if self.run_without_update: self.run_in(self.main_routine, 0)

    def main_routine(self, *args):
        self.PASS = self.PASS + 1
        self.ET, self.PASS = self.Calculate_ET_for_the_day(self.ET, self.z_msl, self.lat, self.lon, self.TZ_lon, self.freq, self.PASS)
        self.log(f"ET is: {self.ET:0.2f}")
        self.set_value("input_number.daily_et", self.ET)
        self.run_time = self.Calculate_run_time(self.ET, self.area, self.sprinkler_number, self.sprinkler_half_circle_rate, self.max_run_time)
        self.log(f"run time is: {self.run_time/60:0.2f} mins")
        self.set_value("input_number.lawn_watering_time", int(self.run_time / 60))
        if self.PASS >= 2: self.run_in(self.main_routine, 1200)

    # METHODS.

    def query_influx(self, query, label):
        self.log(f"Querying: {label}")
        result = self.conn.query(query=query)
        series = result.raw.get('series')
        if not series or not series[0].get('values'):
            raise ValueError(f"No InfluxDB data for: {label}")
        return series[0]['values']

    def Calculate_ET_for_the_day(self, *kwarg):
        try:
            self.conn = InfluxDBClient(
                self.influxdb_host, self.influxdb_port,
                self.influxdb_user, self.influxdb_password,
                self.influxdb_database)
            self.log("Connection to influxdb was succesfull..")

            t = self.tag_temperature
            h = self.tag_humidity
            p = self.tag_pressure
            d = self.tag_dewpoint
            w = self.tag_windspeed
            s = self.tag_solarradiation

            self.df1 = pd.DataFrame(
                self.query_influx(
                    f"SELECT mean(\"value\") FROM \"°C\" WHERE (\"entity_id\"::tag = '{t}') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)",
                    f"{t} (T_mean)"),
                columns=['time', 'T_mean'])

            self.df2 = pd.DataFrame(
                self.query_influx(
                    f"SELECT mean(\"value\") FROM \"%\" WHERE (\"entity_id\"::tag = '{h}') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)",
                    f"{h} (RH_mean)"),
                columns=['time', 'RH_mean'])

            self.df3 = pd.DataFrame(
                self.query_influx(
                    f"SELECT min(\"value\") FROM \"°C\" WHERE (\"entity_id\"::tag = '{t}') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)",
                    f"{t} (T_min)"),
                columns=['time', 'T_min'])

            self.df4 = pd.DataFrame(
                self.query_influx(
                    f"SELECT max(\"value\") FROM \"°C\" WHERE (\"entity_id\"::tag = '{t}') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)",
                    f"{t} (T_max)"),
                columns=['time', 'T_max'])

            self.df5 = pd.DataFrame(
                self.query_influx(
                    f"SELECT mean(\"value\") FROM \"hPa\" WHERE (\"entity_id\"::tag = '{p}') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)",
                    f"{p} (P)"),
                columns=['time', 'P'])
            self.df5['P'] = self.df5['P'] / 10  # hPa to kPa

            self.df6 = pd.DataFrame(
                self.query_influx(
                    f"SELECT mean(\"value\") FROM \"°C\" WHERE (\"entity_id\"::tag = '{d}') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)",
                    f"{d} (T_dew)"),
                columns=['time', 'T_dew'])

            self.df7 = pd.DataFrame(
                self.query_influx(
                    f"SELECT mean(\"value\") FROM \"km/h\" WHERE (\"entity_id\"::tag = '{w}') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)",
                    f"{w} (U_z)"),
                columns=['time', 'U_z'])

            self.df8 = pd.DataFrame(
                self.query_influx(
                    f"SELECT mean(\"value\") FROM \"W/m²\" WHERE (\"entity_id\"::tag = '{s}') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)",
                    f"{s} (R_s)"),
                columns=['time', 'R_s'])
            self.df8['R_s'] = self.df8['R_s'] * 0.0036  # W/m² to MJ/m²/h

            self.df9 = pd.DataFrame(
                self.query_influx(
                    f"SELECT max(\"value\") FROM \"%\" WHERE (\"entity_id\"::tag = '{h}') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)",
                    f"{h} (RH_max)"),
                columns=['time', 'RH_max'])

            self.df10 = pd.DataFrame(
                self.query_influx(
                    f"SELECT min(\"value\") FROM \"%\" WHERE (\"entity_id\"::tag = '{h}') AND time >= now() - 23h and time <= now() GROUP BY time(1h) fill(null)",
                    f"{h} (RH_min)"),
                columns=['time', 'RH_min'])

            self.df1 = pd.merge(self.df1, self.df2, on='time', how='outer')
            self.df1 = pd.merge(self.df1, self.df3, on='time', how='outer')
            self.df1 = pd.merge(self.df1, self.df4, on='time', how='outer')
            self.df1 = pd.merge(self.df1, self.df5, on='time', how='outer')
            self.df1 = pd.merge(self.df1, self.df6, on='time', how='outer')
            self.df1 = pd.merge(self.df1, self.df7, on='time', how='outer')
            self.df1 = pd.merge(self.df1, self.df8, on='time', how='outer')
            self.df1 = pd.merge(self.df1, self.df9, on='time', how='outer')
            self.df1 = pd.merge(self.df1, self.df10, on='time', how='outer')

            # Strip UTC timezone so index operations return UTC-based day/hour values
            self.df1['time'] = pd.to_datetime(self.df1['time'], utc=True).dt.tz_convert(None)
            self.df1.set_index('time', inplace=True)
            self.df1 = self.df1.sort_index()

            valid_hours = self.df1.dropna(how='all').shape[0]
            nan_count = self.df1.isnull().sum().sum()

            if valid_hours < 6:
                self.log(
                    f"WARNING: Only {valid_hours}/24 hours of real sensor data. "
                    f"Skipping ETo calculation — retaining previous ET = {self.ET:.2f}mm",
                    level="WARNING"
                )
                self.notify(
                    f"ET Calculator: Only {valid_hours}/24h of sensor data. "
                    f"Skipping calculation, previous ET ({self.ET:.2f}mm) retained.",
                    title="Irrigation Warning",
                    name=self.notify_target
                )
                self.PASS = 0
                return self.ET, self.PASS

            if valid_hours < 24:
                self.log(
                    f"WARNING: Only {valid_hours}/24 hours have sensor data. "
                    f"Interpolating {nan_count} missing values — ET result may be inaccurate.",
                    level="WARNING"
                )
                self.notify(
                    f"ET Calculator: Only {valid_hours}/24h of sensor data. "
                    f"Result interpolated and may be inaccurate.",
                    title="Irrigation Warning",
                    name=self.notify_target
                )

            self.df1 = self.df1.interpolate(method='time')
            self.df1 = self.df1.bfill().ffill()

            self.log(f"DataFrame ready, shape: {self.df1.shape}, valid hours: {valid_hours}/24")

            if self.debug_extra: self.log(self.df1)

            # ETo v2 API: pass dict of numpy arrays with day_of_year and hour explicitly
            day_of_year = self.df1.index.dayofyear.to_numpy()
            hour = self.df1.index.hour.to_numpy()

            data = {
                'T_mean':  self.df1['T_mean'].to_numpy(),
                'T_min':   self.df1['T_min'].to_numpy(),
                'T_max':   self.df1['T_max'].to_numpy(),
                'RH_mean': self.df1['RH_mean'].to_numpy(),
                'RH_min':  self.df1['RH_min'].to_numpy(),
                'RH_max':  self.df1['RH_max'].to_numpy(),
                'P':       self.df1['P'].to_numpy(),
                'U_z':     self.df1['U_z'].to_numpy() / 3.6,   # km/h → m/s
                'R_s':     self.df1['R_s'].to_numpy(),
                'T_dew':   self.df1['T_dew'].to_numpy(),
            }

            self.et1 = ETo()
            self.et1.param_est(
                data=data,
                freq='H',
                z_msl=self.z_msl,
                lat=self.lat,
                lon=self.lon,
                TZ_lon=self.TZ_lon,
                day_of_year=day_of_year,
                hour=hour
            )

            self.log("param_est complete, running eto_fao")

            eto_values = self.et1.eto_fao()
            self.ET_calc = float(np.nansum(eto_values))
            self.set_value("input_number.daily_calc_et", self.ET_calc)
            self.log(f"ET sucessfully calculated as {self.ET_calc:0.2f}")

            # RAIN ROUTINE
            self.rain_tracked = self.convert_to_float_or_zero(self.get_state('input_number.daily_rain_event'))
            self.daily_rain = self.convert_to_float_or_zero(self.get_state(self.args["DAILYRAIN"]))
            self.event_rain = self.convert_to_float_or_zero(self.get_state(self.args["EVENTRAIN"]))
            self.rained = max(self.daily_rain, self.event_rain, self.rain_tracked)
            if self.rained != 0:
                if self.daily_rain == self.rained:
                    self.ET = self.Apply_rain_to_ET(self.daily_rain, self.ET_calc, self.ET, self.max_bucket_size)
                elif self.event_rain == self.rained:
                    self.ET = self.Apply_rain_to_ET(self.event_rain, self.ET_calc, self.ET, self.max_bucket_size)
                else:
                    self.ET = self.Apply_rain_to_ET(self.rain_tracked, self.ET_calc, self.ET, self.max_bucket_size)
            else:
                self.ET = self.ET_calc

            self.PASS = 0

        except Exception as exc:
            self.PASS = self.PASS + 1
            self.ET = 2
            self.log(f"Exception is {exc}, Pass number: {self.PASS}")
        finally:
            return self.ET, self.PASS

    def Apply_rain_to_ET(self, apply_rain, ET_calc, ET, max_bucket_size):
        if apply_rain > max_bucket_size:
            self.log(f'Rain bucket set from {apply_rain:0.2f} to maximum {max_bucket_size:0.2f} mm')
            apply_rain = max_bucket_size

        if apply_rain >= ET_calc:
            ET = 0
            self.log(f'ET set to 0 as Rain bucket {apply_rain:0.2f} exceeds (or equals) ET_calc {ET_calc:0.2f}')
            apply_rain = apply_rain - ET_calc
            self.log(f'Rain bucket decreased by ET_calc and set to {apply_rain:0.2f} mm')
        else:
            ET = ET_calc - apply_rain
            self.log(f'New ET {ET:0.2f} after ET_calc {ET_calc:0.2f} reduced by Rain bucket {(ET_calc-ET):0.2f} amount')
            apply_rain = 0

        if not self.run_without_update: self.set_value("input_number.daily_rain_event", round(apply_rain, 2))
        return ET

    def Calculate_run_time(self, *kwarg):
        self.throughput = self.sprinkler_number * self.sprinkler_half_circle_rate
        self.precipitation_rate = self.throughput * 1000 / self.area
        self.run_time = self.ET / self.precipitation_rate * 3600
        if self.run_time > self.max_run_time:
            self.run_time = 1800
            self.log('Maximum run time set')
        return self.run_time

    def convert_to_float_or_zero(self, data):
        try:
            return float(data)
        except (ValueError, TypeError):
            return 0.0
