import os
import platform
import socket
import subprocess
import time

from cpuinfo import get_cpu_info
import psutil

if platform.system() == "Windows":
    import wmi
else:
    wmi = None


def cpu_info():
    print("\n--- Информация о процессоре ---")
    cpu_details = get_cpu_info()
    print(f"Модель: {cpu_details.get('brand_raw', platform.processor())}")
    print(f"Физические ядра: {psutil.cpu_count(logical=False)}")
    print(f"Логические ядра: {psutil.cpu_count(logical=True)}")

    freq = psutil.cpu_freq()
    if freq:
        print(f"Текущая частота: {freq.current:.2f} МГц")

    print(f"Кэш L2: {cpu_details.get('l2_cache_size', 'Не определен')} байт")
    print(f"Кэш L3: {cpu_details.get('l3_cache_size', 'Не определен')} байт")
    print(f"Нагрузка: {psutil.cpu_percent(interval=0.5)}%")


def ram_info():
    print("\n--- Информация о памяти ---")
    ram = psutil.virtual_memory()
    print(f"Объем ОЗУ: {ram.total / (1024**3):.2f} ГБ")
    print(f"Использовано ОЗУ: {ram.used / (1024**3):.2f} ГБ ({ram.percent}%)")


def disk_info():
    print("\n--- Информация о дисках ---")
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            print(f"Раздел {partition.device} ({partition.fstype}):")
            print(f"  Общая емкость: {usage.total / (1024**3):.2f} ГБ")
            print(f"  Свободно: {usage.free / (1024**3):.2f} ГБ")
        except PermissionError:
            # Некоторые системные разделы могут быть недоступны
            continue

    if platform.system() == "Windows" and wmi:
        print("\nФизические устройства:")
        for disk in wmi.WMI().Win32_DiskDrive():
            print(f" Накопитель: {disk.Model} | Интерфейс: {disk.InterfaceType}")
    else:
        print("\nФизические устройства:")
        try:
            d = subprocess.check_output(["lsblk", "-d", "-e", "7", "-o", "MODEL,SIZE"])
            print(d.decode('utf-8').strip())
        except FileNotFoundError:
            print("Утилита lsblk недоступна.")


def videocard_info():
    print("\n--- Информация о видеокарте ---")
    if platform.system() == "Windows" and wmi:
        for video in wmi.WMI().Win32_VideoController():
            print(f"Модель видеокарты: {video.Name}")
            raw_ram = video.AdapterRAM or 0
            if int(raw_ram) <= 0:
                gpu_ram_mb = "Более 4096 или не определено"
            else:
                gpu_ram_mb = f"{int(raw_ram) / (1024**2):.0f}"
            print(f"Объем видеопамяти: {gpu_ram_mb} МБ")
            if hasattr(video, 'CurrentBitsPerPixel') and video.CurrentBitsPerPixel:
                print(f"Разрядность: {video.CurrentBitsPerPixel} бит")
    else:
        try:
            output = subprocess.check_output(["lspci"]).decode('utf-8')
            for line in output.split('\n'):
                if "vga" in line.lower() or "3d" in line.lower():
                    print(line.strip())
        except FileNotFoundError:
            print("Утилита lspci недоступна.")


def network_info():
    print("\n--- Сетевая информация ---")
    print(f"Имя компьютера: {socket.gethostname()}")
    for interface_name, addresses in psutil.net_if_addrs().items():
        for addr in addresses:
            if addr.family == socket.AF_INET:
                print(f"Интерфейс: {interface_name} -> IP-адрес: {addr.address}")


def info_print():
    print("\n" + "="*30)
    print("1. Показать информацию о процессоре.")
    print("2. Показать информацию о памяти.")
    print("3. Показать информацию о дисках.")
    print("4. Показать информацию о видеокарте.")
    print("5. Показать сетевую информацию.")
    print("0. Выход.")
    print("="*30)


def main():
    info_print()
    while True:
        inp = input("Введите число: ").strip()
        if inp == "1":
            cpu_info()
        elif inp == "2":
            ram_info()
        elif inp == "3":
            disk_info()
        elif inp == "4":
            videocard_info()
        elif inp == "5":
            network_info()
        elif inp == "0":
            print("Выход из программы... :( ")
            break
        else:
            print("Неверный ввод")
            info_print()
            continue
        
        input("\nНажмите Enter для продолжения...")
        info_print()


if __name__ == "__main__":
    main()
