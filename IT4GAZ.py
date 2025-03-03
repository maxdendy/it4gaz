import tkinter as tk
from tkinter import ttk, messagebox
import requests
from matplotlib.ticker import AutoLocator
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def create_plot(data, names):
    # Extract time and data
    time = [row[0] for row in data]
    values = [[item for item in row[1:]] for row in data]

    # Number of data series
    num_plots = len(values[0])

    # Create subplots
    fig, axes = plt.subplots(num_plots, 1, figsize=(10, 6 * num_plots))

    # If there's only one plot, axes will not be a list but a single object
    if num_plots == 1:
        axes = [axes]

    # Plot the graphs
    for i in range(num_plots):
        axes[i].plot(time, [row[i] for row in values])
        axes[i].set_ylabel(names[i + 1], rotation=0, ha='right', va='center')
        axes[i].yaxis.set_label_coords(-0.075, 0.5)
        axes[i].grid(True)
        axes[i].xaxis.set_major_locator(AutoLocator())  # Automatic X-axis scaling

        # Format the X-axis labels to show date and time in separate lines
        axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M:%S'))

        if i != num_plots - 1:
            axes[i].set_xticklabels([])  # Hide X-axis labels
            axes[i].set_xlabel('')

    # Adjust subplot spacing
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.2, bottom=0.05)

    return fig


class GAZ:
    def __init__(self, root):
        self.root = root
        self.root.title("IT4GAZ")
        self.root.minsize(1200, 800)  # Minimum window size constraint

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Increased font size
        self.large_font = ('Arial', 13)

        # Frame for date and time input
        self.input_frame = ttk.Frame(self.root)
        self.input_frame.pack(side="left", padx=10, pady=20, fill="y")

        # Start date
        ttk.Label(self.input_frame, text="Начальная дата:", font=self.large_font).grid(row=0, column=0, columnspan=7,
                                                                                       pady=5, sticky="S")
        self.start_date = DateEntry(self.input_frame, width=9, background='darkblue', foreground='white', borderwidth=1,
                                    date_pattern='dd.mm.yyyy', locale='ru_RU', font=self.large_font)
        self.start_date.grid(row=1, column=0, columnspan=7, sticky="S")

        # Set the start date to January 1, 2024
        self.start_date.set_date(datetime(2024, 1, 1))

        # Start time
        ttk.Label(self.input_frame, text="Начальное время:", font=self.large_font).grid(row=2, column=0, columnspan=7,
                                                                                        pady=5, sticky="S")
        self.start_hour_entry = self.create_time_entry(self.input_frame, 3, 1, "0")
        self.start_minute_entry = self.create_time_entry(self.input_frame, 3, 3, "0")
        self.start_second_entry = self.create_time_entry(self.input_frame, 3, 5, "0")
        # Separators
        tk.Label(self.input_frame, text=":", font=self.large_font).grid(row=3, column=2, padx=0)
        tk.Label(self.input_frame, text=":", font=self.large_font).grid(row=3, column=4, padx=0)

        # End date
        ttk.Label(self.input_frame, text="Конечная дата:", font=self.large_font).grid(row=4, column=0, columnspan=7,
                                                                                      pady=5, sticky="S")
        self.end_date = DateEntry(self.input_frame, width=9, background='darkblue', foreground='white', borderwidth=1,
                                  date_pattern='dd.mm.yyyy', locale='ru_RU', font=self.large_font)
        self.end_date.grid(row=5, column=0, columnspan=7, sticky="S")
        # Set the default end date to the next day
        self.set_default_end_date()

        # End time
        ttk.Label(self.input_frame, text="Конечное время:", font=self.large_font).grid(row=6, column=0, columnspan=7,
                                                                                       pady=5, sticky="S")
        self.end_hour_entry = self.create_time_entry(self.input_frame, 7, 1, "0")
        self.end_minute_entry = self.create_time_entry(self.input_frame, 7, 3, "0")
        self.end_second_entry = self.create_time_entry(self.input_frame, 7, 5, "0")
        # Separators
        tk.Label(self.input_frame, text=":", font=self.large_font).grid(row=7, column=2, padx=0)
        tk.Label(self.input_frame, text=":", font=self.large_font).grid(row=7, column=4, padx=0)

        # Placeholders (to keep separators close to the input_frame for time)
        tk.Label(self.input_frame, text="     ", font=self.large_font).grid(row=3, column=0)
        tk.Label(self.input_frame, text="     ", font=self.large_font).grid(row=3, column=6)

        # Button
        self.plot_button = ttk.Button(self.input_frame, text="Выполнить", command=self.plot_data, style="Large.TButton")
        self.plot_button.grid(row=8, column=0, columnspan=7, sticky="S", pady=20)

        # Style for the enlarged button
        style = ttk.Style()
        style.configure("Large.TButton", font=self.large_font, padding=7)

        # Frame for displaying the graph and table
        self.graph_frame = ttk.Frame(self.root)
        self.graph_frame.pack(side="right", padx=10, pady=10, expand=True, fill='both')

        # Set white background for the graph and table frame
        self.graph_frame.configure(style="White.TFrame")
        style.configure("White.TFrame", background="white")

        self.graph_frame.pack_propagate(False)

        # Create a Notebook
        self.notebook = ttk.Notebook(self.graph_frame)
        self.notebook.pack(expand=True, fill='both')

        # Tabs
        self.tab_graph = ttk.Frame(self.notebook, style="White.TFrame")
        self.notebook.add(self.tab_graph, text="График")
        self.tab_table = ttk.Frame(self.notebook, style="White.TFrame")
        self.notebook.add(self.tab_table, text="Таблица")

    def set_default_end_date(self):
        # Get the current date
        today = datetime.today()
        # Set the end date to the next day
        next_day = today + timedelta(days=1)
        self.end_date.set_date(next_day)

    def create_time_entry(self, parent, row, column, default_value="0"):
        entry = tk.Entry(parent, textvariable=tk.StringVar(), width=2, font=self.large_font)
        entry.grid(row=row, column=column)
        entry.insert(0, default_value)
        # Bind event for real-time validation
        entry.bind("<FocusOut>", self.validate_time_entry)
        return entry

    def validate_time_entry(self, event):
        entry = event.widget
        value = entry.get()
        try:
            # Check if the value is a number
            int_value = int(value)
            # Check valid ranges
            if entry in [self.start_hour_entry, self.end_hour_entry]:
                if not (0 <= int_value <= 23):
                    entry.delete(0, tk.END)
                    entry.insert(0, "0")
            elif entry in [self.start_minute_entry, self.start_second_entry,
                           self.end_minute_entry, self.end_second_entry]:
                if not (0 <= int_value <= 59):
                    entry.delete(0, tk.END)
                    entry.insert(0, "0")
        except ValueError:
            # If the value is not a number, replace it with 0
            entry.delete(0, tk.END)
            entry.insert(0, "0")

    def get_data(self):
        # Get values from input fields
        start_date = self.start_date.get()
        start_time = f"{self.start_hour_entry.get()}:{self.start_minute_entry.get()}:{self.start_second_entry.get()}"
        end_date = self.end_date.get()
        end_time = f"{self.end_hour_entry.get()}:{self.end_minute_entry.get()}:{self.end_second_entry.get()}"

        # Convert to datetime object
        try:
            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%d.%m.%Y %H:%M:%S")
            end_datetime = datetime.strptime(f"{end_date} {end_time}", "%d.%m.%Y %H:%M:%S")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date or time format: {e}")
            return None, None

        # Check that the end date is not earlier than the start date
        if end_datetime < start_datetime:
            messagebox.showerror("Error", "End date cannot be earlier than the start date")
            return None, None

        # Get data and headers
        url = "http://127.0.0.1:5000/data"
        params = {"start_date": start_datetime, "end_date": end_datetime}

        try:
            response = requests.get(url, params=params, timeout=5)
            print("Статус-код:", response.status_code)

            if response.status_code != 200:
                print("Ошибка сервера:", response.text)
            else:
                try:
                    data = response.json()
                    processed_data = []
                    for row in data:
                        date_str = row[1]
                        date_obj = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S GMT")
                        processed_data.append([date_obj] + row[2:14])
                    data = processed_data
                    print(data)
                    return data
                except requests.exceptions.JSONDecodeError:
                    print("Ошибка: сервер вернул не JSON, а:", response.text)
        except requests.exceptions.RequestException as e:
            print("Ошибка запроса:", e)

    def plot_data(self):
        try:
            data = self.get_data()
            names = ['Time', 'T1_K_1', 'T1_K_3', 'T1_K_2', 'T1_L_1', 'T1_L_2', 'T1_L_3', 'T1_R_1', 'T1_R_2',
                     'T1_R_3', 'T1_Up_1', 'T1_Up_2', 'T1_Up_3', 'T_1']
            if data is None:
                return

            # Clear the previous graph if it exists
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()

            # Build a new graph
            fig = create_plot(data, names)
            self.canvas = FigureCanvasTkAgg(fig, master=self.tab_graph)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(expand=True, fill='both')

            # Create a table
            self.create_table(data, names)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_table(self, data, names):
        # Clear the previous table if it exists
        for widget in self.tab_table.winfo_children():
            widget.destroy()

        # Create a Treeview
        columns = names  # Use names as column headers
        self.tree = ttk.Treeview(self.tab_table, columns=columns, show="headings")

        # Configure headers and columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, stretch=False)  # All columns have the same width

        # Add data to the table
        for row in data:
            # Convert the first column (time) to a string for display
            formatted_row = [row[0].strftime("%Y-%m-%d %H:%M:%S")] + list(row[1:])
            self.tree.insert("", "end", values=formatted_row)

        # Add scrollbars
        vsb = ttk.Scrollbar(self.tab_table, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(self.tab_table, orient="horizontal", command=self.tree.xview)
        hsb.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=hsb.set)

        # Place the table
        self.tree.pack(expand=True, fill="both")

    def on_close(self):
        self.root.destroy()
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = GAZ(root)
    root.mainloop()
