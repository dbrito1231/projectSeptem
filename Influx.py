from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS
from nMapper import Mapper
from nSpeed import Speeder


class Influx:
    token = org = bucket = speeder = mapper = ping = None

    def __init__(self, usr_token, usr_org, usr_bucket, ip):
        self.token = usr_token
        self.org = usr_org
        self.bucket = usr_bucket
        self.speeder = Speeder()
        self.mapper = Mapper(ip)

    def get_device_data(self):
        devices = self.mapper.get_det_netstats()
        sequence = []
        for dev in devices.items():
            hostname = dev[1]['hostname']
            ip = dev[1]['ip']
            mac = dev[1]['mac']
            dev_os = dev[1]['os']
            if dev[1]['vendor'] is not None:
                vendor = dev[1]['vendor'].replace(',', '')
            else:
                vendor = dev[1]['vendor']
            try:
                for port in dev[1]['ports']:
                    query = f"devices,ip={ip},host={hostname},mac={mac},os={dev_os},vendor={vendor} port={port}"
                    sequence.append(query)
            except TypeError:
                query = f"devices,ip={ip},host={hostname},mac={mac},os={dev_os},vendor={vendor} port=''"
                sequence.append(query)
        return sequence

    def get_port_data(self):
        ports_used = self.mapper.get_current_used_ports()
        ports_sequence = []
        for port in ports_used:
            query = f"ports port={port}"
            ports_sequence.append(query)
        return ports_sequence

    def get_curr_net_data(self):
        data = self.speeder.run()
        hosts = self.mapper.get_sum_netstats()
        tf = ["speeds",
              f"source={data['source_ip']}",
              f"download={data['download']}, "
              f"upload={data['upload']}",
              f"ping={data['ping']}",
              f"bytes_sent={data['bytes_sent']}",
              f"bytes_received={data['bytes_recv']}",
              f"uphosts={hosts['uphosts']}",
              f"available_ips={hosts['downhosts']}",
              f"total_ips={hosts['totalhosts']}"]
        fields = ",".join(tf[2:])
        query = f"{tf[0]},{tf[1]} {fields}"
        return query


# You can generate an API token from the "API Tokens Tab" in the UI
token = "FwrmDbdUonIgP7BSZESkeY2p-oxR0ntSrS8kxMfMXL5DyeUmGWdklPGbdpCF5gE5o7bWvyxCjlXG8Ru9oM3rAw=="
org = "devenv"
bucket = "test_bucket"

# with InfluxDBClient(url="http://localhost:8086", token=token, org=org) as client:
#     write_api = client.write_api(write_options=ASYNCHRONOUS)
#
#     data = "test_bucket,host=host1 used_percent=23.43234543"
#     data = "test_bucket,host=host1 used_percent=23.43234543"
#     write_api.write(bucket, org, data)


# client.close()
