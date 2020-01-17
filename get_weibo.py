# -*- coding: utf-8 -*-
# get_weibo.py
import re
import time
import json
import requests
import smtplib
from bs4 import BeautifulSoup
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

# 获取页面json
def get_data(url, headers):
	r = requests.get(url, headers=headers)
	content = r.content
	data = json.loads(content)['data']  # json转为dic
	return data


# 获取用户主页id,用于后续爬取
def get_containerid(data):
    tabs = data['tabsInfo']['tabs']
    for tab in tabs:
    	if tab['tab_type'] == 'weibo':
    		containerid = tab['containerid']
    return containerid


# 获取用户信息
def get_userInfo(data):
	screen_name = data['userInfo']['screen_name']          # 微博昵称
	profile_url = data['userInfo']['profile_url']          # 微博地址
	follow_count = data['userInfo']['follow_count']        # 关注人数
	followers_count = data['userInfo']['followers_count']  # 粉丝数
	userInfo = {
		'微博昵称': screen_name,
		'微博地址': profile_url,
		'关注人数': follow_count,
		'粉丝数': followers_count
	}
	return userInfo


# 解析微博内容
def parse_weibo(weibo_data, headers):
	cards = weibo_data['cards']
	mblog = cards[0]['mblog']  # 每个cards[i]为一组微博,第0个为最新或置顶
	imgs = []  # 图片列表,用于保存图片url,初始为空
	try:
		if '置顶' == mblog['title']['text']:  # 判断是否含有置顶
			mblog = cards[2]['mblog']
	except KeyError as e:
		pass
	if 'pics' in mblog:  # 判断微博内容有没有包含图片
		pics = mblog['pics']
		for pic in pics:
			imgs.append(pic['url'])
	created_at = mblog['created_at']  # 微博发布日期
	text = mblog['text']              # 微博内容,包含html标签
	# 如果未显示全文,需跳转到全文页面获取内容
	if '全文' in text:    # 需跳转到全文的微博,匹配其跳转连接
		href_url = re.findall('<a href="(.*?)\">全文', text)[0]
		full_url = f"https://m.weibo.cn{href_url}"
		response = requests.get(full_url, headers=headers)    # 获取全文网页
		full_page = response.text
		soup = BeautifulSoup(full_page, 'lxml')
		script = soup.select("script")[1].string  # 未登录时,微博内容存放在<script>内
		text = re.findall('"text": (.*)', script)[0]
	text = re.sub(r'href=\\"', 'href="', text)  # 匹配去除href后面斜杠,href=\"www...com"
	text = re.sub('src="//h5(.*?)', 'src=\"http://h5', text)  # 匹配微博表情,添加http才可以显示
	return text,created_at,imgs


# 格式化邮件地址函数
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))
# 发送邮件
def send_email(weibo_text, date, imgs):
	with open('get_weibo.txt', 'a+') as f:
		for img in imgs:     # 如果有图片则以img标签形式追加到文本
			weibo_text += f'<img src="{img}">'
		f.write(weibo_text)  # 把微博内容写入文本记录
	# 设置收发邮箱
	to_addr = ''        # 接收邮箱
	from_addr = ''      # 发送邮箱
	password = ''       # 发送邮箱打开SMTP服务生成的第三方授权码,不是登陆密码！
	smtp_server = ''    # 设置SMTP服务器
	# 格式化邮件信息
	msg = MIMEText(weibo_text, 'html', 'utf-8')                   # 邮件内容
	msg['To'] = _format_addr(f'收件人 <{to_addr}>' )               # 收件人
	msg['From'] = _format_addr(f'发件人 <{from_addr}>')            # 发件人
	msg['Subject'] = Header(f'{date} - 微博爬虫', 'utf-8').encode()  # 邮件标题
	# 发送
	try:
	    # server = smtplib.SMTP(smtp_server, 25)
	    server = smtplib.SMTP_SSL(smtp_server, 465)
	    server.set_debuglevel(1)
	    server.login(from_addr, password)
	    server.sendmail(from_addr, [to_addr], msg.as_string())
	    print("发送成功")
	    server.quit()
	except smtplib.SMTPException as e:
	    print('发送失败,Case:%s' % e)


if __name__ == '__main__':
	oid = ""  # 指定用户oid
	headers = {
	    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
	                  'Chrome/71.0.3578.98 Safari/537.36',
	}

	# 通过主页面json获取用户信息和用户主页containerid
	url = f'https://m.weibo.cn/api/container/getIndex?type=uid&value={oid}'  # 主页url
	data = get_data(url, headers)        # 主页面json
	userInfo = get_userInfo(data)        # 用户信息
	containerid = get_containerid(data)  # 用户主页containerid
	# print(containerid)

	while True:
		print("开始获取...")
		# 通过containerid获取微博页面json,并解析微博页面json得到微博内容
		weibo_url = f'https://m.weibo.cn/api/container/getIndex?type=uid&value={oid}&containerid={containerid}&page=1'
		weibo_data = get_data(weibo_url, headers)  # 微博页面json
		weibo_text,date,imgs = parse_weibo(weibo_data, headers)  # 微博内容和日期,这里设为第0条,即最新一条
		if ('刚刚' in date) or ("分钟" in date and int(date[:-3]) <= 10):  # 微博刚刚发出或发出时间小于10分钟
			print("有新的微博,准备发邮件...")
			flag = True
			with open('get_weibo.txt', 'a+') as f:
				line = f.readline()  # 逐行读取,判断微博内容是否已发送过(即已存在txt中)
				while line:
					if weibo_text in txt:
						flag = False
					line = f.readline()
			if flag: # 不存在txt中则发送
				send_email(weibo_text, date, imgs)
		print("本次抓取完成,休息5分钟...")
		time.sleep(300)
