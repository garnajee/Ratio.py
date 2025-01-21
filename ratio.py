from code.process_torrent import process_torrent
import argparse
import json
import sys
import re
import logging

def parse_args():
   """Create the arguments"""
   parser = argparse.ArgumentParser(description="Fake ratio")
   parser.add_argument("-c", "--config", help="Configuration file", type=str, default="config.json")
   parser.add_argument("-s", "--speed", help="Upload speed (in kB/s)", type=str, default="350")
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

if __name__ == "__main__":
    args = parse_args()
    
    # Configure logger
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(levelname)s - %(message)s")
    
    if args.config:
        configuration = load_configuration(args.config)
        print(configuration)
    else:
        sys.exit("No configuration file provided.")
   
    if not configuration:
        sys.exit("Error in config file.")
 
    # Overwrite config values with CLI arguments if provided
    if args.speed:
        configuration['upload'] = args.speed
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

    torrents = configuration['torrents']
    
    processes = []
    for torrent_file in torrents:
        config = configuration.copy()
        config['torrent'] = torrent_file

        logging.info(f"Starting processing for: {torrent_file}")
        process = process_torrent(config)
        processes.append(process)

    for process in processes:
        process.tracker_process()

    logging.info("All torrents are being processed.")

