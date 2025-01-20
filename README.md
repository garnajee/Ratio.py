# Ratio.py

[![Update Transmission Version](https://github.com/garnajee/Ratio.py/actions/workflows/update-transmission-version.yml/badge.svg)](https://github.com/garnajee/Ratio.py/actions/workflows/update-transmission-version.yml)

Ratio.py is a small command line RatioMaster.Net like in Python3. It fakes upload stats of a torrent. 
Current emulators available are:

- Transmission 4.0.6

### Requirements

1. Python 3.x
2. pip install -r requirements.txt
3. a torrent file (use one with lots of leechers)

### Download

Using `git` command:

```bash
git clone https://github.com/garnajee/Ratio.py.git
```

Or using `cURL`:

```bash
curl -L https://github.com/garnajee/Ratio.py/archive/master.tar.gz -o Ratio.py.tar.gz
tar xzf Ratio.py.tar.gz
rm Ratio.py.tar.gz
mv Ratio.py-master Ratio.py
```

Navigate to the folder:

```bash
cd Ratio.py
```

Then configure your `config.json` file.

### Configuration example

```js
{
   "torrent":["<Torrent file path 1>", "<Torrent file path 2>"],
   "upload": "<Upload speed (kB/s)>",
   "seedtime": "2d3h15m"
}
```

- `torrents`: A list of one of multiples torrent files to process.
- `upload`: The upload speed in kB/s.
- `seedtime`: The duration to fake seed (e.g., "2d3h15m" for 2 days, 3 hours, and 15 minutes). Use "0" or "" for unlimited.

### Usage:

Run the script with a configuration file:

```bash
python3 ratio.py -c config.json 
```

Enable debug mode for detailed logs:

```bash
python3 ratio.py -c config.json -d
```

To run (multiple instances) in background (if you want different configurations for example):

```bash
nohup python3 ratio.py -c config1.json &
nohup python3 ratio.py -c config2.json &> nohup2.out &
```

View logs :

```bash
tail -f nohup.out
```

*This project is an updated fork of [this project](https://github.com/MisterDaneel/Ratio.py).*

