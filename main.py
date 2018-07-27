import threading
import time
import requests
import json
import pathlib
import lxml.html
import random
import os
import captcha
import bs4
import sys

temp_dir = '/home/username/.phantomvk-work-dir/temp/'
main_dir = '/home/username/.phantomvk-work-dir/main/'

path_to_new_proxies  = main_dir + 'newproxies.txt'
path_to_new_accounts = main_dir +'new.txt'

path_to_config_file   = main_dir + 'config.json'
path_to_closed_groups = main_dir + 'closed.txt'
path_to_open_groups   = main_dir + 'open.txt'
path_to_promolinks    = main_dir + 'promolinks.txt'
path_to_photos        = main_dir + 'photos/'
path_to_avatars       = main_dir + 'avatars/'
path_to_promophotos   = main_dir + 'promophotos/'
path_to_accounts_json = main_dir + 'accounts.json'


path_to_proxies          = temp_dir +'proxies.txt'
path_to_error_proxies    = temp_dir +'errorproxies.txt'
path_to_error_accounts   = temp_dir +'erroraccounts.txt'
path_to_blocked_accounts = temp_dir +'bannedaccounts.txt'
path_to_accounts         = temp_dir +'accounts.txt'


# to do
# create function to leave all
# pubs and groups with closed
# comments and where account
# is in ban

# also
# create a function to unpin
# pinned post, if there is pinned post
# on the user wall

config = json.loads(pathlib.Path(path_to_config_file).read_text(encoding='utf-8'))
headers = config['headers']
posts = config['posts']
message = config['message']
public_names = config['public_names']
sids = config['sids']
comms = config['comms']

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Add_new ():
    def __init__(self):
        self.new_accounts = []
        self.new_proxies = []

        des = input(bcolors.WARNING + 'do you want to add new accounts? (y/n) \n» ')

        if des == 'y':
            self.add_accounts()

        elif des == 'n':
            print('ok')

        else:
            print('wrong choice')

        des = input(bcolors.WARNING + 'do you want to add new proxies? (y/n) \n» ')

        if des == 'y':
            self.add_proxies()

        elif des == 'n':
            print('ok')

    def add_accounts(self):
        print('seraching in {}'.format(path_to_new_accounts))

        with open(path_to_new_accounts, 'r') as file:
            for line in file:
                if len(line) > 2:
                    self.new_accounts.append(line.strip())

        print('{} accounts found'.format(len(self.new_accounts)))

        with open(path_to_accounts, 'a') as file:
            for account in self.new_accounts:
                file.write(account + '\n')

        delete = input(bcolors.WARNING + 'do you want to delete all accounts from temp file? \
                      (y/n) \n» ')

        if delete == 'y':
            with open(path_to_new_accounts, 'w') as file:
                pass

        else:
            print('ok')

    def add_proxies(self):
        print('searching in {}'.format(path_to_new_proxies))

        with open(path_to_new_proxies, 'r') as file:
            for line in file:
                if len(line) > 2:
                    if '@' not in line:
                        oneproxy = '{}:{}@{}:{}'.format(line.strip().split(':')[2],
                                                        line.strip().split(':')[
                            3], line.strip().split(':')[0],
                            line.strip().split(':')[1])

                    else:
                        oneproxy = line.strip()

                    self.new_proxies.append(oneproxy)
                    self.new_proxies.append(oneproxy)

        print('{} proxies found'.format(len(self.new_proxies)))

        with open(path_to_proxies, 'a') as file:
            for proxy in self.new_proxies:
                file.write(proxy + '\n')

        delete = input(bcolors.WARNING + 'do you want to delete all proxies from temp file (y/n) \n» ')

        if delete == 'y':
            with open(path_to_new_proxies, 'w') as file:
                pass

        else:
            print('ok')


class Prepare_all ():
    def __init__(self):
        self.accounts = []
        self.allproxies = []

        with open(path_to_accounts, 'r') as file:
            for line in file:
                self.accounts.append(line.strip())

        with open(path_to_proxies, 'r') as file:
            for line in file:
                if self.proxy_check(line.strip()) == '1':
                    self.allproxies.append(line.strip())

                else:
                    with open(path_to_error_proxies, 'a') as file:
                        print('proxy {} doesnt working'.format(line.strip()))
                        file.write(line.strip())

        print('total proxies count: {}'.format(len(self.allproxies)))
        print('total accounts count: {}'.format(len(self.accounts)))

        if len(self.accounts) > len(self.allproxies):
            print('error: proxies is not enough')

        else:
            for i in range(len(self.accounts)):
                login = self.accounts[i].split(':')[0]
                paswd = self.accounts[i].split(':')[1]
                proxy = self.allproxies[i]

                proxies = {
                    'http': 'http://{}'.format(proxy),
                    'https': 'https://{}'.format(proxy)}

                s = requests.session()

                access_token = self.get_access_token(s, login, paswd, proxies, headers)

                if 'blocked' in access_token:
                    print('error: account is blocked')

                    with open(path_to_blocked_accounts, 'a') as file:
                        file.write(accounts[i] + '\n')

                elif access_token == 'https://m.vk.com/':
                    print('error: can\'t get access token, try to use another proxy')

                    with open(path_to_error_accounts, 'a') as file:
                        file.write(accounts[i] + '\n')

                else:
                    print('done: access token successfully recieved')

                    uid = s.get('https://api.vk.com/method/users.get', params={
                        'access_token': access_token, 'v': '5.80'}, proxies=proxies).json()['response'][0]['id']
                    name = s.get('https://api.vk.com/method/users.get', params={
                        'access_token': access_token, 'v': '5.80'}, proxies=proxies).json()['response'][0]['first_name']
                    status = '0'

                    self.write_json(uid, name, login, paswd, proxy, status, access_token)

                    self.get_free_stickers(s, proxies, headers)
                    self.avatar_post(s, access_token, proxies)
                    self.repost(s, access_token, proxies, posts)
                    self.set_privacy(s, access_token, proxies)

                    print('done: account is almost ready')

            with open(path_to_proxies, 'w') as file:
                for proxy in self.allproxies[i+1:]:
                    file.write(proxy + '\n')

            with open(path_to_accounts, 'w') as file:
                pass

    def proxy_check(self, proxy):
        proxies = {'http': 'http://{}'.format(proxy),
                           'https': 'https://{}'.format(proxy)}

        try:
            requests.get('https://m.vk.com/login', proxies=proxies, timeout=5)
            return '1'

        except:
            return '0'

    def get_access_token(self, s, login, paswd, proxies, headers):
        login_page = s.get('https://m.vk.com/login', proxies=proxies, headers=headers)

        parsed_login_page = lxml.html.fromstring(login_page.content)
        form = parsed_login_page.forms[0]

        form.fields['email'] = login
        form.fields['pass'] = paswd

        auth = s.post(form.action, data=form.form_values(), proxies=proxies, headers=headers)

        params = {
            'client_id': '4083558',
            'scope': 'friends,photos,audio,video,docs,notes,pages,status,offers,questions,wall,groups,messages,notifications,stats,ads,market,offline',
            'redirect_uri': 'https://api.vk.com/blank.html',
            'display': 'wap',
            'v': '5.80',
            'response_type': 'token',
            'revoke': 0
        }

        data = s.get('https://oauth.vk.com/authorize',
                     params=params, proxies=proxies, headers=headers)

        try:
            toked = lxml.html.fromstring(data.content)
            form = toked.forms[0]

            data = s.post(form.action, proxies=proxies)
        except:
            pass

        try:
            access_token = data.url.split('access_token=')[1].split('&expires')[0]

        except:
            access_token = data.url

        return access_token

    def write_json(self, uid, name, login, paswd, proxy, status, access_token):
        newobject = {
            "id": uid,
            "link": 'https://vk.com/id{}'.format(uid),
            "name": name,
            "login": login,
            "pass": paswd,
            "proxy": proxy,
            "status": status,
            "access_token": access_token}

        myjson = json.loads(pathlib.Path(path_to_accounts_json).read_text(encoding='utf-8'))

        myjson['almost_ready'].append(newobject)

        with open(path_to_accounts_json, 'w') as file:
            json.dump(myjson, file, indent=2, ensure_ascii=False)

    def avatar_post(self, s, access_token, proxies):
        files = {'file': open(path_to_avatars + random.choice(os.listdir(path_to_avatars)), 'rb')}

        params = s.post(s.get('https://api.vk.com/method/photos.getOwnerPhotoUploadServer', params={
            'access_token': access_token, 'version': '5.80'}, proxies=proxies).json()['response']['upload_url'], files=files, proxies=proxies).json()

        params.update({'version': '5.80', 'access_token': access_token})

        print(s.get('https://api.vk.com/method/photos.saveOwnerPhoto',
                    params=params, proxies=proxies).json())

    def repost(self, s, access_token, proxies, posts):
        random.shuffle(posts)

        for post in posts:

            params = {
                'access_token': access_token,
                'version': '5.80',
                'object': post
            }

            resp = s.get('https://api.vk.com/method/wall.repost',
                         params=params, proxies=proxies).json()

            try:
                print(resp['response'])

            except:
                print(resp)

            time.sleep(2)

    def set_privacy(self, s, access_token, proxies):
        keys = ['mail_send', 'status_replies', 'groups']

        for key in keys:
            params = {'access_token': access_token,
                      'v': '5.80',
                      'key': key,
                      'value': 'nobody'}

            print(s.get('https://api.vk.com/method/account.setPrivacy',
                        params=params, proxies=proxies).json())

    def get_free_stickers(self, s, proxies, headers):
        # try to get stickers
        stickerLinks = [
            'https://m.vk.com/stickers?stickers_id=1&tab=free',
            'https://m.vk.com/stickers?stickers_id=2&tab=free',
            'https://m.vk.com/stickers?stickers_id=4&tab=free',
            'https://m.vk.com/stickers?stickers_id=75&tab=free',
            'https://m.vk.com/stickers?stickers_id=108&tab=free',
            'https://m.vk.com/stickers?stickers_id=139&tab=free',
            'https://m.vk.com/stickers?stickers_id=148&tab=free']

        for url in stickerLinks:
            data = s.get(url, proxies=proxies, headers=headers)

            try:
                soup = bs4.BeautifulSoup(data.content, 'html.parser')
                q = soup.find('a', class_="button wide_button sp_buy_str").get('href')

                s.get('https://m.vk.com/' + str(q), proxies=proxies, headers=headers)

            except:
                print('error while stickers getting')


def clean():
    def unpin ():
        packs = json.loads (pathlib.Path (path_to_accounts_json).read_text (encofing='utf-8'))['packs']
        for pack in packs:
            for account in pack:
                access_token = account['access_token']
                proxy = account['proxy']

                proxies = {'http':'http://{}'.format (proxy), 'https': 'https://{}'.format (proxy)}

                params = {'access_token':access_token, 'v': '5.80', 'count': '1'}
                q = requests.get ('https://api.vk.com/method/wall.get', params=params, proxies=proxies).json()['response']['items'][0]
                
                try:
                    if q['is_pinned'] == 1:
                        print (pinned)

                except:
                    print ('its ok')


    def clean_banned ():
        packs = json.loads (pathlib.Path (path_to_accounts_json).read_text(encoding='utf-8'))
        new_packs = []
        banned = []

        for pack in packs['packs']:
            new_pack = []

            for account in pack:
                params = {'access_token': account['access_token'], 
                          'v': '5.80',
                          'count': '1'}

                proxies = {'http': 'http://{}'.format (account['proxy']), 
                           'https': 'https://{}'.format (account['proxy'])}

                check = requests.get ('https://api.vk.com/method/wall.get',
                                  params=params, proxies=proxies).json ()

                if 'error' in check:
                    if check['error']['error_code'] == 5:
                        banned.append (account)

                    else:
                        new_pack.append (account)

                else:
                    new_pack.append (account)

            new_packs.append (new_pack)
            banned += packs['banned']

        myjson = {'packs': new_packs, 'almost_ready': packs['almost_ready'], 'banned': banned}

        with open (path_to_accounts_json, 'w') as file:
            json.dump (myjson, file, indent=2, ensure_ascii=False)
    delete = input(bcolors.WARNING + 'do you want to delete all almost ready accounts? (y/n)\n» ')

    if delete == 'y':
        print('deleting all accounts in "almost ready" section')

        myjson = json.loads(pathlib.Path(path_to_accounts_json).read_text(encoding='utf-8'))

        newobject = {'packs': myjson['packs'],
                     'almost_ready': [],
                     'banned': myjson['banned']}

        with open(path_to_accounts_json, 'w') as file:
            json.dump(newobject, file, indent=2, ensure_ascii=False)

    else:
        print('ok')

    delete = input(bcolors.WARNING + 'do you want to check and delete all banned accounts from packs? (y/n) \n» ')

    if delete == 'y':
        print ('checking and deleting all banned accounts in the packs')

        clean_banned ()

        print ('banned accounts deleted')






def join_pubs(access_token, proxy):
    global dead

    closed_pubs = []
    open_pubs = []

    with open(path_to_closed_groups, 'r') as file:
        for line in file:
            closed_pubs.append(line.strip())

    with open(path_to_open_groups, 'r') as file:
        for line in file:
            open_pubs.append(line.strip())

    random.shuffle(closed_pubs)
    random.shuffle(open_pubs)

    base = closed_pubs[0:18] + open_pubs[0:75]
    random.shuffle(base)

    s = requests.session()

    proxies = {'http': 'http://{}'.format(proxy), 'https': 'https://{}'.format(proxy)}

    for pub in base:
        joinparams = {
            'access_token': access_token,
            'version': '5.80',
            'group_id': pub}

        if dead == False:
            try:
                result = s.get('https://api.vk.com/method/groups.join',
                               params=joinparams, proxies=proxies).json()

            except:
                sleep(4)

            if 'error' in result:
                if result['error']['error_code'] == 14:
                    print('error: captcha needed')

                    capkey = captcha.main(result['error']['captcha_img'])

                    joincaptchaparams = {
                        'access_token': access_token,
                        'version': '5.80',
                        'group_id': line.strip(),
                        'captcha_sid': result['error']['captcha_sid'],
                        'captcha_key': capkey}

                    s.get('https://api.vk.com/method/groups.join',
                          params=joincaptchaparams, proxies=proxies).json()

            time.sleep(random.randint(7, 20))

        else:
            return


class By_packs ():
    def __init__(self):
        path0 = pathlib.Path(path_to_accounts_json).read_text(encoding='utf-8')
        self.accounts = json.loads(path0)['almost_ready']

        if len(self.accounts) % 5 != 0:
            pack_count = int(len(self.accounts) // 5 + 1)

        else:
            pack_count = int(len(self.accounts) / 5)

        input('there must be {} links in the promolinks file (press ENTER)'.format(pack_count))

        self.promolinks = []
        with open(path_to_promolinks, 'r') as file:
            for line in file:
                self.promolinks.append(line.strip())

        if len(self.promolinks) < pack_count:
            print('there is not enough links in promolinks file, please try again after putting them')
            inlink = input(bcolors.WARNING + 'do you want to manually input promolinks? (y/n)\n» ')
            if inlink == 'y':
                print('this function is not ready right now, sorry')

            else:
                print('ok')

        else:
            for i in range(pack_count):
                pack_json = []
                pack = self.accounts[i*5: (i + 1)*5]
                promolink = self.promolinks[i]

                postmessage = message.split(
                    '//promolink//')[0] + promolink + message.split('//promolink//')[1]

                # main account in pack
                access_token = pack[0]['access_token']

                proxies = {'http': 'http://{}'.format(pack[0]['proxy']),
                           'https': 'https://{}'.format(pack[0]['proxy'])}

                promopost = self.promopost(access_token, proxies, postmessage, promolink)

                for pack_account in pack:
                    access_token = pack_account['access_token']
                    proxy = pack_account['proxy']

                    pack_account_proxies = {'http': 'http://{}'.format(pack_account['proxy']),
                                            'https': 'https://{}'.format(pack_account['proxy'])}

                    self.repost (access_token, proxies, promopost)
                    pack_json.append (pack_account)

                self.write_packs_to_json (pack_json, promopost)
                print ('done: created pack num {}'.format (i))

    def write_packs_to_json (self, pack_json, promopost):
        for pack_account in pack_json:
            pack_account['status'] = '1'
            pack_account.update({'promopost': promopost})

        accounts_json_path = pathlib.Path (path_to_accounts_json).read_text (encoding='utf-8')
        myjson = json.loads (accounts_json_path)

        myjson['packs'].append (pack_json)

        with open (path_to_accounts_json, 'w') as file:
            json.dump (myjson, file, indent=2, ensure_ascii=False)



    def main(self):

            prepare_functions.repost(access_token, proxies, [promopost])

            write_json(acc, promopost)

    def repost (self, access_token, pack_account_proxies, post):
        params = {'access_token': access_token,
                  'version': '5.80',
                  'object': post}

        resp = requests.get('https://api.vk.com/method/wall.repost',
                     params=params, proxies=pack_account_proxies).json()

        if 'error' not in resp:
            print ('promopost reposted')

        else:
            print ('error while promopost reposting')
            print (resp)


    def promopost(self, access_token, proxies, postmessage, promolink):
        public_name = random.choice (public_names)
        create_pub_params = {
            'title': public_name,
            'type': 'public',
            'public_category': 1,
            'subtype': 1,
            'version': '5.80',
            'access_token': access_token
        }

        s = requests.session()

        createpubanswer = s.get('https://api.vk.com/method/groups.create',
                                params=create_pub_params, proxies=proxies).json()

        if 'error' in createpubanswer:

            # if captcha
            if createpubanswer['error']['error_code'] == 14:

                print('captcha needed')

                capkey = captcha.main(createpubanswer['error']['captcha_img'])
                create_pub_params.update({
                    'captcha_sid': createpubanswer['error']['captcha_sid'],
                    'captcha_key': capkey})


                createpubanswer = s.get('https://api.vk.com/method/groups.create',
                                        params=create_pub_params,
                                        proxies=proxies).json()

            else:
                print('unknown error')
                print(createpubanswer)

        pubid = createpubanswer['response']['gid']
        print('pub created, link: https://vk.com/club{}'.format(pubid))

        editpubparams = {'contacts': 0,
                         'wall': 0,
                         'audio': 0,
                         'video': 3,
                         'photos': 0,
                         'topics': 0,
                         'group_id': pubid,
                         'access_token': access_token,
                         'version': '5.80'}

        s.get('https://api.vk.com/method/groups.edit', params=editpubparams, proxies=proxies).json()
        print('pub is edited')

        pubavatargeturlparams = {'owner_id': -pubid,
                                 'access_token': access_token,
                                 'version': '5.80'}

        url = s.get('https://api.vk.com/method/photos.getOwnerPhotoUploadServer',
                    params=pubavatargeturlparams,
                    proxies=proxies).json()['response']['upload_url']

        files = {'file': open(path_to_photos + random.choice(os.listdir(path_to_photos)), 'rb')}
        q1 = s.post(url, files=files).json()
        q1.update({'version': '5.80', 'access_token': access_token})

        print (s.get('https://api.vk.com/method/photos.saveOwnerPhoto',
              params=q1, proxies=proxies).json())

        print('group is prepared')

        for i in range(0, 2):
            url = s.get('https://api.vk.com/method/photos.getWallUploadServer',
                        params={'access_token': access_token,
                                'version': '5.80',
                                'group_id': pubid},
                        proxies=proxies).json()['response']['upload_url']

            files = {'file': open(path_to_photos + random.choice(os.listdir(path_to_photos)), 'rb')}
            photoload = s.post(url, files=files, proxies=proxies).json()

            wallsaveparams = {'access_token': access_token,
                              'version': '5.80',
                              'group_id': pubid,
                              'photo': photoload['photo'],
                              'server': photoload['server'],
                              'hash': photoload['hash']}

            photo = s.get('https://api.vk.com/method/photos.saveWallPhoto',
                          params=wallsaveparams, proxies=proxies).json()['response'][0]['id']

            postparams = {'owner_id': -pubid,
                          'access_token': access_token,
                          'version': '5.80',
                          'attachments': photo}

            answertopost = s.post('https://api.vk.com/method/wall.post',
                                  params=postparams, proxies=proxies).json()

            if 'error' not in answertopost:
                print('post in the group is posted')

            else:
                print('error while posting in the group')

        # promopost posting
        s.get('https://api.vk.com/method/photos.getWallUploadServer',
                    params={'access_token': access_token,
                            'version': '5.80',
                            'group_id': pubid},
                    proxies=proxies).json()

        url = s.get('https://api.vk.com/method/photos.getWallUploadServer',
                    params={'access_token': access_token,
                            'version': '5.80',
                            'group_id': pubid},
                    proxies=proxies).json()['response']['upload_url']

        files = {'file': open(path_to_promophotos +
                              random.choice(os.listdir(path_to_promophotos)), 'rb')}
        photoload = s.post(url, files=files, proxies=proxies).json()

        wallsaveparams = {'access_token': access_token,
                          'version': '5.80',
                          'group_id': pubid,
                          'photo': photoload['photo'],
                          'server': photoload['server'],
                          'hash': photoload['hash']}

        photo = s.get('https://api.vk.com/method/photos.saveWallPhoto',
                      params=wallsaveparams, proxies=proxies).json()['response'][0]['id']

        postparams = {'owner_id': -pubid,
                      'message': postmessage,
                      'access_token': access_token,
                      'version': '5.80',
                      'attachments': photo + ',' + promolink}

        answertopromo = s.post('https://api.vk.com/method/wall.post',
                               params=postparams, proxies=proxies).json()


        try:
            post_id = answertopromo['response']['post_id']
            print('promopost added')
            return 'wall-{}_{}'.format(pubid, post_id)

        except:
            print('REALLY BIG ERROR WHILE PROMO POST ADDING AAAAAAA')


def prepare_questions():
    join_prompt = '┌───────┬───────────────────┐\n' + '├   s   ├   show stats      ┤\n' + \
                  '├   q   ├   exit joining    ┤\n' + '├ clear ├  clear screen     ┤\n' + \
                  '└───────┴───────────────────┘'

    accounts = json.loads(pathlib.Path(path_to_accounts_json).read_text(
        encoding='utf-8'))['almost_ready']

    def show_stat():
        stat = '┌ pub joining stats\n'
        for account in accounts:
            uid = account['id']

            proxies = {'http': 'http://{}'.format(account['proxy']),
                               'https': 'https://{}'.format(account['proxy'])}

            q = requests.get('https://api.vk.com/method/groups.get',
                             params={'access_token': account['access_token'],
                                     'version': '5.80',
                                     'extended': 1}, proxies=proxies).json()

            if 'error' in q:
                status = 'banned'
                views = 'None'

            else:
                status = 'active'
                try:
                    pub_count = q['response'][0]

                except:
                    pub_count = 'None'

            stat += '├ id: {} │ status: {} │ groups count: {}\n'.format(uid, status, pub_count)

        print(stat)

    global dead
    dead = False
    prep = input(bcolors.WARNING + 'do you want to start preparing actions with all accounts in {}? (y/n)\n» '.format(path_to_accounts))

    if prep == 'y':
        act0 = Prepare_all()

    else:
        print('ok')

    prep = input(bcolors.WARNING + 'do you want to start joining pubs with all accounts in almost ready section in "accounts.json"? (y/n)\n» ')

    if prep == 'y':

        for account in accounts:
            # join_pubs (account)
            proxy = account['proxy']
            access_token = account['access_token']
            threading.Thread(target=join_pubs, args=(access_token, proxy)).start()

        while not dead:
            print (join_prompt)
            stop = input(bcolors.OKBLUE + 'join pubs »  ')

            if stop == 'q':
                dead = True

            elif stop == 's':
                show_stat()

            elif stop == 'clear':
                os.system ('clear')

    prep = input(bcolors.WARNING + 'do you want to start creating packs? (y/n)\n» ')

    if prep == 'y':
        print('start creating packs')
        By_packs()


def action (access_token, proxies):
    global action_dead

    def getfeed (a, s, count=10):
        feedparams = {
            'access_token': a [0],
            'version'     : '5.78',
            'filters'     : 'post',
            'count'       : count
        }

        feed = s.get ('https://api.vk.com/method/newsfeed.get', 
            params=feedparams, proxies=a [1]).json () ['response']['items']

        return feed

    def createcomment (a, s, p, m):
        params = {'access_token': a [0],
                  'version'     : '5.78',
                  'owner_id'    : p [0],
                  'post_id'     : p [1],
                  'message'     : m [0],
                  'sticker_id'  : m [1]}

        z = s.get ('https://api.vk.com/method/wall.createComment', 
            params=params, proxies=a [1])

        if 'error' in z.json ():
            if z.json () ['error']['error_code'] == 14:
                print ('error: captcha needed')

                capkey = captcha.main (z.json () ['error']['captcha_img'])
                params.update ({'captcha_sid': z.json () ['error']['captcha_sid'], 
                    'captcha_key': capkey})

                z = s.get ('https://api.vk.com/method/wall.createComment', params=params, proxies=a [1])

            elif z.json () ['error']['error_code'] == 213:
                print ('error: banned in the group, leaving it')

                params = {'group_id'    : -p [0], 
                          'access_token': a [0],
                          'version'     : '5.80'}

                print (s.get ('https://api.vk.com/method/groups.leave', params=params, proxies=a [1]).json ())

        print (z.json ())

    s = requests.session ()
    a = [access_token, proxies]

    # while not action_dead:
    while True:
        if action_dead == True:
            return

        else:
            feed = getfeed (a, s)

            for item in feed:
                if action_dead == False:
                    p = [item ['source_id'], item ['post_id']]
                    m = random.choice ([[None, random.choice (range (sids [0], sids [1]))], 
                        [random.choice (comms), None]])

                    createcomment (a, s, p, m)

                    time.sleep (random.randint (30, 90))
                    # time.sleep (2)

        if action_dead == False:
            time.sleep (250)


def show_pack_status (packs):
    stat = '┌ working accounts status\n'

    i = 0
    for pack in packs:
        stat += '├─── pack num {}\n'.format (i)

        for account in pack:
            uid = account['id']

            params = {'access_token': account['access_token'], 
                      'v': '5.80',
                      'count': '1'}

            proxies = {'http': 'http://{}'.format (account['proxy']), 
                       'https': 'https://{}'.format (account['proxy'])}

            count = requests.get ('https://api.vk.com/method/wall.get',
                                  params=params, proxies=proxies).json ()

            if 'error' in count:
                status = 'banned'
                views = 'None'

            else:
                status = 'active'
                try:
                    views = count['response']['items'][0]['views']

                except:
                    views = 'None'

            stat += '├ id: {} │ status: {} │ views: {}\n'.format (uid, status, views)


        i += 1

    return stat





def action_prompt():
    global action_dead
    action_dead = False

    prompt = '┌───────┬───────────────────┐\n' + '├   a   ├  start spamming   ┤\n' +\
             '├   c   ├  cancel spamming  ┤\n' + '├   q   ├ quit to main menu ┤\n' +\
             '├ stat  ├  show accs stat   ┤\n'\
             '├ clear ├  clear screen     ┤\n' + '└───────┴───────────────────┘'

    while True:
        print (prompt)
        act = input (bcolors.OKBLUE + 'action » ')

        if act == 'a':
            action_dead = False

            accounts_json_path = pathlib.Path(path_to_accounts_json).read_text(encoding='utf-8')
            packs = json.loads (accounts_json_path)['packs']

            for pack in packs:
                for account in pack:
                    access_token = account['access_token']
                    proxies = {'http': 'http://{}'.format (account['proxy']), 
                               'https': 'https://{}'.format (account['proxy'])}

                    action_thread = threading.Thread (target=action, 
                        args=(access_token, proxies))

                    action_thread.start()


        elif act == 'c':
            action_dead = True

        elif act == 'q':
            return

        elif act == 'stat':
            accounts_json_path = pathlib.Path(path_to_accounts_json).read_text(encoding='utf-8')
            packs = json.loads (accounts_json_path)['packs']

            print (show_pack_status (packs))

        elif act == 'clear':
            os.system('clear')




while True:
    main_prompt = '┌───────┬───────────────────┐\n' + '├   a   ├  add accs/proxies ┤\n' + \
             '├   q   ├  quit all & exit  ┤\n' + '├   p   ├  go to prep menu  ┤\n' + \
             '├ clean ├  open clean menu  ┤\n' + '├ clear ├  clear screen     ┤\n' + \
             '├ start ├ go to action menu ┤\n' + '└───────┴───────────────────┘'
             
    
    print ('{} threads working right now'.format (threading.active_count ()))
    print (main_prompt)
    act = input(bcolors.OKBLUE + '» ')

    if act == 'a':
        addnew = Add_new()

    elif act == 'q':
        global dead
        dead = True
        sys.exit()

    elif act == 'p':
        prepare_questions()

    elif act == 'clean':
        clean()

    elif act == 'clear':
        os.system('clear')

    elif act == 'start':
        action_prompt ()
