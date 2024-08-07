import itertools
import logging
import shutil
import threading
import time
import os

import telebot

import magnet_downloader

import constants

BOT_TOKEN = open("telegram_token.txt", 'r').read()

logger = logging.getLogger("torrent_downloader_telegram_bot")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

bot = telebot.TeleBot(BOT_TOKEN)

cleanup_flag = threading.Event()

downloader_pool_lock = threading.Lock()
downloader_pool = []

subscribers = set([])

@bot.message_handler(commands=['disk'])
def disk_space(message):
    disk_usage = shutil.disk_usage("/mnt/external")

    format_usage = f"""
    Total\tUsed\tFree
    """
#    {hurry.filesize.size(disk_usage.total)}\t{hurry.filesize.size(disk_usage.used)}\t{hurry.filesize.size(disk_usage.free)}


    bot.reply_to(message, format_usage)


# TODO: add help/start button
@bot.message_handler(commands=["start", "help"])
def show_usage(message):
    pass

# TODO: convert to button
@bot.message_handler(commands=["ls"])
def print_current_movies(message):
    output = [os.path.basename(dir_name) for dir_name, _, _ in os.walk(constants.MOVIES_FOLDER)]
    bot.reply_to(message, "\n".join(output))


# TODO: convert to button
@bot.message_handler(commands=['new'])
def spawn_new(message):
    msg = bot.reply_to(message, "Hi there, please insert a magnet link")
    bot.register_next_step_handler(msg, magent_link_handler)


def magent_link_handler(message):
    # TODO: there must be a better way to write this function
    try:
        downloader_obj = magnet_downloader.MagnetDownloader(message.text, constants.MOVIES_FOLDER, constants.PORT)
    except:
        bot.reply_to(
            message, "something went wrong, are you sure this is a magnet?")
        return

    with downloader_pool_lock:
        downloader_pool.append(downloader_obj)
    
    subscribers.add(message.chat.id)
    bot.reply_to(message, "link has been added, starting download")

# TODO: convert to button
@bot.message_handler(commands=['status'])
def status_all(message):
    with downloader_pool_lock:
        if not downloader_pool:
            bot.reply_to(message, "There are no torrent in download")
        
        for downloader_obj in downloader_pool:
            bot.reply_to(message, downloader_obj)

#TODO: add ping on compleation
def garbage_collector_function():
    cleanup_flag.set()
    logger.info("garbage collenction is on")

    while cleanup_flag.is_set():
        logger.info("entering sleep")
        time.sleep(constants.CLEANUP_TIMEOUT)
        logger.info("clean up is in session")

        with downloader_pool_lock:
            downloader_pool_ready_to_delete = itertools.filterfalse(
                lambda downloader_obj: not downloader_obj.is_seeding(), downloader_pool)
            
            for chat_id, downloader_obj in itertools.product(subscribers, downloader_pool_ready_to_delete):
                bot.send_message(chat_id, f"{downloader_obj.get_name()} has finished")
            
            downloader_pool[:] = itertools.filterfalse(
                lambda downloader_obj: downloader_obj.is_seeding(), downloader_pool)
                    
        logger.info("done cleaning up for now")


def init():
    logger.setLevel(logging.INFO)

    # This would keep the ram clean (hopfully)
    garbage_collector = threading.Thread(target=garbage_collector_function)

    # TODO: keep links that are mid download in tmp_file, for continue downloading after power off

    garbage_collector.start()
    bot.infinity_polling()

    # bot is shuting down let it finish cleaning before shut down
    cleanup_flag.clear()
    garbage_collector.join()


if __name__ == "__main__":
    init()
