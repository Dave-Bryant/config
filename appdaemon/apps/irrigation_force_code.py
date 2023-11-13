import json
import os
import sqlite3
from datetime import datetime, timedelta
from statistics import mean

import appdaemon.plugins.hass.hassapi as hass           # this needs to be worked on after a history of ET has built up.
import pymysql.cursors
#
# Home Irrigation Force
#
#
class Home_Irrigation_Force(hass.Hass):
    def initialize(self):
        self.log("Starting Home Irrigation Force")
        self.months_active = self.args["MONTHS_ACTIVE"].split(
            ","
        )  # need to finish this
        if datetime.today().strftime("%b") in self.months_active:
            self.log("Force monitoring activated as it is summer")
            self.run_daily(self.monitor_history_of_bucket, "sunset")
        self.run_in(self.monitor_history_of_bucket, 0)  # for debugging
        self.listen_state(
            self.schedule_the_force, "input_boolean.force_irrigation", new="on"
        )

    def schedule_the_force(self, entity, attribute, old, new, kwargs):
        self.log("FORCE started")
        self.run_in(self.turn_it_off, 3)
        self.call_service("smart_irrigation/smart_irrigation_enable_force_mode")
        self.log("FORCE completed ie force set")

    def turn_it_off(self, kwargs):
        self.turn_off("input_boolean.force_irrigation")

    def monitor_history_of_bucket(self, kwargs):
        # initialise variables
        self.average_evapo = '-2.5'
        self.no_of_days = self.args["NO_OF_DAYS"]  # look back N x days
        self.factor = self.args["FACTOR"]  # increase baseline by a factor

        # Connect to History Database
        self.conn = pymysql.connect(
            host="core-mariadb",
            user="homeassistant",
            password="davidcolin23031955",
            db="homeassistant",
            charset="utf8",
        )
        self.log("Connection to MariaDB was succesfull")
        # Load all the historical records
        self.query = f'SELECT state, last_changed FROM states WHERE entity_id = "input_number.daily_et" \
           AND created > DATE_ADD(DATE_ADD(UTC_TIMESTAMP(),INTERVAL -{self.no_of_days} DAY), INTERVAL 1 MINUTE)'
        with self.conn.cursor() as self.cursor:
            self.cursor.execute(self.query)
            self.result = self.cursor.fetchall()
        self.log(self.result)  # for debugging
        self.result = list(self.result)  # convert to list for operations
        for i in range(len(self.result)):  # change list of tuples to list of lists
            self.result[i] = list(self.result[i])

        # need to remove the unknown records and records that didnt change at midnight into new list
        self.newresult = []
        for i in range(len(self.result)):
            if str(self.result[i][1])[11:-7] == "12:00:00":
                self.newresult.append(self.result[i])
        self.result = self.newresult
        self.log(self.result)  # for debugging

        for i in range(len(self.result)):
            self.result[i] = float(self.result[i][0])  # strip off time

        if self.result == []: # when the irrigation system hasnt operated for the period
            self.log(
                f"Force mode will not be triggered as there has been no evapotranspiration ie shitloads of rain...may need a FORCE from you to restart."
            )
        else:
            self.log(
                f"The bucket levels for the last {self.no_of_days} days are: {self.result}"
            )

            self.diff_list = []  # calculate differences between daily bucket levels
            for i in range(1, len(self.result)):
                self.diff_list.append(self.result[i] - self.result[i - 1])

            self.average_evapo = self.average_evapo[1:-1].split(
                ","
            )  # convert string to list
            for i in range(len(self.average_evapo)):
                self.average_evapo[i] = float(self.average_evapo[i])
            self.curr_evapo = (
                self.average_evapo[int(datetime.now().strftime("%m")) - 1] * self.factor
            )
            self.log(self.result,abs(mean(self.diff_list)) ,self.curr_evapo)  # for debugging
            if (
                min(self.result) > 0
                and abs(mean(self.diff_list)) > self.curr_evapo
                and self.result[len(self.result) - 1] > self.curr_evapo
            ):
                self.log(
                    f"Force mode will be triggered as there has been no irrigation for {self.no_of_days} days, the average bucket reduction of {abs(mean(self.diff_list))} is greater than the baseline of {self.curr_evapo} (i.e. hotter than average days) and the bucket of {self.result[len(self.result)-1]} is greater than the expected baseline evaporation of {self.curr_evapo} in the next 24 hours."
                )
                self.set_value("input_number.daily_et", 3)
            else:
                self.log(
                    f"Force mode not triggered as 1) there has been irrigation within the last {self.no_of_days} days or 2) the average bucket reduction of {abs(mean(self.diff_list))} is less than the baseline of {self.curr_evapo} (i.e. colder than average days) or 3) the bucket of {self.result[len(self.result)-1]} is less than the expected baseline evaporation of {self.curr_evapo} in the next 24 hours."
                )
