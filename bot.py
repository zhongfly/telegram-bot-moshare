# encoding:UTF-8
# python3.6
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from postman import islogin, pre_login, login, post_news, dailybonus, get_news, load_cookies
import logging
import re
import time
import os
import requests
from functools import wraps

token = 'xxxxxx'#填入bot的token
admin = [12345678]#填入具有操作权限tg账户的id（通过@getidsbot）
updater = Updater(token, request_kwargs={
    'proxy_url': 'socks5://127.0.0.1:1080/'
})#设置代理
s = requests.Session()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

if os.path.exists('cookie.txt'):
    load_cookies(session=s)
else:
    pass

GETURL, CONFIRM, GETANSWER, news = range(4)


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in admin:
            update.message.reply_text('你没有操作BOT的权限', quote=True)
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


@restricted
def start_handler(bot, update):
    chat_id = update.message.chat_id
    bot.sendMessage(text="/islogin 检查是否登录\n/login 登录\n/dailybonus 每日打卡\n/post 发帖",
                    chat_id=chat_id)


@restricted
def islogin_handler(bot, update):
    chat_id = update.message.chat_id
    result = islogin(s)
    logger.info('检查登录状态，结果为“{}”'.format(result))
    update.message.reply_text(result, quote=True)


@restricted
def dailybonus_handler(bot, update):
    chat_id = update.message.chat_id
    result = dailybonus(s)
    logger.info('每日打卡，结果为“{}”'.format(result))
    update.message.reply_text(result, quote=True)


def post_timeout(bot, job):
    bot.editMessageText(
        chat_id=job.context[0], message_id=job.context[1], text='已结束等待')
    return post_handler.END


@restricted
def post_start(bot, update, job_queue):
    chat_id = update.message.chat_id
    logger.info('开始发帖流程')
    msg = update.message.reply_text('等待输入网址。。。\n/cancel 取消', quote=True)
    global j
    j = job_queue.run_once(post_timeout, 30, context=(chat_id, msg.message_id))
    return GETURL


@restricted
def geturl(bot, update):
    j.schedule_removal()
    text = update.message.text
    chat_id = update.message.chat_id
    logger.info("收到链接{}，进行分析".format(text))
    global news
    news = get_news(text)
    if news != 0:
        confirm_btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='确认', callback_data='ok'),
             InlineKeyboardButton(text='取消', callback_data='cancel')]
        ])
        msg = update.message.reply_text(
            news['title'], quote=True, reply_markup=confirm_btn)
        logger.info("链接分析结果：“{}”".format(news['title']))
        return CONFIRM
    else:
        logger.info('链接无法识别')
        update.message.reply_text('链接无法识别,请重试', quote=True)
        return GETURL


@restricted
def confirm_callback(bot, update):
    query = update.callback_query
    if query.data == 'ok':
        result = post_news(news,s)
        logger.info("执行发帖操作，标题为“{}”，结果为：【{}】".format(news['title'], result))
        bot.sendMessage(text=result, chat_id=query.message.chat_id)
    else:
        logger.info("确认未通过，取消发帖操作。")
        bot.sendMessage(text='已取消操作', chat_id=query.message.chat_id)
        my_news = None
    logger.info("结束会话。")
    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    news = None
    logger.info("取消操作，结束会话。", user.first_name)
    update.message.reply_text('已取消', quote=True)
    return ConversationHandler.END


post_handler = ConversationHandler(
    entry_points=[CommandHandler('post', post_start, pass_job_queue=True)],

    states={
        GETURL: [MessageHandler(Filters.text, geturl)],
        CONFIRM: [CallbackQueryHandler(confirm_callback)],
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    allow_reentry=True,
    conversation_timeout=30,
)


def login_start(bot, update):
    chat_id = update.message.chat_id
    if islogin(s) == '已登录':
        update.message.reply_text('已经登录，请勿重复登录', quote=True)
        return ConversationHandler.END
    else:
        pass
    pre_login(s, openimg=False)
    bot.send_photo(chat_id=chat_id, photo=open('capt.png', 'rb'),
                   reply_to_message_id=update.message.message_id)
    return GETANSWER


def getanswer(bot, update):
    answer = update.message.text
    msg = update.message.reply_text('正在登录ing', quote=True)
    result = login(answer,s)
    bot.editMessageText(
        chat_id=update.message.chat_id, message_id=msg.message_id, text=result)
    return ConversationHandler.END


login_handler = ConversationHandler(
    entry_points=[CommandHandler('login', login_start)],

    states={
        GETANSWER: [MessageHandler(Filters.text, getanswer)],
    },

    fallbacks=[CommandHandler('cancel', cancel)],

    allow_reentry=True,

    conversation_timeout=30,
)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


updater.dispatcher.add_handler(CommandHandler('start', start_handler))
updater.dispatcher.add_handler(CommandHandler('islogin', islogin_handler))
updater.dispatcher.add_handler(
    CommandHandler('dailybonus', dailybonus_handler))
updater.dispatcher.add_handler(post_handler)
updater.dispatcher.add_handler(login_handler)
updater.dispatcher.add_error_handler(error)

updater.start_polling()
updater.idle()
