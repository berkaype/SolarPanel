import tkinter as tk
from tkinter import ttk, messagebox

class SolarPanelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Güneş Paneli Şarj Süresi Hesaplayıcı")
        self.root.geometry("1200x600")

        # Create a main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=1)

        # Create a canvas
        canvas = tk.Canvas(main_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # Add a scrollbar to the canvas
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create another frame inside the canvas
        self.scrollable_frame = tk.Frame(canvas)

        # Add that new frame to a window in the canvas
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.panel_frame = ttk.LabelFrame(self.scrollable_frame, text="Panel ile Alakalı Bilgiler", padding=(20, 10))
        self.panel_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.create_panel_input(self.panel_frame)

        self.device_frame = ttk.LabelFrame(self.scrollable_frame, text="Cihazlar", padding=(20, 10))
        self.device_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.device_inputs = []
        self.create_device_input(self.device_frame)

        self.add_device_button = ttk.Button(self.scrollable_frame, text="+ Cihaz Ekle", command=self.add_device_input)
        self.add_device_button.grid(row=1, column=0, padx=0, pady=0)

        self.calculate_button = ttk.Button(self.scrollable_frame, text="Hesapla", command=self.calculate)
        self.calculate_button.grid(row=3, column=0, padx=20, pady=10)

        self.result_output = tk.Text(self.scrollable_frame, height=10, width=140)
        self.result_output.grid(row=4, column=0, padx=20, pady=10)

        # Scrollbar ekleyin
        result_scrollbar = tk.Scrollbar(self.scrollable_frame, orient=tk.VERTICAL, command=self.result_output.yview)
        result_scrollbar.grid(row=4, column=1, sticky='ns')

        # Text widget'ı scrollbar ile ilişkilendirin
        self.result_output.config(yscrollcommand=result_scrollbar.set)

    def create_panel_input(self, container):
        self.panel_power_var = tk.StringVar()
        self.sunlight_intensity_var = tk.StringVar()
        self.panel_area_var = tk.StringVar()
        self.conversion_efficiency_var = tk.StringVar()
        self.overall_efficiency_var = tk.StringVar()
        self.sun_time_var = tk.StringVar()

        ttk.Label(container, text="Panel Gücü (W):").grid(row=0, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.panel_power_var).grid(row=0, column=1, sticky="ew")

        ttk.Label(container, text="Güneş Işını Şiddeti (W/m2):").grid(row=1, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.sunlight_intensity_var).grid(row=1, column=1, sticky="ew")

        ttk.Label(container, text="Panel Yüzey Alanı (m2):").grid(row=2, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.panel_area_var).grid(row=2, column=1, sticky="ew")

        ttk.Label(container, text="Panel Güneş Işını Dönüştürme Verimliliği (%):").grid(row=3, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.conversion_efficiency_var).grid(row=3, column=1, sticky="ew")

        ttk.Label(container, text="Panel Çevrimi Verimlilik Yüzdesi (%):").grid(row=4, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.overall_efficiency_var).grid(row=4, column=1, sticky="ew")

        ttk.Label(container, text="Panel Güneşlenme Süresi (saat):").grid(row=6, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.sun_time_var).grid(row=6, column=1, sticky="ew")

        self.control_button = ttk.Button(container, text="Kontrol", command=self.check_panel_efficiency)
        self.control_button.grid(row=5, column=0, sticky="ew", columnspan=2)


        self.control_message = ttk.Label(container, text="")
        self.control_message.grid(row=5, column=2, columnspan=2)

        # Tablo
        lux_table_text = """
                      100 lux: Kapalı Hava
                300 – 500 lux: Bulutsuz bir günde Günbatımı / Gündoğumu
                    1,000 lux: Parçalı Bulutlu
          10,000 – 25,000 lux: Açık Hava Gün Işığı (indirekt)
         32,000 – 130,000 lux: Direk Gün Işığı
        """
        lux_table = tk.Text(container, height=7, width=80)
        lux_table.grid(row=0, column=2, rowspan=7, padx=60)
        lux_table.insert(tk.END, lux_table_text)
        lux_table.config(state="disabled")
        # Lux - W/m2 çevirici
        ttk.Label(container, text="Lux:", width=4, anchor="w").grid(row=8, column=2, padx=10, sticky="w")
        self.lux_input_var = tk.StringVar()

        ttk.Entry(container, textvariable=self.lux_input_var, width=10).grid(row=8, column=2, padx=40 , sticky="w")

        convert_button = ttk.Button(container, text="Dönüştür", command=self.convert_lux_to_watt_per_m2, width=10)
        convert_button.grid(row=8, column=2, padx=100, sticky="w")

        self.watt_per_m2_output_var = tk.StringVar()
        ttk.Label(container, textvariable=self.watt_per_m2_output_var, width=40).grid(row=8, column=2, padx=200, sticky="w")

    def convert_lux_to_watt_per_m2(self):
        try:
            lux_value = float(self.lux_input_var.get())
            watt_per_m2_value = lux_value * 0.0079
            self.watt_per_m2_output_var.set(f"{watt_per_m2_value:.2f} W/m²")
        except ValueError:
            self.watt_per_m2_output_var.set("Geçersiz değer")

    def create_device_input(self, container, values=None):
        device_name_var = tk.StringVar()
        capacity_unit_var = tk.StringVar()
        capacity_var = tk.StringVar()
        voltage_var = tk.StringVar()
        charging_cycles_var = tk.StringVar()

        row = len(self.device_inputs)

        ttk.Label(container, text="Cihaz İsmi").grid(row=row, column=0, sticky="w")
        ttk.Entry(container, textvariable=device_name_var).grid(row=row, column=1, sticky="ew")

        ttk.Label(container, text="Kapasite Birimi").grid(row=row, column=2, sticky="w")
        unit_combo = ttk.Combobox(container, textvariable=capacity_unit_var, values=["mAh", "Wh"])
        unit_combo.grid(row=row, column=3, sticky="ew")

        ttk.Label(container, text="Pil Kapasitesi").grid(row=row, column=4, sticky="w")
        ttk.Entry(container, textvariable=capacity_var).grid(row=row, column=5, sticky="ew")

        ttk.Label(container, text="Pil Gerilimi (V)").grid(row=row, column=6, sticky="w")
        ttk.Entry(container, textvariable=voltage_var).grid(row=row, column=7, sticky="ew")

        ttk.Label(container, text="Şarj Sayısı").grid(row=row, column=8, sticky="w")
        ttk.Entry(container, textvariable=charging_cycles_var).grid(row=row, column=9, sticky="ew")

        delete_button = ttk.Button(container, text="-", command=lambda row=row: self.delete_device_input(row))
        delete_button.grid(row=row, column=10, sticky="ew")

        if values:
            device_name_var.set(values["name"])
            capacity_unit_var.set(values["unit"])
            capacity_var.set(values["capacity"])
            voltage_var.set(values["voltage"])
            charging_cycles_var.set(values["cycles"])

        self.device_inputs.append({
            "name": device_name_var,
            "unit": capacity_unit_var,
            "capacity": capacity_var,
            "voltage": voltage_var,
            "cycles": charging_cycles_var,
            "delete_button": delete_button
        })

    def add_device_input(self):
        self.create_device_input(self.device_frame)
        current_height = int(self.result_output.cget("height"))
        self.result_output.config(height=current_height + 1)        

    def delete_device_input(self, row):
        self.device_inputs.pop(row)  # Remove the deleted device from the list
        for widget in self.device_frame.grid_slaves():
            if int(widget.grid_info()["row"]) == row:
                widget.grid_forget()
                widget.destroy()


    def check_panel_efficiency(self):
        try:
            panel_power = float(self.panel_power_var.get())
            sunlight_intensity = float(self.sunlight_intensity_var.get())
            panel_area = float(self.panel_area_var.get())
            conversion_efficiency = float(self.conversion_efficiency_var.get())
            calculated_power = sunlight_intensity * panel_area * conversion_efficiency / 100
            if calculated_power < panel_power:
                self.control_message.config(text="Dikkat Panel yeterince güneş ışığı almıyor!", foreground="red")
            else:
                self.control_message.config(text="Panel yeterince güneş ışığı alıyor!", foreground="green")
        except ValueError:
            self.control_message.config(text="Lütfen tüm alanları doğru doldurun!", foreground="red")

    def calculate(self):
        try:
            panel_power = float(self.panel_power_var.get())
            overall_efficiency = float(self.overall_efficiency_var.get())
            sun_time = self.sun_time_var.get()

            devices = []
            for device_input in self.device_inputs:
                name = device_input["name"].get()
                capacity_unit = device_input["unit"].get()
                capacity = float(device_input["capacity"].get())
                voltage = float(device_input["voltage"].get())
                cycles = float(device_input["cycles"].get())
                capacity = capacity if capacity_unit == "Wh" else capacity * voltage / 1000
                devices.append({"name": name, "capacity": capacity, "voltage": voltage, "charging_cycles": cycles})

            panel_power_after_eff = panel_power * overall_efficiency / 100
            total_device_capacity = sum(device["capacity"] * device["charging_cycles"] for device in devices)

            output_text = ""

            if panel_power_after_eff >= total_device_capacity:
                    output_text += "Güneş paneli kapasitesi, sisteme takılı olan cihazlar için yeterli!\n"
            else:
                    output_text += f"Güneş panelinden bazı cihazları çıkarın!\n"

            if sun_time:
                sun_time = float(sun_time)
            else:
                sun_time_required = max(device["capacity"] * device["charging_cycles"] / (device["voltage"] * 2 * 0.8) for device in devices)
                output_text += f"Gerekli olan güneşlenme süresi {sun_time_required:.2f} saat.\n"

            for device in devices:
                charging_time_hours = device["capacity"] * device["charging_cycles"] / (device["voltage"] * 2 * 0.8)
                output_text += f"{device['name']} şarj olma süresi: {charging_time_hours:.2f} saat, Kapasite: {device['capacity']} Wh \n"


            self.result_output.delete(1.0, tk.END)
            self.result_output.insert(tk.END, output_text)

        except ValueError:
            messagebox.showerror("Hata", "Lütfen tüm alanları doğru doldurun!")

if __name__ == "__main__":
    root = tk.Tk()
    app = SolarPanelApp(root)
    root.mainloop()
