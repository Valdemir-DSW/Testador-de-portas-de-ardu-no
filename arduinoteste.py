import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import time
import collections

def list_serial_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

def update_ports():
    ports = list_serial_ports()
    port_selector['values'] = ports
    if ports:
        port_selector.current(0)

def connect_arduino():
    global ser, connected
    port = port_selector.get()
    if not connected:
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            connect_button.config(text="Desconectar")
            connected = True
            read_thread = threading.Thread(target=read_arduino, daemon=True)
            read_thread.start()
        except Exception as e:
            print(f"Erro: {e}")
    else:
        ser.close()
        connect_button.config(text="Conectar")
        connected = False

def read_arduino():
    global ser
    while connected:
        try:
            ser.write(b'R')
            line = ser.readline().decode().strip()
            if line:
                process_data(line)
            time.sleep(0.1)
        except:
            break

def process_data(line):
    global analog_values, digital_values, time_data, last_reset_time
    try:
        data = list(map(int, line.split(',')))
        current_time = time.time() - start_time
        time_data.append(current_time)
        for i in range(len(analog_values)):
            analog_values[i].append(data[i])
        for i in range(len(digital_values)):
            digital_values[i].append(data[i + len(analog_values)])
        if mode == 1 and current_time - last_reset_time >= 5:
            reset_data()
        update_values_display(data)
        update_plot()
    except:
        pass

def update_plot():
    ax.clear()
    ax.set_title("Leitura das Portas")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Valor (0-255)")
    ax.set_ylim(-4, 265)
    if mode == 0:
        while time_data and time_data[-1] - time_data[0] > 5:
            time_data.popleft()
            for values in analog_values:
                values.popleft()
            for values in digital_values:
                values.popleft()
    selected_ports = [i for i in range(len(analog_values)) if analog_vars[i].get()]
    selected_ports += [i+len(analog_values) for i in range(len(digital_values)) if digital_vars[i].get()]
    for i in selected_ports:
        if i < len(analog_values):
            ax.plot(time_data, analog_values[i], label=f"A{i}")
        else:
            ax.plot(time_data, digital_values[i - len(analog_values)], label=f"D{i-len(analog_values)}")
    ax.legend()
    canvas.draw()
   

def update_values_display(data):
    values_text.delete(1.0, tk.END)
    for i in range(len(analog_values)):
        values_text.insert(tk.END, f"A{i}: {data[i]}\n")
    for i in range(len(digital_values)):
        values_text.insert(tk.END, f"D{i}: {data[i + len(analog_values)]}\n")

def switch_mode():
    global mode, last_reset_time
    mode = (mode + 1) % 2
    mode_button.config(text=["Modo Corrido", "Modo 5s"][mode])
    reset_data()
    last_reset_time = time.time() - start_time

def reset_data():
    global time_data, analog_values, digital_values, start_time, last_reset_time
    start_time = time.time()
    last_reset_time = start_time
    time_data.clear()
    for i in range(len(analog_values)):
        analog_values[i].clear()
    for i in range(len(digital_values)):
        digital_values[i].clear()

root = tk.Tk()
root.title("Testador de Portas Arduino")

frame_left = tk.Frame(root)
frame_left.pack(side=tk.LEFT, padx=10, pady=10)

port_label = tk.Label(frame_left, text="Porta Serial:")
port_label.pack()

port_selector = ttk.Combobox(frame_left)
port_selector.pack()
port_selector.bind("<Button-1>", lambda e: update_ports())

connect_button = tk.Button(frame_left, text="Conectar", command=connect_arduino)
connect_button.pack()

frame_scroll = tk.Frame(frame_left)
frame_scroll.pack()
canvas_scroll = tk.Canvas(frame_scroll)
scrollbar = ttk.Scrollbar(frame_scroll, orient="vertical", command=canvas_scroll.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
frame_checkboxes = tk.Frame(canvas_scroll)
canvas_scroll.create_window((0, 0), window=frame_checkboxes, anchor="nw")
canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
canvas_scroll.config(yscrollcommand=scrollbar.set)

def on_frame_configure(event):
    canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
frame_checkboxes.bind("<Configure>", on_frame_configure)

analog_vars = []
digital_vars = []
analog_values = [collections.deque(maxlen=100) for _ in range(6)]
digital_values = [collections.deque(maxlen=100) for _ in range(14)]
time_data = collections.deque(maxlen=100)
start_time = time.time()
last_reset_time = start_time
mode = 0

for i in range(6):
    var = tk.BooleanVar(value=(i == 0))
    chk = tk.Checkbutton(frame_checkboxes, text=f"A{i}", variable=var)
    chk.pack(anchor=tk.W)
    analog_vars.append(var)

for i in range(14):
    var = tk.BooleanVar(value=(i == 0))
    chk = tk.Checkbutton(frame_checkboxes, text=f"D{i}", variable=var)
    chk.pack(anchor=tk.W)
    digital_vars.append(var)

mode_button = tk.Button(frame_left, text="Modo Corrido", command=switch_mode)
mode_button.pack()

fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

values_text = tk.Text(root, height=20, width=20)
values_text.pack(side=tk.RIGHT, padx=10, pady=10)

connected = False
ser = None

update_plot()

root.mainloop()