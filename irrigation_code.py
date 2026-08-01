import datetime
import appdaemon.plugins.hass.hassapi as hass


class Home_Irrigation(hass.Hass):

    def initialize(self):
        self.start_time = self.args["START_TIME"]
        self.start_days = self.args["START_DAYS"].split(",")
        self.dayz = ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')
        self.precipitation_threshold = self.args["PRECIPITATION_THRESHOLD"]
        self.precipitation_threshold_48 = self.args["PRECIPITATION_THRESHOLD_48"]
        self.watering_threshold = self.args["WATERING_THRESHOLD"]
        self.soil_moisture_min = self.args["SOILMOISTUREMIN"]
        self.rain_threshold = self.args["RAINTHRESHOLD"]
        self.garden_run = self.args["GARDEN_RUN"]
        self.no_of_schedules = self.args["NO_OF_SCHEDULES"]        
        self.debug = self.args.get("debug_run", False)
        self._queue_handles = []

        self.run_daily(self.main_routine, self.start_time)
        self.listen_state(self.toggle_handler, "input_boolean.auto_irrigation_switch")
        self.run_in(self._init_entities, 10)        

        if self.debug:
            self.log("DEBUG: debug_run=true running irrigation logic immediately")
            self.run_in(self.main_routine, 2)

    def terminate(self):
        for handle in self._queue_handles:
            self.cancel_timer(handle)
        self._queue_handles.clear()

    def toggle_handler(self, entity, attribute, old, new, kwargs):
        self.log(f"{entity} changed from {old} to {new}")

    def _build_stations(self):
        args = self.args
        stations = {}
        for n in range(1, 8):
            key = args[f"STATION_{n}"]
            stations[key] = {
                'number': str(n),
                'station_weight': args[f"STATION_{n}_WEIGHT"],
                'station_running_time': 0.0,
            }
            if self.debug:
                self.log(f"DEBUG _build_stations: station {n} key={key} weight={args[f'STATION_{n}_WEIGHT']}")
        return stations

    def _load_sensors(self):
        if (self.get_state("sensor.high_temperature_today") == 0
                or self.get_state("sensor.precip_chance_today") == "unknown"):
            self.running_time = 0.0
            self.chance_of_precipitation = 100.0
            self.chance_of_precipitation_48hrs = 100.0
            self.precipitation = 10.0
            self.log("WU API is down — variables set to safe defaults to prevent irrigation")
        else:
            self.running_time = self.to_float(self.get_state('input_number.lawn_watering_time')) * 60
            self.chance_of_precipitation = self.to_float(self.get_state('sensor.precip_chance_today'))
            self.chance_of_precipitation_48hrs = self.to_float(self.get_state('sensor.precip_chance_tomorrow'))
            self.precipitation = self.to_float(self.get_state('sensor.ws2900c_v2_01_10_daily_rain'))

        s1 = self.to_float(self.get_state('sensor.soil_moisture_1_soil_moisture'))
        s2 = self.to_float(self.get_state('sensor.soil_moisture_2_soil_moisture'))
        s1_ok = s1 > 0.0
        s2_ok = s2 > 0.0

        if s1_ok and s2_ok:
            self.soil_moisture = min(s1, s2)
            self.log(f"Soil moisture: sensor1={s1}% sensor2={s2}% using min={self.soil_moisture}%")
        elif s1_ok:
            self.soil_moisture = s1
            self.log(f"Soil moisture: sensor2 failed, using sensor1={s1}%")
            self.call_service(
                "notify/mobile_app_david_bryants_iphone",
                message='Soil Moisture sensor 2 issue — check batteries or device'
            )
        elif s2_ok:
            self.soil_moisture = s2
            self.log(f"Soil moisture: sensor1 failed, using sensor2={s2}%")
            self.call_service(
                "notify/mobile_app_david_bryants_iphone",
                message='Soil Moisture sensor 1 issue — check batteries or device'
            )
        else:
            self.soil_moisture = 1.0
            self.log("Soil moisture: both sensors failed — defaulting to 1%")
            self.call_service(
                "notify/mobile_app_david_bryants_iphone",
                message='Both Soil Moisture sensors failed — check batteries or devices'
            )

    def main_routine(self, *args):
        today = self.dayz[datetime.datetime.today().weekday()]
        if today not in self.start_days:
            self.log("Wrong day")
            return

        self.stations = self._build_stations()
        self._load_sensors()

        self.log(
            f"Daily run time: {self.running_time:.0f}s (threshold: {self.watering_threshold}s) : "
            f"{'OK' if self.running_time > self.watering_threshold else 'SKIP'}. "
            f"Rain today: {self.chance_of_precipitation}% (threshold: {self.precipitation_threshold}) : "
            f"{'OK' if self.chance_of_precipitation <= self.precipitation_threshold else 'SKIP'}. "
            f"Rain 48h: {self.chance_of_precipitation_48hrs}% (threshold: {self.precipitation_threshold_48}) : "
            f"{'OK' if self.chance_of_precipitation_48hrs <= self.precipitation_threshold_48 else 'SKIP'}. "
            f"Precipitation: {self.precipitation}mm (threshold: {self.rain_threshold}) : "
            f"{'OK' if self.precipitation <= self.rain_threshold else 'SKIP'}. "
            f"Soil moisture: {self.soil_moisture}% (min: {self.soil_moisture_min}) : "
            f"{'OK' if self.soil_moisture <= self.soil_moisture_min else 'SKIP'}. "
            f"Garden watering time: {self.get_state('input_number.garden_watering_time')} min. "
            f"All conditions must be OK to irrigate."
        )

        if self.running_time <= self.watering_threshold:
            status = "No moisture lost yesterday" if int(self.running_time) == 0 else "Irrigation run time too small"
            self.select_option("input_select.irrigation_status", status)
        if self.chance_of_precipitation > self.precipitation_threshold:
            self.select_option("input_select.irrigation_status", "Rain is coming")
        if self.chance_of_precipitation_48hrs > self.precipitation_threshold_48:
            self.select_option("input_select.irrigation_status", "Rain is coming")
        if self.precipitation > self.rain_threshold:
            self.select_option("input_select.irrigation_status", "It has rained")
        if self.soil_moisture > self.soil_moisture_min:
            self.select_option("input_select.irrigation_status", "Soil Moisture too high")

        should_irrigate = (
            self.running_time > self.watering_threshold
            and self.chance_of_precipitation <= self.precipitation_threshold
            and self.chance_of_precipitation_48hrs <= self.precipitation_threshold_48
            and self.precipitation <= self.rain_threshold
            and self.soil_moisture <= self.soil_moisture_min
        )

        if self.debug:
            self.log(f"DEBUG should_irrigate={should_irrigate} garden_run={self.garden_run}")

        if should_irrigate:
            self._run_irrigation()
        else:
            self.log("Irrigation not needed")

    def _run_irrigation(self):
        if self.debug:
            for handle in self._queue_handles:
                self.cancel_timer(handle)
            self._queue_handles.clear()

        base_run_time = self.running_time / self.no_of_schedules
        garden_running_time = self.to_float(self.get_state('input_number.garden_watering_time')) * 60

        if self.debug:
            self.log(f"DEBUG _run_irrigation: base_run_time={base_run_time:.0f}s garden_running_time={garden_running_time:.0f}s")

        if self.garden_run:
            for key, data in self.stations.items():
                if not key.startswith('noswitch'):
                    self._assign_station_time(key, data, garden_running_time)
            self.set_value("input_number.garden_watering_time", 0)
            self.log("Reset cumulative garden run time to zero")
        else:
            cumulative_secs = int(base_run_time + garden_running_time)
            cumulative_mins = int(cumulative_secs / 60)
            self.set_value("input_number.garden_watering_time", cumulative_mins)
            self.log(f"Cumulative garden run time: {cumulative_mins} mins")
            for key, data in self.stations.items():
                if not key.startswith('noswitch'):
                    self._assign_station_time(key, data, base_run_time)

        for key, data in self.stations.items():
            if not key.startswith('noswitch'):
                duration = self.convert_seconds(data['station_running_time']).split('.')[0]
                self.log(f"Station {data['number']} ({key}) run time: {duration}")

        if self.precipitation > 0:
            self.log("Skipping irrigation — it is currently raining")
            return

        for key, data in self.stations.items():
            if not key.startswith('noswitch'):
                self.set_textvalue(f"input_text.{key[7:]}_run_duration", str(round(data['station_running_time'])))        

        switch_state = self.get_state("input_boolean.auto_irrigation_switch")
        if switch_state is None:
            self.log("WARNING: input_boolean.auto_irrigation_switch not found")
            return
        if switch_state != 'on':
            self.log("Auto irrigation switch is off — not starting")
            return

        now = datetime.datetime.today()
        delay = 0
        for key, data in self.stations.items():
            run_time = data['station_running_time']
            if not key.startswith('noswitch') and run_time > 0.001:
                if self.debug:
                    self.log(f"DEBUG queuing {key} at +{delay}s for {round(run_time)}s")
                handle = self.run_in(
                    self._queue_station_cb, delay,
                    current_station=key,
                    run_seconds=round(run_time),
                    now=now
                )
                self._queue_handles.append(handle)
                delay += 2

        self.log("Irrigation schedule set")
        self.select_option("input_select.irrigation_status", "Normal")

    # --- Callbacks ---

    def _init_entities(self, kwargs):
        for key in self._build_stations():
            if not key.startswith('noswitch'):
                suffix = key[7:]
                for entity in (
                    f"input_text.{suffix}_run_duration",
                    f"input_text.{suffix}_run_date",
                    f"input_text.{suffix}_run_time",
                ):
                    state = self.get_state(entity)
                    #self.log(f"Init entity: {entity} = {state!r}")
                    if state in (None, "unknown", "unavailable", ""):
                        self.set_textvalue(entity, "----")

    def _queue_station_cb(self, kwargs):
        key = kwargs["current_station"]
        run_seconds = kwargs["run_seconds"]
        now = kwargs["now"]
        self.call_service("opensprinkler/run", entity_id=key, run_seconds=run_seconds)
        self.set_textvalue(f"input_text.{key[7:]}_run_date", now.strftime("%d/%m"))
        self.set_textvalue(f"input_text.{key[7:]}_run_time", now.strftime("%H:%M"))
        self.log(f"Queued {key} for {run_seconds}s")

    # --- Helpers ---

    def _assign_station_time(self, key, data, base_time):
        if self.debug:
            self.log(f"DEBUG station {data['number']} ({key}): base={base_time:.0f}s")
        weighted = base_time * data['station_weight']
        data['station_running_time'] = weighted
        if self.debug:
            self.log(f"DEBUG station {data['number']} ({key}): weighted={weighted:.0f}s")



    def convert_seconds(self, n):
        return str(datetime.timedelta(seconds=n))

    def to_float(self, data):
        try:
            return float(data)
        except (ValueError, TypeError):
            return 0.0

