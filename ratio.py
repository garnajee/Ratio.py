from code.process_torrent import process_torrent
import argparse
import json
import sys
import re
import logging
import os
import time
import random
from tqdm import tqdm

def parse_args():
   """Create the arguments"""
   parser = argparse.ArgumentParser(description="Fake ratio")
   parser.add_argument("-c", "--config", help="Configuration file", type=str, default="config.json")
   parser.add_argument("-s", "--speed", help="Upload speed (in kB/s)", type=str)
   parser.add_argument("-t", "--time", help="Duration to seed (in days, 0 or empty for unlimitted)", type=str)
   parser.add_argument("-d", "--debug", help="Enable debug logging", action="store_true")
   return parser.parse_args()

def load_configuration(configuration_file):
    with open(configuration_file) as f:
        configuration = json.load(f)

    if 'torrents' not in configuration:
        return None

    return configuration

def get_time(timestring):
    """
    Covnerts a time string (such as '2d3h15m') into total seconds.
    Empty string or 0 represents an unlimited time.
    """
    if not timestring or timestring == "0":
        return None  # No time limit (unlimited)

    # Define the time units and their corresponding values in seconds
    time_units = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}
    total_seconds = 0

    # Find all time occurrences using regex (e.g., 2d3h15m)
    matches = re.findall(r'(\d+)([dhms])', timestring)
    
    for value, unit in matches:
        total_seconds += int(value) * time_units[unit]

    # Return the total seconds, or None if no valid time was found
    return total_seconds if total_seconds > 0 else None

def get_torrent_files(path):
    if os.path.isdir(path):
        return [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.torrent')]
    elif os.path.isfile(path) and path.endswith('.torrent'):
        return [path]
    else:
        return []

def get_upload_speed(size_in_bytes, speed_config):
    if speed_config:
        return int(speed_config)

    # size in MB
    size_in_mb = size_in_bytes / 1024 / 1024
    if size_in_mb < 100:
        return random.randint(50, 150)
    elif size_in_mb < 500:
        return random.randint(150, 400)
    elif size_in_mb < 1024:
        return random.randint(400, 800)
    else:
        return random.randint(800, 2000)

if __name__ == "__main__":
    args = parse_args()
    
    # Configure logger
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")
    
    if args.config:
        configuration = load_configuration(args.config)
    else:
        sys.exit("No configuration file provided.")
   
    if not configuration:
        sys.exit("Error in config file.")
 
    # Overwrite config values with CLI arguments if provided
    if args.speed:
        configuration['upload'] = args.speed
    else:
        configuration['upload'] = None

    if args.time:
        seed_time = get_time(args.time)
        if seed_time is not None:
            configuration['seedtime'] = seed_time
        else:
            configuration['seedtime'] = None
    elif 'seedtime' in configuration and configuration['seedtime']:
        configuration['seedtime'] = get_time(configuration['seedtime'])
    else:
        configuration['seedtime'] = None

    torrent_paths = configuration['torrents']
    torrent_files = []
    if isinstance(torrent_paths, list):
        for path in torrent_paths:
            torrent_files.extend(get_torrent_files(path))
    else:
        torrent_files.extend(get_torrent_files(torrent_paths))

    if not torrent_files:
        sys.exit("No torrent files found.")
    
    processes = []
    for torrent_file in torrent_files:
        logging.info(f"Starting processing for: {torrent_file}")
        process = process_torrent(torrent_file)
        processes.append(process)

    for process in processes:
        process.tracker_start_request()

    start_time = time.time()
    while True:

        # Check if seed time limit is exceeded
        elapsed_time = time.time() - start_time
        if configuration['seedtime'] and elapsed_time >= configuration['seedtime']:
            logging.info("Seed time limit reached. Stopping all processes.")
            break

        # All torrents will have the same interval
        # Get the interval from the first torrent, if not set, set it to 15 minutes
        interval = processes[0].interval if processes[0].interval else 900

        # Wait for the interval
        pbar = tqdm(total=interval, desc="Waiting", leave=False)
        for i in range(interval):
            time.sleep(1)
            pbar.update(1)
            elapsed_time = time.time() - start_time
            if configuration['seedtime'] and elapsed_time >= configuration['seedtime']:
                break
        pbar.close()


        for process in processes:
            upload_speed = get_upload_speed(process.get_torrent_size(), configuration['upload'])
            uploaded = upload_speed * 1024 * interval
            process.tracker_update_request(uploaded=uploaded, downloaded=0)

    logging.info("All torrents are being processed.")

