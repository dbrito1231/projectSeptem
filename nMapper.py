"""
    Name: nMapper.py
    Author: Damian Brito (https://github.com/dbrito1231)
    Date: 12/12/2021
    Description: Nmap Python wrapper
"""
from datetime import datetime
from nmap import PortScanner


class Mapper(PortScanner):
    ip_addr = None
    __current__ = None
    device_objects = None

    def __init__(self, subnet_addr):
        super().__init__()
        self.ip_addr = subnet_addr
        print("[-] Initializing Mapper")
        print("[-] Scanning network")
        self.__current__ = self.scan(hosts=f'{self.ip_addr}/24', arguments='-T4 -O')
        print("[+] Init scan completed!")

    def generate_device_objects(self):
        _ = []
        print("[-] Gathering devices on the network")
        for dev in self.get_hosts():
            if dev.split('.')[-1] != '0':
                _.append(DeviceObj(self.__current__['scan'][dev]))
            else:
                continue
        self.device_objects = _.copy()
        print("[+] Device gathering completed!")

    def get_current_used_ports(self):
        curr_ports = []
        for dev in self.device_objects:
            ports = dev.get_ports()
            if isinstance(ports, list):
                for port in dev.get_ports():
                    curr_ports.append(port)
            else:
                print(f"No ports found for {dev.get_ip_addr()}")
        curr_ports = list(set(curr_ports))
        return sorted(curr_ports)

    def get_hosts(self):
        return list(self.__current__['scan'].keys())

    def get_current_netstats(self):
        curr = self.__current__['nmap']['scanstats'].copy()
        curr.pop('elapsed')
        curr['uphosts'] = int(curr['uphosts'])
        curr['downhosts'] = int(curr['downhosts'])
        curr['totalhosts'] = int(curr['totalhosts'])
        curr['timestamp'] = datetime.strptime(curr['timestr'],
                                              '%a %b %d %H:%M:%S %Y')
        return curr

    def get_ip_obj(self, ip_address):
        return self.__current__['scan'][ip_address]

    def update(self):
        print('[-] Updating current network. Please wait.')
        self.__current__ = self.scan(hosts=f'{self.ip_addr}/24', arguments='-T4 -O')
        print("[+] Network mapping completed!")


class DeviceObj:
    ip = None
    hostname = None
    mac = None
    vendor = None
    ports = None
    OS = None

    def __init__(self, port_scan_obj):
        self.ip = port_scan_obj['addresses']['ipv4']
        print(f"\t[-] Found node on {self.ip}.")
        try:
            self.mac = port_scan_obj['addresses']['mac']
        except KeyError:
            print("\t\t[X] No MAC address found!")
            pass
        self.hostname = port_scan_obj['hostnames'][0]['name']
        if len(port_scan_obj['osmatch']) > 0:
            self.OS = port_scan_obj['osmatch'][0]['name']
        if len(port_scan_obj['vendor'].values()) > 0:
            self.vendor = list(port_scan_obj['vendor'].values())
        try:
            self.ports = list(port_scan_obj['tcp'].keys())
        except KeyError:
            if 'portused' in port_scan_obj.keys():
                self.ports = [port['portid'] for port in port_scan_obj['portused'] if port['state'] != 'closed']
                self.ports = [int(str_port) for str_port in self.ports]
            else:
                self.ports = None
        self.__raw_data__ = port_scan_obj.copy()
        print(f"\t[+] {self.ip} completed!\n")

    def get_ip_addr(self):
        return self.ip

    def get_mac_addr(self):
        return self.mac

    def get_device_name(self):
        return self.hostname

    def get_vendor_name(self):
        if self.vendor is not None:
            return self.vendor
        else:
            return "No vendor name found"

    def get_ports(self):
        if self.ports is not None and len(self.ports) != 0:
            return self.ports
        else:
            return 'No ports discovered'

    def get_os(self):
        if self.OS is not None:
            return self.OS
        elif self.__raw_data__['osmatch'] > 1:
            return 'Multiple OSes found'
        else:
            return 'No ports discovered'


if __name__ == '__main__':
    mapp = Mapper('192.168.1.0')
    mapp.generate_device_objects()
    print(mapp.get_current_netstats())
    print(f"Ports used: {mapp.get_current_used_ports()}")
