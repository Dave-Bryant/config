"""App to plot monthly data from InfluxDB.
Args:
class: InfluxChart
  module: influx_chart
  host: localhost #influxdb host
  user: home_assistant #influxdb user name
  password: 'pwd' #influxdb pwd
  dbname: home_assistant #influxdb db name
  query: "select max(value) from kWh where entity_id = 'energy_generation' and time >= now() - 30d group by time(1d) fill(null) order by time asc;"
  
"""
import appdaemon.plugins.hass.hassapi as hass
from influxdb import InfluxDBClient
import datetime
import matplotlib.pyplot as plt

class InfluxChart(hass.Hass):
    
    def initialize(self):
        self.log("Hello from InfluxChart Data Plot App")
        self.host = self.args.get("host", "localhost")
        port=8086
        self.user = self.args.get("user", "home_assistant")
        self.password = self.args.get("password", None)
        self.dbname = self.args.get("dbname", "home_assistant")
        self.query = self.args.get("query", None)
        #run at midnight
        self.run_daily(self.create_chart, datetime.time(23, 55, 0))
    
    def create_chart(self, kwargs):
        self.log("Querying data: ")
        """Instantiate a connection to the InfluxDB."""
        client =InfluxDBClient(self.host, port, self.user, self.password, self.dbname)
        result = client.query(self.query)
        resultInList = list(result.get_points(measurement='kWh'))
        data = {}
        for p in resultInList:
           d = p['time']
           mt = d.split('-')[1]
           dt = ((d.split('-')[2].split(':')[0])).split('T')[0]
           k = "{}/{}".format(mt,dt)
           data[k] = p['max']
        names = list(data.keys())
        values = list(data.values())
        self.plot_bar_chart(values, names, data)

        
    def plot_bar_chart(self,values, labels, data):
        #set tick label font size
        plt.rc('xtick',labelsize=6)
        plt.rc('ytick',labelsize=6)
        #Plot size
        plt.figure(figsize=(6,3.5))
        h = plt.bar(range(len(labels)), values, label=labels, color='#039BE5')
        plt.subplots_adjust(bottom=0.3)
        ax = plt.gca()
        xticks_pos = [0.5*patch.get_width() + patch.get_xy()[0] for patch in h]
        plt.xlim([-0.5,len(labels)-0.5])
        #hide top and right axis lines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        #plt.tick_params(axis="both", which="both", bottom="on", top="off",
                #labelbottom="on", left="on", right="off", labelleft="on")
        #rotate bottom tick labels
        plt.xticks(xticks_pos, labels,  ha='center', rotation=90, fontsize=6)
        #y axis label
        plt.ylabel('kWh', fontsize=10)
        plt.title('DAILY ELECTRICITY OUTPUT', fontsize=10)
        #plt.savefig('top_words.png', bbox_inches='tight') 
        plt.savefig('/home/anilet/appdaemon/conf/apps/influx_chart/bar.png', bbox_inches='tight') 