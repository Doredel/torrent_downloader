import logging
import time

import tqdm
import typer

import constants
import magnet_downloader


logger = logging.getLogger("torrent_downloader_cli")

# Create a handler
# link handler to logger
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

app = typer.Typer()

@app.command()
def download_torrent(magnet_link: str):
    downloader_obj = magnet_downloader.MagnetDownloader(magnet_link, constants.MOVIES_FOLDER, constants.PORT)

    logger.info("start downloading...")

    last = 0
    with tqdm.tqdm(total=100) as pbar:
        while not downloader_obj.is_seeding():
            diff_to_add = (downloader_obj.get_status().progress * 100) - last
            
            pbar.update(diff_to_add)
            last += diff_to_add
            
            time.sleep(1)
            
    
    logger.info("finish downloading!")


if __name__ == "__main__":
    app()
    
