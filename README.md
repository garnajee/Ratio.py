# Ratio.py

[![Update Transmission Version](https://github.com/garnajee/Ratio.py/actions/workflows/update-transmission-version.yml/badge.svg)](https://github.com/garnajee/Ratio.py/actions/workflows/update-transmission-version.yml)

Ratio.py is a Python-based tool for faking torrent upload statistics, similar to RatioMaster.Net. It currently emulates the following BitTorrent client:

-   Transmission 4.0.6

## Features

-   **Fake Upload Stats**: Simulate uploading of torrents to improve your ratio on private trackers.
-   **Multiple Torrents**: Process multiple torrents at once, either by specifying individual files or a directory.
-   **Dynamic Upload Speed**: The upload speed is randomized and adjusted based on the size of the torrent, creating a more realistic seeding pattern.
-   **Error Handling**: The script is designed to handle common tracker errors, such as "Unregistered torrent" and "Compact announce not supported," by retrying or adjusting its parameters.
-   **Docker Support**: Run the script in a lightweight, isolated environment using Docker and Docker Compose.

## Getting Started

### Prerequisites

-   Python 3.x
-   Pip

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/garnajee/Ratio.py.git
    cd Ratio.py
    ```

2.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The script is configured using a `config.json` file. Here's an example:

```json
{
    "torrents": ["./torrents", "./another.torrent"],
    "upload": "350",
    "seedtime": "2d3h15m"
}
```

-   `torrents`: A path to a `.torrent` file, or a directory containing `.torrent` files. You can also provide a list of paths.
-   `upload` (optional): A fixed upload speed in kB/s. If not provided, the script will use a dynamic speed based on the torrent size.
-   `seedtime` (optional): The duration to fake seed (e.g., "2d3h15m" for 2 days, 3 hours, and 15 minutes). Use "0" or an empty string for unlimited seeding.

## Usage

### Command-Line Arguments

-   `-c`, `--config`: Path to the configuration file (default: `config.json`).
-   `-s`, `--speed`: Override the upload speed from the configuration file (in kB/s).
-   `-t`, `--time`: Override the seed time from the configuration file.
-   `-d`, `--debug`: Enable debug logging.
-   `-h`, `--help`: Show the help message.

### Running the Script

To run the script, use the following command:

```bash
python3 ratio.py
```

You can also use the command-line arguments to override the configuration:

```bash
python3 ratio.py -c my_config.json -s 500 -t 1d
```

### Running in the Background

To run the script in the background, you can use `nohup`:

```bash
nohup python3 ratio.py > ratio.log 2>&1 &
```

This will redirect the output to a `ratio.log` file. You can view the logs with `tail -f ratio.log`.

### Running with Docker

You can also run the script using Docker and Docker Compose for a more isolated and reproducible environment. The Docker image is based on Google's distroless images, which are more secure and have a smaller footprint.

1.  **Build the Docker image:**

    ```bash
    docker-compose build
    ```

2.  **Run the script:**

    ```bash
    docker-compose up
    ```

    The script will use the `config.json` file and the `torrents` directory from your host machine.

## Disclaimer

This tool is for educational purposes only. Using it may be against the terms of service of some trackers. Use it at your own risk.

*This project is an updated fork of [this project](https://github.com/MisterDaneel/Ratio.py).*
