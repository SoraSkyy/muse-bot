import datetime
import time
import pickle
from Pastebin import PastebinAPI
import json
import urllib.request
import urllib.parse
import usertimes


class Logger():
    def __init__(self,dpl):
        self.lpl = 'D:\Documents\muse-bot\logs.pickle'
        self.logstxt = 'D:\Documents\muse-bot\logs.txt'
        self.pastebin = PastebinAPI()
        self.dpl = dpl
    def log(self, dict):
        dict['time'] = datetime.datetime.utcnow()
        f = open(self.lpl, 'rb')
        data = pickle.load(f)
        f.close()
        if not dict['channel'] == None and not dict['private_messaged'] == True:
            data[dict['channel']].append(dict)
            f = open(self.lpl, 'wb')
            pickle.dump(data, f)
            f.close()
    def read(self, dict):
        a = usertimes.TimeZoneCheck()
        tz = a.get_raw_timezone(self.dpl,dict['name'].lower())
        if tz == None:
            return
        f = open(self.lpl, 'rb')
        data = pickle.load(f)
        f.close()
        f = open(self.logstxt, 'wb')
        for a in data['#nanodesu']:
            f.write(self.display_time(a['time'],tz).encode())
            if a['type'] == 'PRIVMSG':
                f.write(('%s|%s\r\n' %(self.display_name(a['name']), a['message'])).encode())
            elif a['type'] == 'JOIN':
                f.write(('%s%s has joined the channel.\r\n' %(self.display_name(None), a['name'])).encode())
            elif a['type'] == 'PART':
                f.write(('%s%s has parted from the channel.\r\n' %(self.display_name(None), a['name'])).encode())
            elif a['type'] == 'QUIT':
                f.write(('%s%s has left the channel.\r\n' %(self.display_name(None), a['name'])).encode())
            elif a['type'] == 'NICK':
                f.write(('%s%s has changed his nick to %s.\r\n' %(self.display_name(None), a['name'],a['message'])).encode())
        f.close()
        f = open('D:\Documents\muse-bot\logs.txt', 'r')
        a = {'key':'808f1be384f08c1d10806809193fe66b','description':'test', 'paste':f.read()}
        json.dumps(a)
        url = 'https://paste.ee/api'
        b = urllib.parse.urlencode(a).encode('utf-8')
        f.close()
        try:
            request = urllib.request.urlopen(url, b)
        except http.client.HTTPException as e:
            print(e)
        response = request.read().decode()
        dict['message'] = json.loads(response)['paste']['link']
        return dict
        '''
        f = open(self.logstxt, 'r')
        a = self.pastebin.paste('2333bedc76cd701be6a8526402393da6',f.read(),api_user_key=self.pastebin.generate_user_key('2333bedc76cd701be6a8526402393da6','SoraSky','123456'),paste_private = 'public')
        f.close()
        return a
        '''
    def clear(self):
        f = open(self.lpl, 'wb')
        data = {'#nanodesu':[]}
        pickle.dump(data,f)
        f.close()

    def display_time(self,time,tz):
        time += datetime.timedelta(hours=tz)
        if time.hour < 10:
            hour_zero = str(0)
        else:
            hour_zero = ''
        if time.minute < 10:
            minute_zero = str(0)
        else:
            minute_zero = ''
        return '[%s%d:%s%d]' %(hour_zero, time.hour, minute_zero, time.minute)
    def display_name(self, name):
        if name == None:    #for channel parts, quits, joins, etc
            return (' ' * 12)+'|'
        space = ''
        if len(name) < 12:
            space = ' ' * (12 - len(name))
        if len(name) > 12:
            name = name[:12]
        return space + name
