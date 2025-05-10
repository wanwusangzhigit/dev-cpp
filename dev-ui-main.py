import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.by import By
import html2text
from tkinterhtml import HTMLScrolledText  # 需要安装 tkinterhtml 模块
import bs4
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import os
import time
import psutil  # 需要安装 psutil 模块
import markdown  # 需要安装 markdown 模块

def spider(url, username, userpassword):
    option = webdriver.ChromeOptions()
    option.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=option)
    driver.get(url)
    time.sleep(1)
    
    element = driver.find_element(By.NAME, "uname")
    element.send_keys(username)
    
    element = driver.find_element(By.NAME, "password")
    element.send_keys(userpassword)
    
    button = driver.find_element(By.NAME, "login_submit")
    button.click()
    time.sleep(1)
    html_code = driver.page_source
    
    soup = bs4.BeautifulSoup(html_code, 'html.parser')
    for katex_span in soup.find_all('span', class_='katex'):
        annotation = katex_span.find('annotation')
        if annotation:
            katex_span.replace_with(f"${annotation.text}$")
    
    problem_content = soup.find('div', class_='problem-content')
    if problem_content:
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.bypass_tables = False
        h.ignore_images = False
        h.body_width = 0
        markdown = h.handle(str(problem_content))
    else:
        markdown = "未找到题目内容"
    
    driver.quit()
    return markdown

class DevCppSimulator:
    def __init__(self, root, username, password, problem_link):
        self.root = root
        self.root.title("Dev-C++ 模拟器")
        self.root.geometry("1000x600")
        self.root.configure(bg="black")

        self.file_path = None
        self.current_directory = os.getcwd()

        self.username = username
        self.password = password
        self.problem_link = problem_link

        self.create_menu()

        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.main_frame, width=300, bg="black")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.markdown_label = tk.Label(self.left_frame, text="Markdown 预览", bg="black", fg="white")
        self.markdown_label.pack(fill=tk.X)

        self.markdown_text = HTMLScrolledText(self.left_frame, background="black", foreground="white")
        self.markdown_text.pack(fill=tk.BOTH, expand=True)
        self.markdown_text.set_html(self.get_markdown())

        self.right_frame = tk.Frame(self.main_frame, bg="black")
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.editor = tk.Text(self.right_frame, wrap=tk.WORD, font=("Consolas", 12), bg="black", fg="white")
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.insert(tk.END, "#include <iostream>\n\nint main() {\n    std::cout << \"Hello, Dev-C++!\" << std::endl;\n    return 0;\n}")

        self.output_frame = tk.Frame(self.root, bg="black")
        self.output_frame.pack(fill=tk.X)

        self.output_label = tk.Label(self.output_frame, text="编译输出:", bg="black", fg="white")
        self.output_label.pack(side=tk.LEFT)

        self.output_text = scrolledtext.ScrolledText(self.output_frame, height=10, bg="black", fg="white")
        self.output_text.pack(fill=tk.X)

        self.button_frame = tk.Frame(self.root, bg="black")
        self.button_frame.pack(fill=tk.X)

        self.compile_button = tk.Button(self.button_frame, text="编译", command=self.compile_code, bg="black", fg="white")
        self.compile_button.pack(side=tk.LEFT)

        self.run_button = tk.Button(self.button_frame, text="运行", command=self.run_code, bg="black", fg="white")
        self.run_button.pack(side=tk.LEFT)

        self.submit_button = tk.Button(self.button_frame, text="提交", command=self.submit, bg="black", fg="white")
        self.submit_button.pack(side=tk.LEFT)

        self.exit_button = tk.Button(self.button_frame, text="退出", command=self.exit_app, bg="black", fg="white")
        self.exit_button.pack(side=tk.LEFT)

        self.highlight_cpp_syntax()

    def create_menu(self):
        menu_bar = tk.Menu(self.root, bg="black", fg="white")

        file_menu = tk.Menu(menu_bar, tearoff=0, bg="black", fg="white")
        file_menu.add_command(label="新建", command=self.new_file)
        file_menu.add_command(label="打开", command=self.open_file)
        file_menu.add_command(label="保存", command=self.save_file)
        file_menu.add_command(label="另存为...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.exit_app)
        menu_bar.add_cascade(label="文件", menu=file_menu)

        compile_menu = tk.Menu(menu_bar, tearoff=0, bg="black", fg="white")
        compile_menu.add_command(label="编译", command=self.compile_code)
        compile_menu.add_command(label="运行", command=self.run_code)
        compile_menu.add_command(label="编译并运行", command=self.compile_and_run)
        menu_bar.add_cascade(label="编译", menu=compile_menu)

        self.root.config(menu=menu_bar)

    def new_file(self):
        self.editor.delete(1.0, tk.END)
        self.file_path = None

    def open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".cpp",
            filetypes=[("C++ 文件", "*.cpp"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path = file_path
            with open(file_path, 'r', encoding='utf-8') as file:
                self.editor.delete(1.0, tk.END)
                self.editor.insert(tk.END, file.read())
            self.highlight_cpp_syntax()

    def save_file(self):
        if self.file_path:
            self._save_file(self.file_path)
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".cpp",
            filetypes=[("C++ 文件", "*.cpp"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_path = file_path
            self._save_file(file_path)

    def _save_file(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.editor.get(1.0, tk.END))
            messagebox.showinfo("保存成功", f"文件已保存到: {file_path}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def exit_app(self):
        if messagebox.askokcancel("退出", "确定要退出程序吗?"):
            self.root.destroy()

    def _get_file_info(self):
        if not self.file_path:
            messagebox.showwarning("警告", "请先保存文件")
            return None, None, None

        base_dir = os.path.dirname(self.file_path)
        file_name = os.path.basename(self.file_path)
        file_base_name = os.path.splitext(file_name)[0]

        return base_dir, file_name, file_base_name

    def compile_code(self):
        self.output_text.delete(1.0, tk.END)

        base_dir, file_name, file_base_name = self._get_file_info()
        if not base_dir:
            return

        temp_dir = os.path.join(self.current_directory, "temp")
        os.makedirs(temp_dir, exist_ok=True)

        compile_command = [
            'g++',
            self.file_path,
            '-o',
            os.path.join(temp_dir, file_base_name),
            '-std=c++14',
            '-O2'
        ]

        try:
            process = subprocess.Popen(
                compile_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=base_dir,
                text=True
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                self.output_text.insert(tk.END, f"编译失败:\n{stderr}")
            else:
                self.output_text.insert(tk.END, "编译成功\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"编译过程中出现错误: {str(e)}\n")

    def run_code(self):
        base_dir, file_name, file_base_name = self._get_file_info()
        if not base_dir:
            return

        temp_dir = os.path.join(self.current_directory, "temp")
        executable_path = os.path.join(temp_dir, file_base_name)

        if not os.path.exists(executable_path):
            messagebox.showwarning("警告", "请先编译代码")
            return

        self.output_text.delete(1.0, tk.END)

        start_time = time.time()
        try:
            process = subprocess.Popen(
                [executable_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()
            end_time = time.time()

            self.output_text.insert(tk.END, f"程序输出:\n{stdout}")
            if stderr:
                self.output_text.insert(tk.END, f"错误输出:\n{stderr}")

            self.output_text.insert(tk.END, f"运行时间: {end_time - start_time:.6f} 秒\n")

            if process.returncode == 0:
                self.output_text.insert(tk.END, f"程序顺利结束，返回值为 {process.returncode}\n")
            else:
                self.output_text.insert(tk.END, f"程序运行失败，返回值为 {process.returncode}\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"运行过程中出现错误: {str(e)}\n")

    def compile_and_run(self):
        self.compile_code()
        if "编译成功" in self.output_text.get("1.0", tk.END):
            self.run_code()

    def submit(self):
        base_dir, file_name, file_base_name = self._get_file_info()
        if not base_dir:
            return

        code = self.editor.get("1.0", tk.END)

        submit_file_path = os.path.join(self.current_directory, "submission.cpp")
        try:
            with open(submit_file_path, 'w', encoding='utf-8') as submit_file:
                submit_file.write(code)
            messagebox.showinfo("提交成功", f"代码已提交到: {submit_file_path}")
        except Exception as e:
            messagebox.showerror("提交失败", str(e))

    def get_markdown(self):
        return spider(self.problem_link, self.username, self.password)

    def highlight_cpp_syntax(self):
        keywords = [
            "auto", "break", "case", "catch", "char", "const", "continue", "default", "delete",
            "do", "double", "else", "enum", "extern", "float", "for", "goto", "if", "inline",
            "int", "long", "namespace", "new", "operator", "private", "protected", "public",
            "return", "short", "signed", "sizeof", "static", "struct", "switch", "template",
            "this", "throw", "try", "typedef", "typename", "union", "unsigned", "using",
            "void", "volatile", "while"
        ]

        self.editor.tag_configure("keyword", foreground="#FF8C00")
        self.editor.tag_configure("string", foreground="#FF00FF")
        self.editor.tag_configure("comment", foreground="#008000")
        self.editor.tag_configure("number", foreground="#008080")

        code = self.editor.get("1.0", tk.END)

        for keyword in keywords:
            start = "1.0"
            while True:
                pos = self.editor.search(r'\b' + keyword + r'\b', start, stopindex=tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(keyword)}c"
                self.editor.tag_add("keyword", pos, end)
                start = end

        start = "1.0"
        while True:
            pos = self.editor.search(r'"[^"]*"', start, stopindex=tk.END)
            if not pos:
                break
            end = f"{pos}+{len(self.editor.get(pos, pos + 'lineend'))}c"
            self.editor.tag_add("string", pos, end)
            start = end

        start = "1.0"
        while True:
            pos = self.editor.search(r'//.*', start, stopindex=tk.END)
            if not pos:
                break
            end = f"{pos}+{len(self.editor.get(pos, pos + 'lineend'))}c"
            self.editor.tag_add("comment", pos, end)
            start = end

        start = "1.0"
        while True:
            pos = self.editor.search(r'\b\d+\b', start, stopindex=tk.END)
            if not pos:
                break
            end = f"{pos}+{len(self.editor.get(pos, pos + 'lineend'))}c"
            self.editor.tag_add("number", pos, end)
            start = end


class StartPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Dev-C++ 模拟器 - 启动页面")
        self.root.geometry("600x400")
        self.root.configure(bg="black")

        self.check_gcc_installed()

    def check_gcc_installed(self):
        try:
            subprocess.run(['g++', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.show_main_page()
        except FileNotFoundError:
            self.show_install_instructions()

    def show_install_instructions(self):
        self.install_frame = tk.Frame(self.root, bg="black")
        self.install_frame.pack(fill=tk.BOTH, expand=True)

        label = tk.Label(self.install_frame, text="未检测到 GCC 编译器。请先安装 GCC。", bg="black", fg="white")
        label.pack(pady=20)

        instructions = tk.Text(self.install_frame, wrap=tk.WORD, bg="black", fg="white", font=("Courier New", 12))
        instructions.pack(fill=tk.BOTH, expand=True)
        instructions.insert(tk.END, """
安装 GCC 的方法：
1. 在 Windows 上：
   - 下载并安装 MinGW：http://www.mingw.org/download
   - 在安装过程中选择安装 `mingw32-gcc-g++` 组件。
   - 将 MinGW 的 `bin` 目录添加到系统的 `PATH` 环境变量中。

2. 在 Linux 上：
   - 打开终端并运行以下命令：
     ```
     sudo apt-get update
     sudo apt-get install build-essential
     ```

3. 在 macOS 上：
   - 安装 Homebrew（如果尚未安装）：
     ```
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```
   - 安装 GCC：
     ```
     brew install gcc
     ```
        """)
        instructions.config(state=tk.DISABLED)

        button = tk.Button(self.install_frame, text="退出", command=self.root.destroy, bg="black", fg="white")
        button.pack(pady=20)

    def show_main_page(self):
        if hasattr(self, 'install_frame'):
            self.install_frame.destroy()

        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        label = tk.Label(self.main_frame, text="欢迎使用 Dev-C++ 模拟器", bg="black", fg="white")
        label.pack(pady=20)

        self.username_label = tk.Label(self.main_frame, text="用户名:", bg="black", fg="white")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.main_frame, bg="black", fg="white", insertbackground="white")
        self.username_entry.pack()

        self.password_label = tk.Label(self.main_frame, text="密码:", bg="black", fg="white")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.main_frame, show="*", bg="black", fg="white", insertbackground="white")
        self.password_entry.pack()

        self.problem_link_label = tk.Label(self.main_frame, text="题目链接:", bg="black", fg="white")
        self.problem_link_label.pack()
        self.problem_link_entry = tk.Entry(self.main_frame, bg="black", fg="white", insertbackground="white")
        self.problem_link_entry.pack()

        self.start_button = tk.Button(self.main_frame, text="开始", command=self.start_main_program, bg="black", fg="white")
        self.start_button.pack(pady=20)

    def start_main_program(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        self.problem_link = self.problem_link_entry.get()

        if not self.username or not self.password or not self.problem_link:
            messagebox.showwarning("警告", "请填写所有信息")
            return

        self.root.destroy()
        root = tk.Tk()
        app = DevCppSimulator(root, self.username, self.password, self.problem_link)
        root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = StartPage(root)
    root.mainloop()
