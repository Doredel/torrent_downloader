import itertools
import logging
import shutil
import threading
import time

import hurry.filesize
import telebot

import magnet_downloader

BOT_TOKEN = open("telegram_token.txt", 'r').read()
MOVIES_FOLDER = '/mnt/external/movies'

# time in seconds
CLEANUP_TIMEOUT = 60

# TODO: give support to more then 1 port
PORT = 6881

bot = telebot.TeleBot(BOT_TOKEN)

cleanup_flag = threading.Event()

downloader_pool_lock = threading.Lock()
downloader_pool = []


@bot.message_handler(commands=['disk'])
def disk_space(message):
    disk_usage = shutil.disk_usage("/mnt/external")
    
    format_usage = f"""
    Total\tUsed\tFree
    {hurry.filesize.size(disk_usage.total)}\t{hurry.filesize.size(disk_usage.used)}\t{hurry.filesize.size(disk_usage.free)}
    """

    bot.reply_to(message, format_usage)


# TODO: add help/start button
# TODO: show list of downloaded movies button

# TODO: convert to button
@bot.message_handler(commands=['new'])
def spawn_new(message):
    msg = bot.reply_to(message, "Hi there, please insert a magnet link")
    bot.register_next_step_handler(msg, magent_link_handler)


def magent_link_handler(message):
    # TODO: there must be a better way to write this function
    try:
        downloader_obj = magnet_downloader.MagnetDownloader(
            message.text, MOVIES_FOLDER, PORT)
    except:
        bot.reply_to(
            message, "something went wrong, are you sure this is a magnet?")
        return

    with downloader_pool_lock:
        downloader_pool.append(downloader_obj)

    bot.reply_to(message, "link has been added, starting download")

# TODO: convert to button
@bot.message_handler(commands=['status'])
def status_all(message):
    with downloader_pool_lock:
        for downloader_obj in downloader_pool:
            bot.reply_to(message, downloader_obj)
        else:
            bot.reply_to(message, "There are no torrent in download")


def garbage_collector_function():
    cleanup_flag.set()
    logging.info("garbage collenction is on")
    
    while cleanup_flag.is_set():
        logging.info("entering sleep")
        time.sleep(CLEANUP_TIMEOUT)
        logging.info("clean up is in session")

        with downloader_pool_lock:
            downloader_pool[:] = itertools.filterfalse(
                lambda downloader_obj: not downloader_obj.is_seeding(), downloader_pool)

        logging.info("done cleaning up for now")


def init():
    logging.getLogger().setLevel(logging.INFO)

    # This would keep the ram clean (hopfully)
    garbage_collector = threading.Thread(target=garbage_collector_function)

    # TODO: keep links that are mid download in tmp_file, for continue downloading after power off
    
    garbage_collector.start()
    bot.infinity_polling()

    #bot is shuting down let it finish cleaning before shut down
    cleanup_flag.clear()
    garbage_collector.join()


if __name__ == "__main__":
    init()
