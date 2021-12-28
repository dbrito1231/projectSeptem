"""
    Name: nSpeed.py
    Author: Damian Brito (https://github.com/dbrito1231)
    Date: 12/26/2021
    Description: Speedtest.net Python wrapper
"""
from speedtest import Speedtest
import pandas as pd


def bytes_to_mb(data):
    return round(data / 1000000, 2)


class Speeder(Speedtest):
    primary_srv = None
    threads = None
    download = None
    upload = None
    ping = None

    def __init__(self, threads=3):
        super().__init__()
        self.primary_srv = pd.Series(self.get_best_server())
        self.threads = threads

    def set_primary_server(self, srv_data):
        self.primary_srv = pd.Series(srv_data)

    def get_curr_threads(self):
        return self.threads

    def set_curr_threads(self, threads):
        if threads > 0:
            self.threads = threads
        else:
            self.threads = 3

    def get_all_servers(self):
        servers = pd.DataFrame(self.get_closest_servers())
        return servers

    def get_closest_srv(self):
        return self.get_all_servers().iloc[0]

    def get_download(self):
        return self.download

    def get_upload(self):
        return self.upload

    def get_ping(self):
        return self.ping

    def run(self):
        self.download(threads=self.threads)
        self.upload(threads=self.threads)
        res = self.results.dict()
        results = self.process_data(res)
        self.download, self.upload, self.ping = results[:3]
        return results

    def process_data(self, results):
        download = bytes_to_mb(results['download'])
        upload = bytes_to_mb(results['upload'])
        ping = round(results['ping'], 2)
        bytes_sent = bytes_to_mb(results['bytes_sent'])
        bytes_received = bytes_to_mb(results['bytes_received'])
        source_public_ip = results['client']['ip']
        self.set_primary_server(results['server'])
        return download, upload, ping, bytes_sent, bytes_received, source_public_ip
