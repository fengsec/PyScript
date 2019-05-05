import time
import datetime
import schedule
import requests
from bs4 import BeautifulSoup

# API测试：https://open.weibo.com/tools/console # 获取access_token
# API文档：https://open.weibo.com/wiki/2/statuses/share


# 发送微博
def send_weibo(one_text, one_pic, today_text):
    weibo_url = "https://api.weibo.com/2/statuses/share.json"
    data = {
        "access_token": "Your_access_token",
        "status": today_text + one_text + "http://wufazhuce.com/",  # 文本需要包含一个安全域名
    }
    files = {
        "pic": one_pic  # 图片
    }
    send = requests.post(weibo_url, data=data, files=files)


# 获取每日一句&图片
def get_one():
    one_url = "http://wufazhuce.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/71.0.3578.98 Safari/537.36',
    }
    response = requests.get(one_url, headers=headers)
    html = response.content.decode('utf-8')
    soup = BeautifulSoup(html, 'lxml')
    text = soup.find(class_='fp-one-cita').text  # 找到'fp-one-cita'类中的文本
    pic_url = soup.find(class_='fp-one-imagen')['src']  # 找到'fp-one-image'类中图片地址
    pic = requests.get(pic_url).content  # img二进制文件
    return text, pic  # 返回文本和图片


# 获取日期
def get_time():
    week_day = {
        0: '星期一',
        1: '星期二',
        2: '星期三',
        3: '星期四',
        4: '星期五',
        5: '星期六',
        6: '星期天',
    }
    today = datetime.datetime.today()
    day = today.weekday()  # 获取星期
    today_str = today.strftime('%Y-%m-%d')  # 截断日期
    today_text = f'{today_str} {week_day[day]}'
    return today_text


# 整合
def job():
    one_text, one_pic = get_one()  # 获取每日一句&图片
    today_text = get_time()  # 获取日期
    send_weibo(one_text, one_pic, today_text)
    # print("发送成功")


schedule.every().day.at("08:00").do(job)  # 每日定时执行

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)
