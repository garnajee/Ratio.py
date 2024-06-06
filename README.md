# Ratio.py

Ratio.py is a small command line RatioMaster.Net like in Python3. It fakes upload stats of a torrent. 
Current emulators available are:

- Transmission 3.00

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
   "torrent": "<Torrent file path>",
   "upload": "<Upload speed (kB/s)>"
}
```

### Usage:

```bash
python3 ratio.py -c config.json 
```

To run (multiple instances) in background :

```bash
nohup python3 ratio.py -c config.json &
nohup python3 ratio.py -c config.json &> nohup2.out &
```

View logs :

```bash
tail -f nohup.out
```

*This project is an updated fork of [this project](https://github.com/MisterDaneel/Ratio.py).*

