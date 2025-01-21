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

    def __init__(self, configuration):
        self.configuration = configuration
        self.seedtime = self.configuration.get('seedtime')        
        self.open_torrent()
        self.torrentclient = Transmission406(self.tracker_info_hash())
        #self.torrentclient = Transmission406(self.configuration['torrent'])
        logging.info(f"Initialized process for torrent: {self.configuration['torrent']}")

    def open_torrent(self):
        torrent_file = self.configuration['torrent']
        with open(torrent_file, 'rb') as tf:
            data = tf.read()
        self.b_enc = bencoding()
        self.metainfo = self.b_enc.bdecode(data)
        self.info = self.metainfo['info']
        if 'length' not in self.info:
            self.info['length'] = 0
            for file in self.info['files']:
                self.info['length'] += file['length']
            logging.debug(f"Files in torrent: {pretty_data(self.info['files'])}")

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
            except requests.exceptions.ConnectionError as e:
                logging.warning("Connection error, retrying...")
                time.sleep(1)
                continue
            break
        return r.content

    def tracker_start_request(self):
        tc = self.torrentclient
        headers = tc.get_headers()
        params = tc.get_query(uploaded=0,
                              downloaded=0,
                              event='started')

        logging.info("Sending 'started' event to tracker.")
        content = self.send_request(params, headers)
        self.tracker_response_parser(content)

    def tracker_response_parser(self, tr_response):
        b_enc = bencoding()
        response = b_enc.bdecode(tr_response)
        logging.debug("Tracker response received.")
        logging.debug(pretty_data(response))
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
        logging.info(f"Interval from tracker: {self.interval} seconds")

    def wait(self, start_time, seedtime):
        """
        Wait for the interval while checking the seed time limit.
        
        Args:
            start_time (float): The starting time of the seeding process.
            seedtime (int): The maximum seed time in seconds (None for unlimited).
        """
        random_badtime = random.randint(10, 15) * 60  # Interval between 10 and 15 minutes
        self.interval = random_badtime
        logging.info(f"Waiting for {self.interval // 60} minutes before the next tracker request.")
        
        pbar = tqdm(total=self.interval, desc="Waiting", leave=False)
        t = 0
        while t < self.interval:
            time.sleep(1)  # Wait for 1 second
            t += 1
            pbar.update(1)
            
            # Check if the seed time limit is exceeded
            elapsed_time = time.time() - start_time
            if seedtime and elapsed_time >= seedtime:
                logging.info("Seed time limit reached during wait. Stopping process.")
                pbar.close()
                return False  # Signal to stop the process
        
        pbar.close()
        return True  # Signal to continue

    def tracker_process(self):
        """Main process loop for interacting with multiple torrents simultaneously."""
        torrents = self.configuration['torrents']  # List of torrents to process
        start_time = time.time()  # Start time for the entire seeding process
        completed = set()  # Set to track completed torrents
        interval = random.randint(10, 15) * 60  # Common interval for all torrents

        logging.debug(f"Starting tracker process for {len(torrents)} torrents with seedtime: {self.seedtime} seconds")
        logging.info(f"Initial interval set to {interval // 60} minutes for all torrents.")

        while len(completed) < len(torrents):
            for torrent in torrents:
                # Skip torrents already completed
                if torrent in completed:
                    continue

                elapsed_time = time.time() - start_time
                logging.debug(f"Torrent: {torrent}, Elapsed time: {elapsed_time:.2f} seconds, Seed time: {self.seedtime} seconds")

                # Check if seed time limit is exceeded
                if self.seedtime and elapsed_time >= self.seedtime:
                    logging.info(f"Seed time limit reached for torrent: {torrent}. Stopping process for this torrent.")
                    completed.add(torrent)
                    continue

                # Process the torrent (upload/download simulation)
                logging.info(f"Processing torrent: {torrent}")
                min_up = int(interval - (interval * 0.1))  # 90% of interval
                max_up = int(interval)  # Full interval
                randomize_upload = random.randint(min_up, max_up)
                uploaded = int(self.configuration['upload']) * 1000 * randomize_upload
                logging.info(f"Upload amount sent: {uploaded} bytes (torrent: {torrent})")

                # get download
                downloaded = 0

                # Send tracker update
                tc = self.torrentclient
                headers = tc.get_headers()
                params = tc.get_query(uploaded=uploaded,
                                      downloaded=downloaded,
                                      event='stopped')
                content = self.send_request(params, headers)
                self.tracker_response_parser(content)

            # Use a single wait for all torrents
            remaining_time = self.seedtime - elapsed_time if self.seedtime else None
            if remaining_time and remaining_time < interval:
                logging.debug(f"Adjusting wait time to {remaining_time:.2f} seconds to match seedtime.")
                interval = int(remaining_time)

            # Use wait to handle the time for all torrents
            if not self.wait(start_time, interval):
                break

        logging.info("All torrents have been processed.")

