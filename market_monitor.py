import tkinter as tk
import json
import time
import calendar
from datetime import datetime, timedelta
import pandas as pd
from tkinter import ttk
from tkinter import messagebox
import requests

indices = json.load(open("data.json"))["indices"]
stocks = json.load(open("data.json"))["stocks"]
class Market:
    def __init__(self):
        self.Scrip = None #indices['Nifty 50']
        if self.Scrip:
            self.y_value = self.get_last_day_value(self.Scrip)

    def get_last_day_value(self, Scrip):
        Scrip = Scrip.replace('&', '%26')
        t = datetime.now() - timedelta(days=1)
        yesterday = calendar.timegm(t.timetuple()) - 19800
        value = self.get_response(Scrip, '1D', yesterday)
        return value

    def getdata(self, Scrip):
        t = datetime.now()
        Time = calendar.timegm(t.timetuple()) - 19800
        return self.get_response(Scrip, '1',Time)

    def get_response(self, Scrip, period, Time):
        Scrip = Scrip.replace('&', '%26')
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
        if response.status_code == 200:
            data = json.loads(response.text)
            if 'error' in data['s']:
                messagebox.showerror("Error")
                return -1
            data.pop("s")
            df = pd.DataFrame(data)
            return df.at[0, 'c']

class WidgetItem:
    def __init__(self, master):
        self.group_frame = tk.Frame(master, bg='#f0f0f0', width=600, height=100, borderwidth=1, relief='groove')
        self.label = tk.Label(self.group_frame, text="22000", padx=10, width=30)
        self.selected_option = tk.StringVar()
        self.dropdown = ttk.Combobox(self.group_frame, textvariable=self.selected_option)
        self.market = Market()

    def dropdown_callback(self, event):
        selected = self.selected_option.get()
        if selected not in stocks:
            self.market.Scrip = indices[selected]
        else:
            self.market.Scrip = selected
        self.market.y_value = self.market.get_last_day_value(self.market.Scrip)
        self.get_data()

    def get_dropdown_text(self, event):
        selected = self.dropdown.get()
        if selected in list(indices.keys()):
            self.market.Scrip = indices[selected]
        else:
            self.market.Scrip = selected
        self.market.y_value = self.market.get_last_day_value(self.market.Scrip)
        self.get_data()

    def get_data(self):
        t_value = self.market.getdata(self.market.Scrip)
        if t_value == -1:
            self.label.config(text='')
        change = (t_value - self.market.y_value)/self.market.y_value
        string = f"{t_value}, {change*100:.2f}%"
        if change >= 0:
            color = 'green'
        else:
            color = 'red'
        self.label.config(text=string, fg=color)

class FloatingWidgetApp:
    def __init__(self, master):
        self.market = Market()
        self.master = master
        master.title("Market Monitor")

        self.widget_groups = []
        # Create a frame for the widget
        self.create_group()
        #self.master.attributes("-topmost", True)
        self.update_labels()

    def create_group(self):
        widget_item = WidgetItem(self.master)
        group_frame = tk.Frame(self.master, bg='#f0f0f0', width=600, height=100, borderwidth=1, relief='groove')
        group_frame.pack(padx=10, pady=2, anchor='w')
        # Create a label inside the group frame
        label = tk.Label(group_frame, text="", padx=10, width=30)
        label.grid(row=0, column=1)
        # Initialize available options for the Combobox
        self.indices_options = list(indices.keys())
        self.stock_options = stocks

        # Create a Combobox with suggestions inside the group frame
        selected_option = tk.StringVar()
        dropdown = ttk.Combobox(group_frame, textvariable=selected_option)
        dropdown['values'] = self.indices_options
        dropdown.bind("<<ComboboxSelected>>", widget_item.dropdown_callback)
        dropdown.bind("<Return>", widget_item.get_dropdown_text)
        dropdown.grid(row=0, column=0)

        # Bind the <KeyRelease> event to update suggestions
        #dropdown.bind("<KeyRelease>", self.update_suggestions)

        # Create an "Add" button inside the group frame
        add_button = tk.Button(group_frame, text="+", padx=20, command=lambda: self.add_group(widget_item))
        add_button.grid(row=0, column=2)

        # Add the group frame to the list

        widget_item.group_frame = group_frame
        widget_item.label = label
        widget_item.dropdown = dropdown
        widget_item.selected_option = selected_option
        widget_item.market = Market()
        self.widget_groups.append(widget_item)

        ## Bind mouse events to allow dragging the widget
        #self.frame.bind("<ButtonPress-1>", self.start_move)
        #self.frame.bind("<B1-Motion>", self.on_move)

        ## Keep the widget always on top

        ## Add callback for dropdown selection
        #self.dropdown.bind("<<ComboboxSelected>>", self.dropdown_callback)

        ## Ensure the widget is always displayed but not focused
        ##self.master.overrideredirect(True)
        ##self.master.grab_set()
        ## Start the periodic update of label1
        #self.update_label1()

    #def update_suggestions(self, event):
    #    current_input = self.dropdown.get().lower()
    #    suggestions = [option for option in self.all_options if current_input in option.lower()]
    #    self.dropdown['values'] = suggestions
    #    #self.dropdown.event_generate("<Button-1>")

    def add_group(self, parent):
        # Create a new group frame
        widget_item = WidgetItem(self.master)
        new_group_frame = tk.Frame(self.master, bg='#f0f0f0', width=600, height=100, borderwidth=1, relief='groove')
        new_group_frame.pack(padx=10, pady=2, anchor='w')

        # Create a label inside the new group frame
        label = tk.Label(new_group_frame, text="0", width=30, padx=10)
        label.grid(row=0, column=1)

        # Initialize available options for the new Combobox

        # Create a Combobox with suggestions inside the new group frame
        selected_option = tk.StringVar()
        dropdown = ttk.Combobox(new_group_frame, textvariable=selected_option)
        dropdown.bind("<<ComboboxSelected>>", widget_item.dropdown_callback)
        dropdown.bind("<Return>", widget_item.get_dropdown_text)
        dropdown['values'] = self.stock_options
        dropdown.grid(row=0, column=0)

        # Bind the <KeyRelease> event to update suggestions
        #dropdown.bind("<KeyRelease>", self.update_suggestions)

        # Create an "Add" button inside the new group frame
        add_button = tk.Button(new_group_frame, text="+", command=lambda: self.add_group(widget_item))
        add_button.grid(row=0, column=2)

        # Create a "Remove" button inside the new group frame
        remove_button = tk.Button(new_group_frame, text="-", command=lambda: self.remove_group(widget_item))
        remove_button.grid(row=0, column=3)

        # Insert the new group frame after the parent group frame
        index = self.widget_groups.index(parent)
        new_index = index + 1
        widget_item.group_frame = new_group_frame
        widget_item.label = label
        widget_item.dropdown = dropdown
        widget_item.selected_option = selected_option
        widget_item.market = Market()
        self.widget_groups.insert(new_index, widget_item)

    def remove_group(self, widget_item):
        # Remove the specified group frame from the list and destroy it
        self.widget_groups.remove(widget_item)
        widget_item.group_frame.destroy()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")


    def update_labels(self):
        # Update labels with current time every 5 seconds
        for widget_item in self.widget_groups:
            if widget_item.market.Scrip:
                widget_item.get_data()
        # Schedule next update after 5 seconds
        self.master.after(5000, self.update_labels)

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

def main():
    root = tk.Tk()
    app = FloatingWidgetApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

