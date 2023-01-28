import tkinter as tk
import numpy as np
from matplotlib import pyplot as plt
import requests
import time
import datetime as dt
from PIL import ImageTk, Image


class GraphGenerator:

    graph_type = "line"

    def __init__(self, master):

        master.iconphoto(False, tk.PhotoImage(file='icon.png'))

        frame = tk.Frame(master)
        frame.pack()

        self.create_menus(master, frame)
        self.main_window(frame, "handmade")

    def main_window(self, frame, source_type):

        for widgets in frame.winfo_children():
            widgets.destroy()

        self.back_pic = ImageTk.PhotoImage(Image.open('pic.png').resize((480, 3500), Image.ANTIALIAS))
        back_label = tk.Label(frame, image=self.back_pic)
        back_label.place(relx=0.5, rely=0.5, anchor='center')

        if source_type == "handmade":
            self.handmade_graphs(frame)
        elif source_type == "API":
            self.API_graphs(frame)

    def create_menus(self, master, frame):
        menu = tk.Menu(master)
        master.config(menu=menu)

        edit = tk.Menu(menu)
        menu.add_cascade(label="Edit", menu=edit)

        edit.add_command(label="Open the text editor", command=self.text_editor)
        edit.add_command(label="Clear", command=self.clear)

        view = tk.Menu(menu)
        menu.add_cascade(label="View", menu=view)

        view.add_command(label="Stocks", command=lambda: self.main_window(frame=frame, source_type="API"))
        view.add_command(label="Custom", command=lambda: self.main_window(frame=frame, source_type="handmade"))

        view.add_separator()

        view.add_command(label="Line Plot", command=lambda: self.set_graph_type("line"))
        view.add_command(label="Bar Graph", command=lambda: self.set_graph_type("bar"))
        view.add_command(label="Scatter Plot", command=lambda: self.set_graph_type("scatter"))

    def handmade_graphs(self, frame):

        entry_x = tk.Entry(frame, width=20, borderwidth=5)
        entry_y = tk.Entry(frame, width=20, borderwidth=5)
        label_x = tk.Label(frame, text="X", background='#008ECC')
        label_y = tk.Label(frame, text="Y", background='#008ECC')
        button_add = tk.Button(frame, text="Add", padx=20, pady=5, command=lambda: self.write_to_file(entry_x, entry_y))
        button_show = tk.Button(frame, text="Create", padx=30, pady=8, command=self.show_graph)

        label_x.grid(column=1, row=1, columnspan=2, sticky=tk.S)
        label_y.grid(column=4, row=1, columnspan=2, sticky=tk.S)
        entry_x.grid(column=1, row=2, columnspan=2, sticky=tk.N)
        entry_y.grid(column=4, row=2, columnspan=2, sticky=tk.N)
        button_add.grid(column=3, row=3, sticky=tk.S)
        button_show.grid(column=2, row=4, columnspan=3, sticky=tk.S)

        self.frame_config(frame)

    def API_graphs(self, frame):
        stock_label = tk.Label(frame, text="Nasdaq code of the company:", background='#008ECC')
        stock_entry = tk.Entry(frame, borderwidth=5)
        stock_button = tk.Button(frame, text="Plot", command=lambda: self.plot_stock_graph(str(stock_entry.get())))

        stock_label.grid(column=2, row=1, columnspan=3, sticky=tk.S)
        stock_entry.grid(column=2, row=3, columnspan=3, sticky=tk.N)
        stock_button.grid(column=3, row=5, sticky=tk.N)

        self.frame_config(frame)

    def frame_config(self, frame):
        frame.columnconfigure(6, minsize=50)
        frame.rowconfigure(6, minsize=50)

        col_count, row_count = frame.grid_size()

        for col in range(col_count):
            frame.grid_columnconfigure(col, minsize=50)
        for row in range(row_count):
            frame.grid_rowconfigure(row, minsize=50)

    def plot_stock_graph(self, stock_code):
        x, y = [], []

        api_key = "PUT YOUR TWELVE DATA KEY HERE"
        a = requests.get(f"https://api.twelvedata.com/avgprice?symbol={stock_code.upper()}&interval=1week&apikey={api_key}").json()

        for i in a['values']:
            d = time.mktime(dt.datetime.strptime(i['datetime'], "%Y-%m-%d").timetuple())
            f = float(i['avgprice'])
            x.append(d)
            y.append(f)

        dateconv = np.vectorize(dt.datetime.fromtimestamp)
        x = dateconv(x)

        p1 = plt.subplot2grid((1,1),(0,0))

        if self.graph_type == "line":
            plt.plot(x, y)
        elif self.graph_type == "scatter":
            plt.scatter(x, y)
        else:
            plt.bar(x, y)

        for date in p1.xaxis.get_ticklabels():
            date.set_rotation(45)
        for price in p1.yaxis.get_ticklabels():
            price.set_rotation(45)

        plt.xlabel("Date")
        plt.ylabel("AVGprice")
        plt.xticks(fontsize=7)
        plt.yticks(fontsize=7)
        plt.title(f"AVGprice graph of the {stock_code}")
        plt.subplots_adjust(left=0.16,bottom=0.212)
        plt.show()

    def write_to_file(self, entry_x, entry_y):
        x_value, y_value = entry_x.get(), entry_y.get()
        wfile = open("data.csv", "a")
        wfile.write(f"{x_value},{y_value}\n")
        wfile.close()

    def show_graph(self):
        data = open("data.csv")
        x_values, y_values = np.loadtxt(data, unpack=True, delimiter=",")
        self.plot_graph(x_values, y_values)

    def plot_graph(self, x_values, y_values):

        if self.graph_type == "line":
            plt.plot(x_values, y_values)
            plt.show()
        elif self.graph_type == "bar":
            plt.bar(x_values, y_values)
            plt.show()
        elif self.graph_type == "scatter":
            plt.scatter(x_values, y_values)
            plt.show()

    def set_graph_type(self, graph_type):
        self.graph_type = graph_type

    def text_editor(self):
        top_editor = tk.Toplevel()
        top_editor.geometry("640x360")

        toolbar_frame = tk.Frame(top_editor, borderwidth=5)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        save_button = tk.Button(toolbar_frame, padx=5, pady=5, text="save", command=lambda: self.save_event(text_box))
        save_button.pack()

        editor_frame = tk.Frame(top_editor)
        editor_frame.pack(pady=5)

        editor_scroll = tk.Scrollbar(editor_frame)
        editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        text_box = tk.Text(editor_frame, width=97, height=25, undo=True, yscrollcommand=editor_scroll.set)
        text_box.pack()

        editor_scroll.config(command=text_box.yview)

        text = open("data.csv").read()
        text_box.insert("1.0", text)

    def save_event(self, text_box):
        wfile = open("data.csv", "w")
        wfile.write(text_box.get("1.0", tk.END))
        wfile.close()

    def clear(self):
        wfile = open("data.csv", "w")
        wfile.write("")
        wfile.close()


root = tk.Tk()
app = GraphGenerator(root)
root.title("GraphGenerator")
root.resizable(width=False, height=False)
root.mainloop()