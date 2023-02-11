import logging
import sys
import time

import typer

import magnet_downloader

MOVIES_FOLDER = '/mnt/external/movies'
PORT = 6881


def download_torrent(magnet_link: str):
    downloader_obj = magnet_downloader.MagnetDownloader(
        magnet_link, MOVIES_FOLDER, PORT)

    print("start downloading...")

    while not downloader_obj.is_seeding():
        print(f'\r{downloader_obj}', end=' ')

        sys.stdout.flush()
        time.sleep(1)
    
    print("finish downloading!")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    typer.run(download_torrent)
