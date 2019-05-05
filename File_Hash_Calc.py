import hashlib
from tkinter import *
from tkinter import filedialog
from tkinter import scrolledtext


def selectPath():
	global file_path
	select_path = filedialog.askopenfile()
	path.set(select_path.name)
	file_path = select_path.name


def calc():
	md5 = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
	sha1 = hashlib.sha1(open(file_path, 'rb').read()).hexdigest()
	sha256 = hashlib.sha256(open(file_path, 'rb').read()).hexdigest()
	sha512 = hashlib.sha512(open(file_path, 'rb').read()).hexdigest()
	tk.output.insert(END, f"MD5: {md5}\n\n")
	tk.output.insert(END, f"SHA1: {sha1}\n\n")
	tk.output.insert(END, f"SHA256: {sha256}\n\n")
	tk.output.insert(END, f"SHA512: {sha512}\n")


if __name__ == '__main__':
	file_path = ''
	print("校验器启动...")
	tk = Tk()
	tk.title("哈希校验器")
	path = StringVar()

	# 组件&布局
	tk.label1 = Label(text="文件路径")
	tk.path_text = Entry(textvariable=path)
	tk.select_path_btn = Button(text="选择文件", command=selectPath)
	tk.calc_btn = Button(text='开始计算', command=calc, width=15)
	tk.output = scrolledtext.ScrolledText(width=50, height=30)
	tk.label3 = Label(text="@ FengSec")  # name
	# 网格布局
	tk.label1.grid(row=0, column=0)
	tk.path_text.grid(row=0, column=1)
	tk.select_path_btn.grid(row=0, column=2)
	tk.calc_btn.grid(row=2, columnspan=3)
	tk.output.grid(row=3, columnspan=3)
	tk.label3.grid(row=4, column=2)

	tk.mainloop()
