import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext.dispatcher import run_async

import ipdb
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.WARNING)


import requests, time
from datetime import datetime
from parseDepartureTime import trainHasArrived
from parseDepartureTime import trainIsComing
from parseDepartureTime import checkStationTrain
from parseDepartureTime import getETA



def read_api_key(fname='api-key.txt'):
    import json
    api_key = None
    with open(fname) as f:
        api_key = json.loads(f.read())['telegram'].strip()

    return api_key


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me! Type '/watch' to begin monitoring departure of train")

def echo(bot, update):
    msg = "I received: '%s'\nThis is an unkown command. Please try something else" %update.message.text
    bot.send_message(chat_id=update.message.chat_id, text=msg)



@run_async
def watch(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Watching for next 'Saarlandstraße' departure")
    print('start watching')
    doNotifyForWait = True # only notifies for waiting the first time
    doNotifyForSoonComing = True  # only notifies for soon coming  Train the first time
    notifyOnce = False
    while True:
        try:
            # ipdb.set_trace()
            isComing, abfahrt, id = trainIsComing()

            # msg =
            # bot.send_message(chat_id=update.message.chat_id, text=msg)
            if isComing:
                bot.send_message(chat_id=update.message.chat_id, text="TRAIN %s HAS ARRIVED! at Römerplatz" %(id,))
                while not trainHasArrived(id):
                    time.sleep(2)
                msg = 'Train has left Römerplatz'
                bot.send_message(chat_id=update.message.chat_id, text=msg)
                break
            elif abfahrt:
                if doNotifyForWait:
                    msg = "Train %s comes in %s min at Saarlandstraße. Waiting for Arrival" %(id, abfahrt,)
                    bot.send_message(chat_id=update.message.chat_id, text=msg)
                    doNotifyForWait = False if notifyOnce else True

                time.sleep(60 * (abfahrt / 2))

                # continues outer while loop

            elif abfahrt == 0:
                if doNotifyForSoonComing:
                    msg = "TRAIN %s IS COMING NOW! Waiting for Arrival" % (id,)
                    bot.send_message(chat_id=update.message.chat_id, text=msg)
                    doNotifyForSoonComing = False
                time.sleep(2)
                # continues outer while loop
            else:  # abfahrt is none
                # time sleep until 4am, when first train is arriving
                msg = "No ETA available for Saarlandstraße. Sleep until 4am"
                bot.send_message(chat_id=update.message.chat_id, text=msg)
                # sleep until 4am
                now = datetime.now()
                later = datetime.strptime('04:00:00', '%H:%M:%S')
                time.sleep((later-now).seconds)
                # time.sleep(5)
                # bot.send_message(chat_id=update.message.chat_id, text="%s, %s, %s"%(isComing,abfahrt,id))


        except requests.exceptions.RequestException as e:
            logging.error('%s' % e)
            bot.send_message(chat_id=update.message.chat_id, text='RequestException:%s' % e)
            print('%s' % e)
    print('end watch')
    bot.send_message(chat_id=update.message.chat_id, text='end /watch')




if __name__ == '__main__':
    api_key = read_api_key()

    bot = telegram.Bot(token=api_key)
    print(bot.get_me())
    updater = Updater(token=api_key)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(CommandHandler('watch', watch))

    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)

    updater.start_polling()

    # ipdb.set_trace()

