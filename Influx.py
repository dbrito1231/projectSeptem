from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS, SYNCHRONOUS
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
                    point = Point("devices") \
                        .tag("ip", f"{ip}") \
                        .tag("host", f"{hostname}") \
                        .tag("mac", f"{mac}") \
                        .field("os", f"{dev_os}") \
                        .field("vendor", f"{vendor}") \
                        .field("port", port)
                    sequence.append(point)
            except TypeError:
                point = Point("devices") \
                    .tag("ip", f"{ip}") \
                    .tag("host", f"{hostname}") \
                    .tag("mac", f"{mac}") \
                    .field("os", f"{dev_os}") \
                    .field("vendor", f"{vendor}") \
                    .field("port", -1)
                sequence.append(point)
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
        # tf = ["speeds",
        #       f"source={data['source_ip']}",
        #       f"download={data['download']}, "
        #       f"upload={data['upload']}",
        #       f"ping={data['ping']}",
        #       f"bytes_sent={data['bytes_sent']}",
        #       f"bytes_received={data['bytes_recv']}",
        #       f"uphosts={hosts['uphosts']}",
        #       f"available_ips={hosts['downhosts']}",
        #       f"total_ips={hosts['totalhosts']}"]
        # fields = ",".join(tf[2:])
        # query = f"{tf[0]},{tf[1]} {fields}"
        point = Point("speeds") \
            .tag("source", data['source_ip']) \
            .field("download", data['download']) \
            .field("upload", data['upload']) \
            .field("ping", data['ping']) \
            .field("tx", data['bytes_sent']) \
            .field("rx", data['bytes_recv']) \
            .field("uphosts", hosts['uphosts']) \
            .field("available_ips", hosts['downhosts']) \
            .field("total_ips", hosts['totalhosts'])
        return point

    def update_influx(self):
        print("[!] Writing to InfluxDB")
        with InfluxDBClient(url="http://localhost:8086", token=self.token, org=self.org) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)
            device_bat = self.get_device_data()
            ports_bat = self.get_port_data()
            curr_stats = self.get_curr_net_data()
            for data_set in [device_bat, ports_bat, curr_stats]:
                for data in data_set:
                    print(data.to_line_protocol())
                    write_api.write(self.bucket, self.org, data)
            # print(" [+] Devices updated!")
            # write_api.write(self.bucket, self.org, ports_bat)
            # print(" [+] Ports updated!")
            # write_api.write(self.bucket, self.org, curr_stats)
            # print(" [+] Network status updated!")
        print("[+] Write to db completed!")
        client.close()
