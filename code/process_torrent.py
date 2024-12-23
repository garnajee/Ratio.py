from code.decoding_bencoded import bencoding
from code.torrentclientfactory import Transmission406
from code.pretty import pretty_data, pretty_GET

from hashlib import sha1
from urllib.parse import quote_plus
import requests
import logging
import random
from tqdm import tqdm
from time import sleep

from struct import unpack
import os

logging.basicConfig(level=logging.INFO)

class process_torrent():
    def __init__(self, configuration):
        self.configuration = configuration
        self.open_torrent()
        self.timer = 0
        self.torrentclient = Transmission406(self.tracker_info_hash())

    def open_torrent(self):
        torrent_file = self.configuration['torrent']
        with open(torrent_file, 'rb') as tf:
            data = tf.read()
        self.b_enc = bencoding()
        self.metainfo = self.b_enc.bdecode(data)
        self.info = self.metainfo['info']
        self.files = []
        if 'length' not in self.info:
            self.info['length'] = 0
            for file in self.info['files']:
                self.info['length'] += file['length']
                self.files.append(file['path'])
            # print(pretty_data(self.info['files']))
            # print(self.files)

    def tracker_info_hash(self):
        raw_info = self.b_enc.get_dict('info')
        hash_factory = sha1()
        hash_factory.update(raw_info)
        hashed = hash_factory.hexdigest()
        sha = bytearray.fromhex(hashed)
        return str(quote_plus(sha))

    def send_request(self, params, headers):
        url = self.metainfo['announce']
        print(pretty_GET(url, headers, params))
        while True:
            try:
                r = requests.get(url, params=params, headers=headers)
            except requests.exceptions.ConnectionError as e:
                sleep(1)
                continue
            break
        return r.content

    def tracker_start_request(self):
        tc = self.torrentclient
        headers = tc.get_headers()
        params = tc.get_query(uploaded=0,
                              downloaded=0,
                              event='started')
        content = self.send_request(params, headers)
        self.tracker_response_parser(content)

    def tracker_response_parser(self, tr_response):
        b_enc = bencoding()
        response = b_enc.bdecode(tr_response)
        raw_peers = b_enc.get_dict('peers')
        i = 0
        peers = []
        while i<len(raw_peers)-6:
            peer = raw_peers[i:i+6]
            i+=6
            unpacked_ip = unpack('BBBB', peer[0:4])
            ip = ".".join(str(i) for i in unpacked_ip)
            unpacked_port = unpack('!H', peer[4:6])
            port = unpacked_port[0]
            peers.append((ip, port))
        self.interval = response['interval']

def seedqueue(queue, time):
    while time > 0:
        waitingqueue = ""
        for torrent in queue:
            if torrent.timer <= 0:
                torrent.tracker_start_request()

                min_up = torrent.interval-(torrent.interval*0.1)
                max_up = torrent.interval
                randomize_upload = random.randint(min_up, max_up)
                uploaded = int(torrent.configuration['upload'])*1000*randomize_upload

                downloaded = 0

                tc = torrent.torrentclient
                headers = tc.get_headers()
                params = tc.get_query(uploaded=uploaded,
                                        downloaded=downloaded,
                                        event='stopped')
                content = torrent.send_request(params, headers)
                torrent.tracker_response_parser(content)

                torrent.timer = random.randint(10,15)*60   # interval to send request betwen 10min and 15min
                torrent.interval = torrent.timer
            else:
                torrent.timer -= 1
                waitingqueue += f"Waiting {torrent.timer} seconds for {torrent.configuration['torrent']}" + "\n"
        os.system('cls' if os.name == 'nt' else 'clear')
        print(waitingqueue)
        sleep(1)
        time -= 1