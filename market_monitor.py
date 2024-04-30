import tkinter as tk
import json
import time
import calendar
from datetime import datetime, timedelta
import pandas as pd
from tkinter import ttk
from tkinter import messagebox
import requests

indices = {'Nifty midcap 50': 'in%3Bccx', "Nifty 50": 'in%3BNSX', "Nifty bank":"in%3Bnbx"}

def get_last_day_value(Scrip):
    t = datetime.now() - timedelta(days=1)
    yesterday = calendar.timegm(t.timetuple()) - 19800
    NumOfCandles = 1
    if Scrip in indices.values():
        url = f"https://priceapi.moneycontrol.com//techCharts/indianMarket/index/history?symbol={Scrip}&resolution=1D&from=1&to={yesterday}&countback=1&currencyCode=INR"
    else:
        url = f"https://priceapi.moneycontrol.com//techCharts/indianMarket/stock/history?symbol={Scrip}&resolution=1D&from=1&to={yesterday}&countback=1&currencyCode=INR"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    y_value = 0
    if response.status_code == 200:
        data = json.loads(response.text)
        data.pop("s")
        df = pd.DataFrame(data)
        return df.at[0, 'c']

Scrip = indices['Nifty 50']
y_value = get_last_day_value(Scrip)
class FloatingWidgetApp:
    def __init__(self, master):
        self.master = master
        master.title("Market Monitor")

        # Create a frame for the widget
        self.frame = tk.Frame(master, bg='#f0f0f0', width=300, height=100, borderwidth=2, relief='groove')
        self.frame.pack_propagate(0)  # Don't allow frame to shrink
        self.frame.pack()

        # Create the first label inside the frame
        self.label1 = tk.Label(self.frame, text="Floating Widget", bg='#f0f0f0', font=('Arial', 12))
        self.label1.pack(expand=True, fill='both', pady=5)

        # Create a Text widget inside the frame
        self.textbox = tk.Entry(master, bg='white', font=('Arial', 10))
        self.textbox.pack(expand=True, fill='both', padx=10, pady=(0, 5))
        self.textbox.bind("<Return>", self.on_enter_pressed)
        self.textbox.bind("<KeyRelease>", self.convert_to_uppercase)

        # Create a stylish dropdown menu
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use a predefined theme for ttk widgets
        self.style.configure('TCombobox', foreground='black', background='#f0f0f0', bordercolor='#aaaaaa')
        self.selected_option = tk.StringVar(master)
        self.selected_option.set("Nifty 50")  # Default value
        self.dropdown = ttk.Combobox(master, textvariable=self.selected_option, values=["Nifty 50", "Nifty bank", 'Nifty midcap 50'], state='readonly', width=15)
        self.dropdown.pack(fill='both', padx=10, pady=5)

        # Bind mouse events to allow dragging the widget
        self.frame.bind("<ButtonPress-1>", self.start_move)
        self.frame.bind("<B1-Motion>", self.on_move)

        # Keep the widget always on top
        #self.master.attributes("-topmost", True)

        # Add callback for dropdown selection
        self.dropdown.bind("<<ComboboxSelected>>", self.dropdown_callback)

        # Start the periodic update of label1
        self.update_label1()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")

    def dropdown_callback(self, event):
        global Scrip, y_value
        self.textbox.delete(0, tk.END)
        selected = self.selected_option.get()
        Scrip = indices[selected]
        y_value = get_last_day_value(Scrip)
        self.get_data(Scrip)

    def get_data(self, Scrip):
        t_value = getdata(Scrip)
        if t_value == -1:
            self.label1.config(text='')
        change = (t_value - y_value)/y_value
        string = f"{t_value}, {change*100:.2f}%"
        self.label1.config(text=string)
        #self.label2.config(text="Another text")

    def update_label1(self):
        # Update label1 with fresh data
        self.get_data(Scrip)
        # Schedule the next update after 1 minute (60000 milliseconds)
        self.master.after(10000, self.update_label1)

    def on_enter_pressed(self, event):
        # Call a function when Enter key is pressed in the textbox
        global y_value, Scrip
        entered_text = self.textbox.get()#.upper()  # Get text from the textbox
        #self.textbox.delete(0, tk.END)
        #self.textbox.insert(0, entered_text)
        Scrip = entered_text
        y_value = get_last_day_value(Scrip)
        self.get_data(Scrip)
        # Add your function call here

    def convert_to_uppercase(self, event):
        # Convert the text in the entry widget to uppercase
        text = self.textbox.get().upper()
        self.textbox.delete(0, tk.END)
        self.textbox.insert(0, text)
    #def select_text(self, event):
    #    # Select text in the textbox when it receives focus
    #    self.textbox.tag_add("sel", "1.0", "end")

def getdata(Scrip):
    t = datetime.now()
    Scrip = Scrip.replace('&', '%26')
    Time = calendar.timegm(t.timetuple()) - 19800
    NumOfCandles = 1
    if Scrip in indices.values():
        url = f"https://priceapi.moneycontrol.com//techCharts/indianMarket/index/history?symbol={Scrip}&resolution=1&from=1&to={Time}&countback=1&currencyCode=INR"
    else:
        url = f"https://priceapi.moneycontrol.com//techCharts/indianMarket/stock/history?symbol={Scrip}&resolution=1&from=1&to={Time}&countback=1&currencyCode=INR"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)

    df = None
    if response.status_code == 200:
        data = json.loads(response.text)
        if 'error' in data['s']:
            messagebox.showerror("Error")
            return -1
        data.pop("s")
        df = pd.DataFrame(data)
        return df.at[0, 'c']

def main():
    root = tk.Tk()
    app = FloatingWidgetApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

