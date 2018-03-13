# encoding:UTF-8
# python3.6
import os
import re
import json
import time
import datetime
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from PIL import Image
from requests_toolbelt import MultipartEncoder

pwuser = 'xxxx'#用户名
pwpwd = 'xxxx'#密码
question = '1'#验证问题序号（从上到下）
answer = 'xxxx'#验证问题答案

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/60.0.3112.90 Safari/537.36',
}
proxies = {
    'http': 'socks5://127.0.0.1:1080',
    'https': 'socks5://127.0.0.1:1080'
}
defalt_proxies = proxies


def save_cookies(session, file='cookie.txt'):
    with open(file, 'w') as f:
        json.dump(requests.utils.dict_from_cookiejar(session.cookies), f)


def load_cookies(session, file='cookie.txt'):
    with open(file, 'r') as f:
        session.cookies = requests.utils.cookiejar_from_dict(json.load(f))


def islogin(session):
    if os.path.exists('cookie.txt'):
        load_cookies(session=session)
    else:
        pass
    try:
        r = session.get('http://moeshare.com/u.php', headers=headers,
                        proxies=defalt_proxies)
    except Exception as e:
        r = session.get('http://moeshare.com/u.php',
                        headers=headers, proxies=proxies)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'lxml')
    flag = soup.title.text
    print(flag)
    if flag != '提示信息 - Powered by phpwind':
        result = '已登录'
    else:
        result = '未登录'
    return result


def pre_login(session, openimg=True):
    try:
        r = session.get('http://moeshare.com/login.php#breadCrumb',
                        headers=headers, proxies=defalt_proxies)
    except Exception as e:
        r = session.get('http://moeshare.com/login.php#breadCrumb',
                        headers=headers, proxies=proxies)
    soup = BeautifulSoup(r.text, 'lxml')
    divs = soup.find_all('img')
    try:
        capt = session.get(urljoin('http://moeshare.com',
                                   divs[-1]['src']), headers=headers, stream=True, proxies=defalt_proxies)
    except Exception as e:
        capt = session.get(urljoin('http://moeshare.com',
                                   divs[-1]['src']), headers=headers, stream=True, proxies=proxies)
    with open('capt.png', 'wb') as f:
        for chunk in capt.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    if openimg == True:
        with Image.open("capt.png") as im:
            im.show()
    else:
        pass


def login(qanswer, session):
    try:
        os.remove('capt.png')
    except Exception as e:
        raise
    data = {
        'answer': answer，
        'cktime': '31536000',
        'hideid': '0',
        'jumpurl': 'index.php',
        'lgt': '0',
        'pwpwd': pwpwd,
        'pwuser': pwuser,
        'qanswer': qanswer,
        'qkey': '-1',
        'question': question,
        'step': '2',
    }
    try:
        r = session.post('http://moeshare.com/login.php?',
                         data=data, headers=headers, proxies=defalt_proxies)
    except Exception as e:
        r = session.post('http://moeshare.com/login.php?',
                         data=data, headers=headers, proxies=proxies)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'lxml')
    flag = soup.find('span')
    if flag != None and flag.text == '您已经顺利登录':
        result = '登录成功'
        save_cookies(session)
    else:
        result = '登录失败'
    return result


def post_news(news, session):
    try:
        r = session.get('http://moeshare.com/post.php?fid=17',
                        headers=headers, proxies=defalt_proxies)
    except Exception as e:
        r = session.get('http://moeshare.com/post.php?fid=17',
                        headers=headers, proxies=proxies)
    soup = BeautifulSoup(r.text, 'lxml')
    verify = soup.find('input', attrs={'name': 'verify'})['value']
    hexie = soup.find(
        'input', attrs={'name': '_hexie'}).find_next_sibling('script').text[-11:-3]
    fields = {
        "magicname": '',
        "magicid": '',
        "verify": verify,
        "cyid": '0',
        "ajax": '1',
        "iscontinue": '0',
        "atc_usesign": '1',
        "atc_autourl": '1',
        "atc_convert": '1',
        "atc_money": '1',
        "atc_credittype": 'money',
        "atc_rvrc": '0',
        "atc_enhidetype": '0',
        "atc_title": news['title'],  # 标题
        "atc_iconid": '0',
        "p_type": '59',
        "p_sub_type": '0',
        "atc_content": news['content'],  # 正文
        "att_special1": '0',
        "att_ctype1": 'money',
        "atc_needrvrc1": '0',
        "step": '2',
        "action": 'new',
        "fid": '17',
        "tid": '0',
        "article": '0',
        "special": '0',
        "_hexie": hexie,
    }
    m = MultipartEncoder(fields, boundary='WebKitFormBoundary0ABbhG1IDBxTLQam')
    nowtime = str(round(time.time() * 1000))  # 毫秒时间戳
    post_url = 'http://moeshare.com/post.php?fid=17&nowtime='+nowtime+'&verify='+verify
    new = headers
    new['Content-Type'] = m.content_type
    try:
        r = session.post(post_url, data=m, headers=new, proxies=defalt_proxies)
    except Exception as e:
        r = session.post(post_url, data=m, headers=new, proxies=proxies)
    pattern = re.compile(r'(?<=(\[CDATA\[)).+(?=(\]\]></ajax>))')
    #'<?xml version="1.0" encoding="utf-8"?><ajax><![CDATA[success\tread.php?tid=145492]]></ajax>'
    result = pattern.search(r.text.replace('\t', ' '))
    if result != None:
        text = result.group().split(' ')
        if text[0] == 'success':
            text[1] = urljoin('http://moeshare.com', text[1])
            result = '{}\n{}'.format(text[0], text[1])
        else:
            result = result.group()
    else:
        result = '未返回结果'
    save_cookies(session)
    return result


def dailybonus(session):
    try:
        r = session.get('http://moeshare.com/u.php',
                        headers=headers, proxies=defalt_proxies)
    except Exception as e:
        r = session.get('http://moeshare.com/u.php',
                        headers=headers, proxies=proxies)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'lxml')
    verify = soup.find('input', attrs={'name': 'verify'})['value']
    post_url = 'http://moeshare.com/jobcenter.php?action=punch&verify=' + verify + '&step=2'
    try:
        r = session.post(
            post_url, headers=headers, proxies=defalt_proxies)
    except Exception as e:
        r = session.post(
            post_url, headers=headers, proxies=proxies)
    r.encoding = 'utf-8'  # 纠正编码
    pattern = re.compile('(?<=(\"message\":\')).+(?=(\',\"flag\"))')
    try:
        result = pattern.search(r.text).group()
    except Exception as e:
        print(r.text[:30])
        result = 'no result'
    save_cookies(session)
    return result


def get_news(url):
    news = {}
    acgdog_pattern = re.compile(r'http(s)?://www\.acgdoge\.net/archives/\d+')
    dmzj_pattern = re.compile(
        r'http(s)?://(m)?news\.dmzj\.com/article/\d+\.html')
    qq_pattern = re.compile(r'http(s)?://comic\.qq\.com/a/\d+/\d+\.htm')
    if acgdog_pattern.search(url):
        url = acgdog_pattern.search(url).group()
        r = requests.get(url, headers=headers)
        r.encoding = 'utf-8'  # 纠正编码
        # soup=BeautifulSoup(r.text, "lxml")
        # soup=soup.find('hgroup',attrs={'class':"post_hctn"}).parent
        # lxml真是有毒，就是不能直接找到我要的tag,html5lib就可以
        soup = BeautifulSoup(r.text, "html5lib")
        soup = soup.find('article')
        title = soup.find(class_="post_h").a.text
        post_time = soup.find(class_="post_t_d").text.split('/')
        mon = int(post_time[0])
        day = int(post_time[1])
        china_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        china_time = china_time.timetuple()
        if mon > china_time[1]:
            year = china_time[0]-2001
        else:
            year = china_time[0]-2000
        news['title'] = '[{0}{1:02}{2:02}]{3}'.format(
            str(year), mon, day, title)
        content_divs = soup.find(class_="post_t").find_all('p')
        img_src = 'data-lazy-src'
    elif dmzj_pattern.search(url):
        url = dmzj_pattern.search(url).group().replace('mnews', 'news')
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        soup = soup.find(class_="news_content autoHeight")
        title = soup.find('h1').text
        time = soup.find(class_="data_time").text[2:10].replace('-', '')
        news['title'] = '[{0}]{1}'.format(time, title)
        content_divs = soup.find(class_="news_content_con").find_all('p')
        img_src = 'src'
    elif qq_pattern.search(url):
        url = acgdog_pattern.search(url).group()
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        soup = soup.find(class_="qq_article")
        title = soup.find('h1').text.rstrip()
        time = soup.find(class_="a_time").text[2:10].replace('-', '')
        news['title'] = '[{0}]{1}'.format(time, title)
        content_divs = soup.find(bosszone="content")
        img_src = 'src'
    else:
        return 0
    content = '[url]{}[/url]'.format(url)+'\n'
    for div in content_divs:
        if div.text == '':
            if div.find('img') != None:
                img_url = div.find('img')[img_src]
                content = content+'[img]{}[/img]\n'.format(img_url)
            else:
                pass
        else:
            content = content+'{}\n'.format(div.text)
    news['content'] = content
    return news
