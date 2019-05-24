from dtelbot.oop import Bot
from dtelbot.inline_keyboard import button, markup
from dtelbot.inline import article

from dsr_checker import DSRChecker

import os

BOT_ID = os.environ['BOT_ID']


app = Flask(__name__)

def stop_checker(a):
    checker = a.session.get('checker')
    if checker:
        if checker.is_run:
            checker.stop()
            a.msg('Message handler was stopped').send()

chats = {}

class Core:
    b = Bot(BOT_ID)
    message = b.message
    callback = b.callback_query

    @message('/start')
    def start(self, a):
        a.msg('Send me url of chat').send()

    @message('(https?:\/\/[^\/]+).*\/chat\/([^\/]+)')
    def joinChat(self, a):
        #stop_checker(a)
        checker = chats.get(a.args[2])
        if not checker:
            checker = DSRChecker(a.bot, a.chat_id, a.args[1] + '/api/chat/' + a.args[2])
            if checker.token:
                chats[a.args[2]] = checker
                checker.start()
            else:
                a.msg('You can`t connect this chat').send()
                return
        else:
            checker.chat_ids.append(a.chat_id)
        a.session['checker'] = checker
        a.msg('Connected to chat \'{}\''.format(a.args[2])).send()
            

    @message('/stop')
    def stop(self, a):
        stop_checker(a)

    @message('(.+)')
    def send(self, a):
        checker = a.session.get('checker')
        if checker:
            try:
                checker.sendMessage(a.args[1], a.chat_id, a.data['message_id'])
            except:
                stop_checker(a)

c = Core()

@app.route('/{}'.format(BOT_ID), methods=['POST']) #Telegram should be connected to this hook
def webhook():
    c.b.check(request.get_json())
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
