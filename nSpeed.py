"""
    Name: nSpeed.py
    Author: Damian Brito (https://github.com/dbrito1231)
    Date: 12/26/2021
    Description: Speedtest.net Python wrapper
"""
from datetime import datetime

from speedtest import Speedtest
import pandas as pd
import pprint


def bytes_to_mb(data):
    return round(data / 1000000, 2)


class Speeder(Speedtest):
    primary_srv = None
    threads = None
    down = None
    up = None
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
        print("[-] Testing Download")
        self.download(threads=self.threads)
        print("[+] Download completed. Testing Upload")
        self.upload(threads=self.threads)
        print("[+] Upload completed. Cleaning results")
        res = self.results.dict()
        results = self.process_data(res)
        self.down, self.up, self.ping = list(results.values())[:3]
        return results

    def process_data(self, r):
        data = {
            'date': datetime.now().date().strftime('%m/%d/%Y'),
            'time': datetime.now().time().strftime("%H:%M:%S"),
            'download': bytes_to_mb(r['download']),
            'upload': bytes_to_mb(r['upload']),
            'ping': round(r['ping'], 2),
            'bytes_sent': bytes_to_mb(r['bytes_sent']),
            'bytes_recv': bytes_to_mb(r['bytes_received']),
            'source_ip': r['client']['ip'],
        }
        # self.set_primary_server(r['server'])
        return data


if __name__ == '__main__':
    x = Speeder()
    results = x.run()
    pprint.pprint(results)
