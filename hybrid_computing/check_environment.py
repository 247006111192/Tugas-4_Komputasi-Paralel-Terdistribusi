#!/usr/bin/env python3
"""
Script Pengecekan Environment Hybrid Computing
Mendeteksi spesifikasi sistem secara otomatis tanpa hardcoding.
"""

import sys
import os
import platform
import shutil

def get_cpu_info():
    """Mendeteksi informasi CPU menggunakan psutil atau wmi/platform."""
    cpu_name = platform.processor()
    try:
        import subprocess
        # Mengambil nama prosesor lengkap pada Windows via PowerShell CIM
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor).Name"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if res.returncode == 0 and res.stdout.strip():
            cpu_name = res.stdout.strip()
    except Exception:
        pass
    return cpu_name

def check_env():
    print("=" * 45)
    print("        HYBRID COMPUTING ENVIRONMENT")
    print("=" * 45)

    # 1. Python Version
    py_ver = sys.version.split()[0]
    print(f"Python          : {py_ver} ({sys.executable})")

    # 2. Operating System
    os_info = f"{platform.system()} {platform.release()} ({platform.architecture()[0]}, {platform.machine()})"
    print(f"Operating System: {os_info}")

    # 3. CPU
    cpu_model = get_cpu_info()
    print(f"CPU             : {cpu_model}")

    # 4. Cores & Threads
    physical_cores = None
    logical_cpus = os.cpu_count()
    ram_gb = "N/A"

    try:
        import psutil
        physical_cores = psutil.cpu_count(logical=False)
        logical_cpus = psutil.cpu_count(logical=True)
        mem = psutil.virtual_memory()
        ram_gb = f"{mem.total / (1024**3):.2f} GB (Available: {mem.available / (1024**3):.2f} GB)"
    except ImportError:
        pass

    print(f"Physical cores  : {physical_cores if physical_cores is not None else 'N/A'}")
    print(f"Logical CPUs    : {logical_cpus if logical_cpus is not None else 'N/A'}")
    print(f"RAM             : {ram_gb}")

    # Catatan spesifikasi penugasan
    print("-" * 45)
    print("Catatan Parameter Tugas:")
    print("Target Physical Cores untuk N_WORKERS (B1) = 14 Core")
    print("Target Logical Threads laptop               = 20 Thread")
    print("-" * 45)

    # 5. mpi4py Status
    try:
        import mpi4py
        from mpi4py import MPI
        print(f"mpi4py          : Terpasang (Versi {mpi4py.__version__})")
        print(f"MPI Vendor      : {MPI.get_vendor()}")
    except ImportError as e:
        print(f"mpi4py          : Belum terpasang ({e})")

    # 6. mpiexec executable
    mpiexec_path = shutil.which("mpiexec")
    if not mpiexec_path:
        # Cek path standar Microsoft MPI jika belum ada di session PATH
        msmpi_default = r"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe"
        if os.path.exists(msmpi_default):
            mpiexec_path = msmpi_default

    if mpiexec_path:
        print(f"mpiexec Path    : {mpiexec_path}")
    else:
        print("mpiexec Path    : Tidak ditemukan di PATH atau Program Files")

    print("=" * 45)

if __name__ == "__main__":
    check_env()
