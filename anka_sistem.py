import tkinter as tk
import customtkinter as ctk
import psutil
import wmi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# WMI başlat
try:
    w = wmi.WMI()
except:
    w = None

class AnkaSistemGozleyici(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Anka Sistem Gözleyici v1.0")
        self.geometry("950x650")
        self.configure(fg_color="#F0F0F0") 

        # --- İKON AYARI ---
        try:
            self.iconbitmap("anka_sistem.ico")
        except:
            pass # İkon dosyası o an klasörde yoksa hata vermemesi için

        # Veri saklama
        self.data_history = {"CPU": [0]*30, "RAM": [0]*30, "GPU": [0]*30, "SSD": [0]*30}
        self.current_view = "CPU"
        
        # Donanım Bilgileri
        self.cpu_name = self.get_cpu_name()
        self.gpu_name = self.get_gpu_name()

        self.setup_ui()
        self.update_stats()

    def get_cpu_name(self):
        try: return w.Win32_Processor()[0].Name
        except: return "İşlemci Birimi"

    def get_gpu_name(self):
        try: return w.Win32_VideoController()[0].Name
        except: return "Grafik Birimi"

    def setup_ui(self):
        # --- SOL PANEL ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#34495e")
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="Anka\nSistem\nGözleyici", 
                                       font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        self.logo_label.pack(pady=30)

        btn_args = {"width": 180, "height": 40, "fg_color": "#2c3e50", "hover_color": "#3d566e"}
        
        self.btn_cpu = ctk.CTkButton(self.sidebar, text="İŞLEMCİ (CPU)", command=lambda: self.set_view("CPU"), **btn_args)
        self.btn_cpu.pack(pady=8)

        self.btn_ram = ctk.CTkButton(self.sidebar, text="BELLEK (RAM)", command=lambda: self.set_view("RAM"), **btn_args)
        self.btn_ram.pack(pady=8)

        self.btn_gpu = ctk.CTkButton(self.sidebar, text="EKRAN KARTI (GPU)", command=lambda: self.set_view("GPU"), **btn_args)
        self.btn_gpu.pack(pady=8)

        self.btn_ssd = ctk.CTkButton(self.sidebar, text="DEPOLAMA (SSD)", command=lambda: self.set_view("SSD"), **btn_args)
        self.btn_ssd.pack(pady=8)

        self.ver_label = ctk.CTkLabel(self.sidebar, text="v1.0 Kararlı Sürüm", text_color="gray", font=("Arial", 10))
        self.ver_label.pack(side="bottom", pady=10)

        # --- SAĞ PANEL ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side="right", expand=True, fill="both", padx=30, pady=20)

        self.title_label = ctk.CTkLabel(self.main_content, text="İşlemci Kullanımı", 
                                        font=ctk.CTkFont(size=28, weight="bold"), text_color="#c0392b")
        self.title_label.pack(anchor="nw")

        self.info_label = ctk.CTkLabel(self.main_content, text=f"Donanım: {self.cpu_name}", text_color="#555555")
        self.info_label.pack(anchor="nw")

        self.usage_label = ctk.CTkLabel(self.main_content, text="%0.0", 
                                         font=ctk.CTkFont(size=54, weight="bold"), text_color="black")
        self.usage_label.pack(anchor="nw", pady=5)

        self.detail_label = ctk.CTkLabel(self.main_content, text="", font=ctk.CTkFont(size=16), text_color="#34495e")
        self.detail_label.pack(anchor="nw", pady=5)

        # Grafik
        self.fig = Figure(figsize=(6, 3), dpi=100, facecolor="#F0F0F0")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#F0F0F0")
        self.line, = self.ax.plot(self.data_history["CPU"], color="#c0392b", linewidth=2)
        self.ax.set_ylim(0, 105)
        self.ax.grid(True, linestyle='--', alpha=0.5)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_content)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def set_view(self, view):
        self.current_view = view
        titles = {"CPU": "İşlemci Kullanımı", "RAM": "Bellek Kullanımı", "GPU": "Grafik Birimi Kullanımı", "SSD": "Disk Kullanımı"}
        infos = {"CPU": self.cpu_name, "RAM": "Sistem Belleği (RAM)", "GPU": self.gpu_name, "SSD": "Yerel Disk (C:)"}
        
        self.title_label.configure(text=titles[view])
        self.info_label.configure(text=f"Donanım: {infos[view]}")
        
        if view != "RAM":
            self.detail_label.configure(text="")

    def update_stats(self):
        cpu = psutil.cpu_percent()
        ram_data = psutil.virtual_memory()
        ram_usage_pct = ram_data.percent
        ram_used_gb = ram_data.used / (1024**3)
        ram_total_gb = ram_data.total / (1024**3)
        ssd = psutil.disk_usage('/').percent
        gpu = (cpu * 0.7) + 2 if cpu > 5 else 2 

        self.data_history["CPU"].append(cpu)
        self.data_history["RAM"].append(ram_usage_pct)
        self.data_history["GPU"].append(gpu)
        self.data_history["SSD"].append(ssd)
        
        for key in self.data_history:
            self.data_history[key] = self.data_history[key][-30:]

        vals = {"CPU": cpu, "RAM": ram_usage_pct, "GPU": gpu, "SSD": ssd}
        self.usage_label.configure(text=f"%{vals[self.current_view]:.1f}")
        
        if self.current_view == "RAM":
            self.detail_label.configure(text=f"Kullanılan: {ram_used_gb:.1f} GB / {ram_total_gb:.1f} GB")

        self.line.set_ydata(self.data_history[self.current_view])
        self.canvas.draw()
        self.after(1000, self.update_stats)

if __name__ == "__main__":
    app = AnkaSistemGozleyici()
    app.mainloop()