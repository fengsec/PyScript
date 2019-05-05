import requests
from PIL import Image
from bs4 import BeautifulSoup
import copy
import time
import re
import os
import json
import threading
import smtplib
import platform
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr


class Spider:
    class Lesson:

        def __init__(self, name, code, teacher_name, Time, number):
            self.name = name
            self.code = code
            self.teacher_name = teacher_name
            self.time = Time
            self.number = number

        def show(self):
            print('  name:' + self.name + '  code:' + self.code + '  teacher_name:' + self.teacher_name + '  time:' + self.time)

    def __init__(self, url):
        self.__uid = ''
        self.__real_base_url = ''
        self.__base_url = url
        self.__name = ''
        self.__base_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': '',
            'ddl_kcxz': '',
            'ddl_ywyl': '',
            'ddl_kcgs': '',
            'ddl_xqbs': '1',
            'ddl_sksj': '',
            'TextBox1': '',
            'dpkcmcGrid:txtChoosePage': '1',
            'dpkcmcGrid:txtPageSize': '200',
        }
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/67.0.3396.62 Safari/537.36',
        }
        self.session = requests.Session()
        self.__now_lessons_number = 0

    def __set_real_url(self):
        """
        得到真实的登录地址（无Cookie）
        获取Cookie（有Cookie)
        :return: 该请求
        """
        request = requests.get(self.__base_url, headers=self.__headers)
        real_url = request.url
        self.__real_base_url = real_url[:len(real_url) - len('default2.aspx')]
        return request

    def __get_code(self):
        """
        获取验证码
        :return: 验证码
        """
        request = self.session.get(self.__real_base_url + 'CheckCode.aspx?', headers=self.__headers)
        with open('code.jpg', 'wb')as f:  # 写入验证码
            f.write(request.content)
        # 判断当前操作系统,Windows直接显示验证码Linux则以邮件形式发送验证码图片
        sys = platform.system()
        if sys == 'Windows':
            print("当前系统为Windows,显示登录验证码...")
            im = Image.open('code.jpg')
            im.show()
        else:
            with open('code.jpg', 'rb')as f:
                img_data = f.read()
            send_email_img(to_addr, from_addr, smtp_password, smtp_server,img_data)  # 发送邮件
            # print("当前系统为Linux,登录验证码以邮件形式发送,请注意查收...")
        print('请输入验证码:')
        code = input()
        return code

    def __get_login_data(self, uid, password):
        """
        得到登录包
        :param uid: 学号
        :param password: 密码
        :return: 含登录包的data字典
        """
        self.__uid = uid
        request = self.__set_real_url()
        soup = BeautifulSoup(request.text, 'lxml')
        form_tag = soup.find('input')
        __VIEWSTATE = form_tag['value']
        code = self.__get_code()
        data = {
            '__VIEWSTATE': __VIEWSTATE,
            'txtUserName': self.__uid,
            'TextBox2': password,
            'txtSecretCode': code,
            'RadioButtonList1': '学生'.encode('gb2312'),
            'Button1': '',
            'lbLanguage': '',
            'hidPdrs': '',
            'hidsc': '',
        }
        return data

    def login(self, uid, password):
        """
        外露的登录接口
        :param uid: 学号
        :param password: 密码
        :return: 抛出异常或返回是否登录成功的布尔值
        """
        while True:
            data = self.__get_login_data(uid, password)
            if self.__real_base_url != 'http://218.75.197.123:83/':
                request = self.session.post(self.__real_base_url + 'default2.aspx', headers=self.__headers, data=data)
            else:
                request = self.session.post(self.__real_base_url + 'index.aspx', headers=self.__headers, data=data)
            soup = BeautifulSoup(request.text, 'lxml')
            if request.status_code != requests.codes.ok:
                print('4XX or 5XX Error,try to login again')
                time.sleep(0.5)
                continue
            if request.text.find('验证码不正确') > -1:
                print('验证码错误')
                continue
            if request.text.find('密码错误') > -1:
                print('密码错误')
                return False
            if request.text.find('用户名不存在') > -1:
                print('用户名错误')
                return False
            try:
                name_tag = soup.find(id='xhxm')
                self.__name = name_tag.string[:len(name_tag.string) - 2]
                email['name'] = self.__name
                print('欢迎' + self.__name)
                self.__enter_lessons_first()
                return True
            except:
                print('未知错误，尝试再次登录')
                time.sleep(0.5)
                continue

    def __enter_lessons_first(self):
        """
        首次进入选课界面
        :return: none
        """
        data = {
            'xh': self.__uid,
            'xm': self.__name.encode('gb2312'),
            'gnmkdm': 'N121103',
        }
        self.__headers['Referer'] = self.__real_base_url + 'xs_main.aspx?xh=' + self.__uid
        request = self.session.get(self.__real_base_url + 'xf_xsqxxxk.aspx', params=data, headers=self.__headers)
        self.__headers['Referer'] = request.url
        soup = BeautifulSoup(request.text, 'lxml')
        self.__set__VIEWSTATE(soup)
        selected_lessons_pre_tag = soup.find('legend', text='已选课程')
        selected_lessons_tag = selected_lessons_pre_tag.next_sibling
        tr_list = selected_lessons_tag.find_all('tr')[1:]
        self.__now_lessons_number = len(tr_list)
        try:
            xq_tag = soup.find('select', id='ddl_xqbs')
            self.__base_data['ddl_xqbs'] = xq_tag.find('option')['value']
        except:
            pass

    def __set__VIEWSTATE(self, soup):
        __VIEWSTATE_tag = soup.find('input', attrs={'name': '__VIEWSTATE'})
        self.__base_data['__VIEWSTATE'] = __VIEWSTATE_tag['value']

    def __get_lessons(self, soup):
        """
        提取传进来的soup的课程信息
        :param soup:
        :return: 课程信息列表
        """
        lesson_list = []
        lessons_tag = soup.find('table', id='kcmcGrid')
        lesson_tag_list = lessons_tag.find_all('tr')[1:]
        for lesson_tag in lesson_tag_list:
            td_list = lesson_tag.find_all('td')
            code = td_list[0].input['name']  # 选课id
            name = td_list[2].string  # 课程名
            teacher_name = td_list[4].string  # 教师名
            Time = td_list[9].string  # 上课时间
            number = td_list[11].string  # 余量
            lesson = self.Lesson(name, code, teacher_name, Time, number)
            lesson_list.append(lesson)
        return lesson_list

    def __search_lessons(self, lesson_name=''):
        """
        搜索课程
        :param lesson_name: 课程名字
        :return: 课程列表
        """
        self.__base_data['TextBox1'] = lesson_name.encode('gb2312')
        data = self.__base_data.copy()
        data['Button2'] = '确定'.encode('gb2312')
        request = self.session.post(self.__headers['Referer'], data=data, headers=self.__headers)
        soup = BeautifulSoup(request.text, 'lxml')
        self.__set__VIEWSTATE(soup)
        return self.__get_lessons(soup)

    def __select_lesson(self, lesson_list):
        """
        开始选课
        :param lesson_list: 选的课程列表
        :return: none
        """
        data = copy.deepcopy(self.__base_data)
        data['Button1'] = '  提交  '.encode('gb2312')
        while True:
            for lesson in lesson_list:
                try:
                    code = lesson.code
                    data[code] = 'on'
                    request = self.session.post(self.__headers['Referer'], data=data, headers=self.__headers,timeout=5)
                except:
                    continue
                start = time.time()
                soup = BeautifulSoup(request.text, 'lxml')
                self.__set__VIEWSTATE(soup)
                error_tag = soup.html.head.script
                if not error_tag is None:
                    error_tag_text = error_tag.string
                    r = "alert\('(.+?)'\);"
                    for s in re.findall(r, error_tag_text):
                        print(s)
                print('已成功选到的课程:')
                selected_lessons_pre_tag = soup.find('legend', text='已选课程')
                selected_lessons_tag = selected_lessons_pre_tag.next_sibling
                tr_list = selected_lessons_tag.find_all('tr')[1:]
                self.__now_lessons_number = len(tr_list)
                for tr in tr_list:
                    td = tr.find('td')
                    print(td.string)
                print(time.time()-start)

    def run(self,uid,password):
        """
        开始运行
        :return: none
        """
        if self.login(uid, password):
            print('请输入搜索课程名字，直接回车则显示全部可选课程')
            lesson_name = input()
            lesson_list = self.__search_lessons(lesson_name)
            print('请输入想选的课的id，id为每门课程开头的数字,如果没有课程显示，代表公选课暂无')
            for i in range(len(lesson_list)):
                print(i, end='')
                lesson_list[i].show()
            select_id = int(input('请输入选课id(每门课程开头的数字): '))
            lesson_list = lesson_list[select_id:select_id + 1]
            email['lesson'] = lesson_list[0].name  # 课程名称
            print(f"正在抢课: {email['lesson']}...")
            thread_list = list()
            for i in range(15):
                thread_list.append(threading.Thread(target=self.__select_lesson, args=(lesson_list,)))
            for i in range(15):
                print(f"启动线程{i+1}...")
                thread_list[i].start()
            for i in range(15):
                thread_list[i].join()


# 格式化邮件地址函数
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_email_text(to_addr, from_addr, smtp_password, smtp_server):
# 格式化邮件
    msg = MIMEText(f"{email['name']}所选课程:{email['lesson']}抢课已完成,{email['text']}", 'html', 'utf-8')  # 邮件内容
    msg['To'] = _format_addr(f'收件人 <{to_addr}>' )  # 收件人
    msg['From'] = _format_addr(f'发件人 <{from_addr}>')   # 发件人
    msg['Subject'] = Header(f"{email['name']}抢课成功!!", 'utf-8').encode()  # 邮件标题
# 发送
    try:
        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.set_debuglevel(1)
        server.login(from_addr, smtp_password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        print("发送成功")
        server.quit()
    except smtplib.SMTPException as e:
        print('发送失败，Case:%s' % e)


def send_email_img(to_addr, from_addr, smtp_password, smtp_server, img_data):
# 创建邮件对象并格式化
    msg = MIMEMultipart()
    msg['To'] = _format_addr(f'收件人 <{to_addr}>' )  # 收件人
    msg['From'] = _format_addr(f'发件人 <{from_addr}>')   # 发件人
    msg['Subject'] = Header(f'图片验证码', 'utf-8').encode()  # 邮件标题
# 以html形式发送图片验证码
    content = MIMEText('<html><body><img src="cid:imageid" alt="imageid"></body></html>','html','utf-8')
    msg.attach(content)
    img = MIMEImage(img_data)
    img.add_header('Content-ID', 'imageid')
    msg.attach(img)
# 发送
    try:
        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.set_debuglevel(1)
        server.login(from_addr, smtp_password)
        server.sendmail(from_addr, [to_addr], msg.as_string())
        print("发送成功")
        server.quit()
    except smtplib.SMTPException as e:
        print('发送失败，Case:%s' % e)


if __name__ == '__main__':
    url = "" # 官网地址
    uid = ""  # 学号
    password = ""  # 密码
    to_addr = ""  # 发件人
    from_addr = ""  # 收件人
    smtp_server = ""  # smtp服务器
    smtp_password = ""  # smtp授权码
# 显示说明并尝试登录
    print(ReadMe)
    print('尝试登录...')
    email = {'text': '请登录教务网检查!!!'}
    spider = Spider(url)
    spider.run(uid, password)
    os.system("pause")
    send_email_text(to_addr, from_addr, smtp_password, smtp_server)  # 抢课完成
