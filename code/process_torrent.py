from code.decoding_bencoded import bencoding
from code.torrentclientfactory import Transmission406
from code.pretty import pretty_data, pretty_GET

from hashlib import sha1
from urllib.parse import quote_plus
import requests
import logging
import random
from tqdm import tqdm
import time

from struct import unpack

logging.basicConfig(level=logging.DEBUG)

class process_torrent():

    def __init__(self, torrent_file, compact=1, supportcrypto=1):
        self.torrent_file = torrent_file
        self.open_torrent()
        self.torrentclient = Transmission406(self.tracker_info_hash(), compact=compact, supportcrypto=supportcrypto)
        self.interval = None
        self.seeders = 0
        self.leechers = 0
        logging.info(f"Initialized process for torrent: {self.torrent_file}")

    def get_torrent_name(self):
        return self.info.get('name', 'N/A')

    def open_torrent(self):
        with open(self.torrent_file, 'rb') as tf:
            data = tf.read()
        self.b_enc = bencoding()
        self.metainfo = self.b_enc.bdecode(data)
        self.info = self.metainfo['info']
        if 'length' not in self.info:
            self.info['length'] = 0
            for file in self.info['files']:
                self.info['length'] += file['length']
            logging.debug(f"Files in torrent: {pretty_data(self.info['files'])}")

    def get_torrent_size(self):
        return self.info['length']

    def tracker_info_hash(self):
        raw_info = self.b_enc.get_dict('info')
        hash_factory = sha1()
        hash_factory.update(raw_info)
        hashed = hash_factory.hexdigest()
        sha = bytearray.fromhex(hashed)
        return str(quote_plus(sha))

    def send_request(self, params, headers):
        url = self.metainfo['announce']
        logging.debug(pretty_GET(url, headers, params))
        while True:
            try:
                r = requests.get(url, params=params, headers=headers)
                content = r.content
                response = bencoding().bdecode(content)
                if 'failure reason' in response:
                    failure_reason = response['failure reason']
                    logging.warning(f"Tracker error: {failure_reason}")
                    if 'Unregistered torrent' in failure_reason:
                        logging.info("Unregistered torrent, waiting 15 minutes before retrying...")
                        time.sleep(900)
                        continue
                    elif 'Your client does not support compact announces' in failure_reason:
                        logging.info("Compact announce not supported, retrying with compact=0")
                        self.torrentclient = Transmission406(self.tracker_info_hash(), compact=0)
                        # We need to rebuild the query parameters
                        # This is a bit of a hack, but it's the easiest way to do it
                        # we need to extract the event from the params
                        event = None
                        if 'event' in params:
                            event_param = [p for p in params.split('&') if 'event' in p]
                            if event_param:
                                event = event_param[0].split('=')[1]

                        uploaded = 0
                        if 'uploaded' in params:
                            uploaded_param = [p for p in params.split('&') if 'uploaded' in p]
                            if uploaded_param:
                                uploaded = int(uploaded_param[0].split('=')[1])

                        downloaded = 0
                        if 'downloaded' in params:
                            downloaded_param = [p for p in params.split('&') if 'downloaded' in p]
                            if downloaded_param:
                                downloaded = int(downloaded_param[0].split('=')[1])

                        params = self.torrentclient.get_query(
                            uploaded=uploaded,
                            downloaded=downloaded,
                            left=0, # This is not correct, but we don't have the value here
                            event=event
                        )
                        headers = self.torrentclient.get_headers()
                        continue

            except requests.exceptions.ConnectionError as e:
                logging.warning("Connection error, retrying...")
                time.sleep(60)
                continue
            break
        return content

    def tracker_start_request(self):
        tc = self.torrentclient
        headers = tc.get_headers()
        params = tc.get_query(uploaded=0,
                              downloaded=0,
                              event='started')

        logging.info("Sending 'started' event to tracker.")
        content = self.send_request(params, headers)
        self.tracker_response_parser(content)

    def tracker_update_request(self, uploaded, downloaded):
        tc = self.torrentclient
        headers = tc.get_headers()
        params = tc.get_query(uploaded=uploaded,
                              downloaded=downloaded)

        logging.info("Sending update to tracker.")
        content = self.send_request(params, headers)
        self.tracker_response_parser(content)

    def tracker_response_parser(self, tr_response):
        b_enc = bencoding()
        response = b_enc.bdecode(tr_response)
        logging.debug("Tracker response received.")
        logging.debug(pretty_data(response))
        if 'failure reason' in response:
            return

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
        
        if 'interval' in response:
            self.interval = response['interval']
            logging.info(f"Interval from tracker: {self.interval} seconds")

        if 'complete' in response:
            self.seeders = response['complete']

        if 'incomplete' in response:
            self.leechers = response['incomplete']

