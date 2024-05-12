import tkinter as tk
import json
import time
import calendar
from tkinter import ttk
from datetime import datetime, timedelta
import pandas as pd
from tkinter import messagebox
import requests
from PIL import Image, ImageTk

data = json.load(open("data.json"))
indices = data["indices"]
session = requests.sessions.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
response = session.get('https://www.nseindia.com/api/live-analysis-stocksTraded', timeout=30)
if response.status_code == 200:
    x = json.loads(response.text)
    stocks = [data['symbol'] for data in x['total']['data'][1:] if data['series'] == 'EQ']
else:
    stocks = data["stocks"]
stocks.sort()

def custom_messagebox(title, message):
    # Create a Toplevel window
    popup = tk.Toplevel()
    popup.title(title)
    popup.resizable(False, False)

    # Create a label to display the message
    label = tk.Label(popup, text=message, font=("Arial", 10))
    label.pack(padx=20, pady=10)

    # Create an OK button to close the popup
    ok_button = tk.Button(popup, text="OK", command=popup.destroy)
    ok_button.pack(pady=10)

    # Make sure the popup window grabs the focus
    popup.focus_set()
    popup.grab_set()

    # Wait for the popup to be closed
    popup.wait_window()

class Market:
    def __init__(self, Scrip=None):
        self.Scrip = Scrip
        if self.Scrip:
            self.y_value = self.get_last_day_value()

    def get_last_day_value(self):
        Scrip = self.Scrip.replace('&', '%26')
        t = datetime.now() - timedelta(days=1)
        yesterday = calendar.timegm(t.timetuple()) - 19800
        value = self.get_response('1D', yesterday)
        return value

    def get_current_value(self):
        t = datetime.now()
        Time = calendar.timegm(t.timetuple()) - 19800
        val = self.get_response('1',Time)
        percentage = None
        while(not val): #sometimes server don't give data
            t = datetime.now()
            Time = calendar.timegm(t.timetuple()) - 19800
            val = self.get_response('1',Time)
        if self.y_value:
            change = (val - self.y_value)/self.y_value
            percentage = f"{change*100:.2f}"
        return val, percentage

    def get_response(self, period, Time):
        Scrip = self.Scrip.replace('&', '%26')
        NumOfCandles = 1
        if Scrip in indices.values():
            url = f"https://priceapi.moneycontrol.com//techCharts/indianMarket/index/history?symbol={Scrip}&resolution={period}&from=1&to={Time}&countback=1&currencyCode=INR"
        else:
            url = f"https://priceapi.moneycontrol.com//techCharts/indianMarket/stock/history?symbol={Scrip}&resolution={period}&from=1&to={Time}&countback=1&currencyCode=INR"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        response = requests.get(url, headers=headers)

        df = None
        try:
            if response.status_code == 200:
                data = json.loads(response.text)
                if 'error' in data['s']:
                    self.Scrip = None
                    custom_messagebox("Error", "Invalid Stock")
                    return None
                data.pop("s")
                df = pd.DataFrame(data)
                return df.at[0, 'c']
        except Exception as e:
            return None

class WidgetItem:
    def __init__(self, master):
        self.group_frame = None
        self.label = None
        self.selected_option = None
        self.dropdown = None
        self.market = Market()

    def dropdown_callback(self, event):
        selected = self.selected_option.get()
        if selected not in stocks:
            self.market.Scrip = indices[selected]
        else:
            self.market.Scrip = selected.upper()
        self.market.y_value = self.market.get_last_day_value()
        self.update_label()

    def get_dropdown_text(self, event):
        selected = self.dropdown.get()
        if selected in list(indices.keys()):
            self.market.Scrip = indices[selected]
        else:
            self.market.Scrip = selected.upper()
        self.market.y_value = self.market.get_last_day_value()
        self.update_label()

    def update_dropdown_suggestions(self, event):
        current_input = self.dropdown.get().upper()
        self.dropdown.delete(0, tk.END)
        self.dropdown.insert(0, current_input)
        suggestions = [option for option in stocks if current_input in option]
        self.dropdown['values'] = suggestions


    def update_label(self):
        if not self.market.y_value:
            self.label.config(text='')
        else:

            t_value, percentage = self.market.get_current_value()
            try:
                string = f"{t_value}, {percentage}%"
                if float(percentage) >= 0:
                    color = 'green'
                else:
                    color = 'red'
                self.label.config(text=string, fg=color)
            except Exception as e:
                print(f"Exception: {e}")
                print(t_value)

class FloatingWidgetApp:
    def __init__(self, master):
        self.market = Market()
        self.master = master
        self.master.bind("<FocusOut>", self.set_window_out_of_focus)
        self.master.title("Market Monitor")
        im = Image.open('stocks.png')
        photo = ImageTk.PhotoImage(im)
        self.master.wm_iconphoto(True, photo)
        self.master.bind("<Destroy>", self.on_close)
        self.master.resizable(False, False)

        ## Ensure the widget is always displayed but not focused
        self.master.attributes("-topmost", True)
        #self.master.grab_set()

        self.widget_groups = []
        # Create a frame for the widget
        self.create_first_group()
        self.update_labels()

    def create_first_group(self):
        widget_item = WidgetItem(self.master)
        group_frame = tk.Frame(self.master, bg='#f0f0f0', width=300, height=100, borderwidth=1, relief='groove')
        group_frame.pack(padx=10, pady=2, anchor='w')
        label = tk.Label(group_frame, text="", padx=10, width=20)
        label.grid(row=0, column=1)

        # Create a Combobox with suggestions inside the group frame
        selected_option = tk.StringVar()
        dropdown = ttk.Combobox(group_frame, textvariable=selected_option)
        dropdown.grid(row=0, column=0)
        dropdown['values'] = list(indices.keys())
        dropdown.set("Nifty 50")

        dropdown.bind("<<ComboboxSelected>>", widget_item.dropdown_callback)
        dropdown.bind("<Return>", widget_item.get_dropdown_text)
        dropdown.bind("<KeyRelease>", widget_item.update_dropdown_suggestions)

        # Create an "Add" button inside the group frame
        add_button = tk.Button(group_frame, text="+", padx=27, command=lambda: self.add_group(widget_item))
        add_button.grid(row=0, column=2)

        widget_item.group_frame = group_frame
        widget_item.label = label
        widget_item.dropdown = dropdown
        widget_item.selected_option = selected_option
        widget_item.market = Market(indices["Nifty 50"])
        self.widget_groups.append(widget_item)

    def add_group(self, parent):
        widget_item = WidgetItem(self.master)
        new_group_frame = tk.Frame(self.master, bg='#f0f0f0', width=300, height=100, borderwidth=1, relief='groove')
        new_group_frame.pack(padx=10, pady=2, anchor='w')

        label = tk.Label(new_group_frame, text="", width=20, padx=10)
        label.grid(row=0, column=1)

        selected_option = tk.StringVar()
        dropdown = ttk.Combobox(new_group_frame, textvariable=selected_option)
        dropdown['values'] = stocks
        dropdown.grid(row=0, column=0)

        dropdown.bind("<<ComboboxSelected>>", widget_item.dropdown_callback)
        dropdown.bind("<Return>", widget_item.get_dropdown_text)
        dropdown.bind("<KeyRelease>", widget_item.update_dropdown_suggestions)

        # Create an "Add" button inside the new group frame
        add_button = tk.Button(new_group_frame, text="+", command=lambda: self.add_group(widget_item))
        add_button.grid(row=0, column=2)

        # Create a "Remove" button inside the new group frame
        remove_button = tk.Button(new_group_frame, text="-", command=lambda: self.remove_group(widget_item))
        remove_button.grid(row=0, column=3)

        # Insert the new group frame after the parent group frame
        widget_item.group_frame = new_group_frame
        widget_item.label = label
        widget_item.dropdown = dropdown
        widget_item.selected_option = selected_option
        widget_item.market = Market()

        index = self.widget_groups.index(parent)
        new_index = index + 1
        self.widget_groups.insert(new_index, widget_item)

    def remove_group(self, widget_item):
        self.widget_groups.remove(widget_item)
        widget_item.group_frame.destroy()

    def update_labels(self):
        for widget_item in self.widget_groups:
            if widget_item.market.Scrip:
                widget_item.update_label()
        self.master.after(1000, self.update_labels)

    def on_close(self, event):
        data["stocks"] = sorted(stocks)
        out_file = open("data.json", "w")
        json.dump(data, out_file, indent=4)

    def set_window_out_of_focus(self, event):
        self.master.attributes("-topmost", False)

def main():
    root = tk.Tk()
    app = FloatingWidgetApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

