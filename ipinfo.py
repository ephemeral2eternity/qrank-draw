import json
import requests
import os
import socket
import struct
import urllib2

def is_reserved(ip):
    f = struct.unpack('!I', socket.inet_aton(ip))[0]
    private = (
        [2130706432, 4278190080], # 127.0.0.0,   255.0.0.0   http://tools.ietf.org/html/rfc3330
        [3232235520, 4294901760], # 192.168.0.0, 255.255.0.0 http://tools.ietf.org/html/rfc1918
        [2886729728, 4293918720], # 172.16.0.0,  255.240.0.0 http://tools.ietf.org/html/rfc1918
        [167772160,  4278190080], # 10.0.0.0,    255.0.0.0   http://tools.ietf.org/html/rfc1918
    )
    for net in private:
        if (f & net[1]) == net[0]:
            return True
    return False

def ipinfo(ip=None):
    if ip:
        url = 'http://ipinfo.io/' + ip
    else:
        url = 'http://ipinfo.io/'

    hop_info = {}
    try:
        resp = requests.get(url)
        hop_info = json.loads(resp.text)
    except:
        print "[Error]Failed to get hop info from ipinfo.io, the maximum # of requests have been achieved today!"
        print "[Error]The ip needed is :", ip
        exit(0)

    if 'org' in hop_info.keys():
        hop_org = hop_info['org']
        hop_org_items = hop_org.split()
        hop_info['AS'] = int(hop_org_items[0][2:])
        hop_info['ISP'] = " ".join(hop_org_items[1:])
    else:
        hop_info['AS'] = -1
        hop_info['ISP'] = "unknown"

    if 'loc' in hop_info.keys():
        locations = hop_info['loc'].split(',')
        hop_info['latitude'] = float(locations[0])
        hop_info['longitude'] = float(locations[1])
    else:
        hop_info['latitude'] = 0.0
        hop_info['longitude'] = 0.0

    if ('city' not in hop_info.keys()):
        hop_info['city'] = ''

    if ('region' not in hop_info.keys()):
        hop_info['region'] = ''

    if ('country' not in hop_info.keys()):
        hop_info['country'] = ''

    if ('hostname' not in hop_info.keys()):
        hop_info['hostname'] = ip
    elif ('No' in hop_info['hostname']):
        hop_info['hostname'] = ip

    hop_info['name'] = hop_info['hostname']

    return hop_info