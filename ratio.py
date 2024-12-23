from code.process_torrent import process_torrent, seedqueue
import argparse
import json
import sys
import os

def parse_args():
   """Create the arguments"""
   parser = argparse.ArgumentParser(description="Fake ratio")
   parser.add_argument("-c", "--configuration", help="Configuration file")
   parser.add_argument("-t", "--time", help="Time to seed", type=str, default="1d")
#    parser.add_argument("-s", "--speed", help="Speed to seed", type=str, default="350")
   return parser.parse_args()

def load_configuration(configuration_file):
    with open(configuration_file) as f:
        configuration = json.load(f)
    if 'torrents' not in configuration:
        return None
    return configuration

def get_time(timestring):
    days = hours = minutes = seconds = 0
    if 'd' in timestring:
        days, timestring = timestring.split('d')
        days = int(days)
    if 'h' in timestring:
        hours, timestring = timestring.split('h')
        hours = int(hours)
    if 'm' in timestring:
        minutes, timestring = timestring.split('m')
        minutes = int(minutes)
    if 's' in timestring:
        seconds = int(timestring.split('s')[0])
    total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
    return total_seconds

if __name__ == "__main__":
    queue = []
    args = parse_args()
    if args.configuration:
        configuration = load_configuration(args.configuration)
    else:
        sys.exit()
    if not configuration:
        sys.exit()
    folder_path = configuration['torrents']
    torrents_path = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".torrent"):
                torrents_path.append(os.path.join(root, file))
    for torrent_file in torrents_path:
        config = {
            "torrent": torrent_file,
            "upload": configuration['upload']
        }
        torrent = process_torrent(config)
        queue.append(torrent)
    print(f'Got {len(queue)} torrents')
    time = get_time(args.time)
    seedqueue(queue, time)