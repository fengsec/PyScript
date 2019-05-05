import socket
from tkinter import *
from tkinter import scrolledtext

def scan():
    ip = tk.ip_input.get() or '127.0.0.1'  # 输入IP,默认本机
    start = tk.port_start.get() or '0'  # 输入始末网段,默认0~65535
    end = tk.port_end.get() or '65535'
    tk.output.insert(END, f'开始扫描IP: {ip} && Port:{start} - {end} \n')
    open_port = []
    for port in range(int(start), int(end)):
        try:
            s = socket.socket()
            s.settimeout(0.2)  # 超时
            s.connect((ip, port))
            txt = f"[+] Port: {port} open\n"
            open_port.append(port)
            s.close()
        except:
            txt = f"[-] Port: {port} close\n"
            # txt = ''
        finally:
            tk.output.insert(END, txt)  # 在末尾END插入
            tk.output.update()  # 实时输出
    tk.output.insert(END, f"扫描结束,检测到开启端口共{len(open_port)}个...\n")
    tk.output.insert(END, f"已开启端口: {open_port}")


if __name__ == '__main__':
    print("端口扫描器启动...")
    tk = Tk()
    tk.title('端口扫描器')

    # 组件
    tk.label1 = Label(text="请输入需要扫描的IP(默认本机) ")  # IP提示
    tk.ip_input = Entry(width=19)  # IP
    tk.label2 = Label(text="请输入需要扫描的网段(默认0~65535)")  # 网段提示
    tk.port_start = Entry(width=8)  # 开始端口
    tk.port_end = Entry(width=8)  # 结束端口
    tk.scan_btn = Button(text='开始扫描', command=scan, width=12)
    tk.output = scrolledtext.ScrolledText(width=50, height=30)
    tk.label3 = Label(text="@ 袁剑锋")  # name

    # grid网格布局
    tk.label1.grid(row=0, column=0)
    tk.ip_input.grid(row=0, column=1, columnspan=2)
    tk.label2.grid(row=1, column=0)
    tk.port_start.grid(row=1, column=1)
    tk.port_end.grid(row=1, column=2)
    tk.scan_btn.grid(row=2, columnspan=2)
    tk.output.grid(row=3, columnspan=3)
    tk.label3.grid(row=4, column=2)
    tk.mainloop()  # 主消息循环
