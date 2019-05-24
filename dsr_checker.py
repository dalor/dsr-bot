from threading import Thread
import requests
import time
import re
from io import BytesIO
import base64

class DSRChecker(Thread):
    def __init__(self, bot, chat_id, chat_url):
        Thread.__init__(self)
        self.bot = bot
        self.chat_ids = [chat_id]
        self.chat_url = chat_url[:-2] if chat_url[-1] == '/' else chat_url
        self.s = requests.Session()
        self.token = None
        self.last_id = 0
        self.count = 5000
        self.is_run = True
        self.sleep_time = 0.3
        self.my_messages = []
        self.auth()

    def auth(self):
        res = self.s.get(self.chat_url + '/joinUser').json()
        if res['ok']:
            self.token = res['result'][0]['content']

    def check_photo(self, text):
        return re.match('data:image/[^;]+;base64[^"]+', text)


    def run(self):
        while self.is_run:
            try:
                messages = self.s.get(self.chat_url + '/getAll', params={'from': self.last_id + 1, 'to': self.last_id + self.count}).json()
                for mess in messages:
                    if mess['id'] > self.last_id:
                        #if not mess['content'] in self.my_messages:
                        if not self.check_photo(mess['content']):
                            send_urls = [self.bot.msg(mess['content'], chat_id=chat_id) for chat_id in self.chat_ids]
                        else:
                            photo = BytesIO(base64.b64decode(mess['content']))
                            send_urls = [self.bot.photo(photo, chat_id=chat_id) for chat_id in self.chat_ids]
                        self.bot.more(send_urls)
                        #else:
                            #self.my_messages.remove(mess['content'])
                if messages:
                    self.last_id = messages[-1]['id']
            except:
                pass
            time.sleep(self.sleep_time)

    def sendMessage(self, text, chat_id, message_id):
        result  = self.s.get(self.chat_url + '/sendmessage', params={'content': text}).json()
        print(result)
        if result['ok']:
            self.my_messages.append(text)
            res = self.bot.msg('Sended', chat_id=chat_id, reply_to_message_id=message_id).send()
            time.sleep(1)
            self.bot.delete(chat_id=chat_id, message_id=res['result']['message_id']).send()
            self.bot.more([self.bot.delete(chat_id=chat_id, message_id=message_id),
                           self.bot.delete(chat_id=chat_id, message_id=res['result']['message_id'])])
        else:
            res = self.bot.msg('ERROR: ' + result['result'][0]['content'], chat_id=chat_id, reply_to_message_id=message_id).send()
            #time.sleep(1)
            #self.bot.delete(chat_id=chat_id, message_id=res['result']['message_id']).send()

    def stop(self):
        self.is_run = False


