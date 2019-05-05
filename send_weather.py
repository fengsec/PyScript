# -*- coding: utf-8 -*-
import json
import itchat
import requests
import time
import datetime

# 获取并解析天气数据
def get_data(location='guangzhou'):
    url = f'https://free-api.heweather.net/s6/weather/now?location={location}&key=9fa71c2078b749c1bc674dd8da51a51f'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/71.0.3578.98 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    json_data = response.content.decode('utf-8')
    data = json.loads(json_data)
# 解析天气
    status = data['HeWeather6'][0]['status']  # 接口状态
    if status != 'ok':
        weather_txt = '天气获取失败!'
        return weather_txt
    basic = data['HeWeather6'][0]['basic']
    update = data['HeWeather6'][0]['update']
    now = data['HeWeather6'][0]['now']
    city = basic['location']  # 所在城市
    tmp = now['tmp']  # 温度
    cond_txt = now['cond_txt']  # 天气
    wind_sc = now['wind_sc']  # 风力
    wind_dir = now['wind_dir']  # 风向
    if wind_sc == '0':
        wind_sc = '微风'
    else:
        wind_sc = f'风力{wind_sc}级'
# 返回文本
    weather_txt = f'{city}天气:{cond_txt}\n温度:{tmp}°\n{wind_dir},{wind_sc}'
    return weather_txt


# 自动回复查询天气
@itchat.msg_register(itchat.content.TEXT)  # 封装好的装饰器,itchat.content.
def reply_search_weather(msg):
    content = msg['Content']  # 获取收到的文本信息
    user_code = msg['FromUserName']  # 获取发送者特征码
    user_nick_name = itchat.search_friends(userName=user_code)['NickName']  # 通过特征码获取用户名
    my_nick_name = itchat.search_friends()['NickName']   # 获取自身用户名
    if '天气' in content and user_nick_name != my_nick_name:  # 判断消息不是自己发出的
        location = content[:-2]
        weather_txt = get_data(location)
        msg.user.send(weather_txt)


# 定时信息
def send_weather():
    while True:
        f_name = itchat.search_friends(remarkName='备注')[0]['UserName']  # 通过备注指定好友
        now = datetime.datetime.now()    # 获取当前时间
        now_str = now.strftime('%Y/%m/%d %H:%M:%S')[11:-3]  # 截断得到时分
        weather_txt = get_data(location='广州')
        text = f'现在是{now.hour}点{now.minute}分\n下面是天气预报:\n' + weather_txt
        if now_str in ['07:00','11:00','17:00','22:00']:   # 设置触发时间
            itchat.send(text, toUserName=f_name)
        time.sleep(60)   # 每分钟运行一次


if __name__ == '__main__':
    itchat.auto_login(enableCmdQR=2, hotReload=True)  # 登录,暂存登陆状态hotReload=True,命令行二维码enableCmdQR=True
    print("登录成功")
    send_weather()
    # itchat.run(debug=True)  # 开启自动回复
