#!/usr/bin/env python3
"""
run_benchmark.py - Otomasi Benchmark Strong Scaling MPI + ProcessPool (Bagian B2)

Kombinasi Parameter:
- MPI ranks   : [1, 2, 4]
- max_workers : [1, 2, 4]
Total = 3 * 3 = 9 konfigurasi.

Metrik:
- T1        : Makespan pada konfigurasi baseline (1 rank x 1 worker)
- Makespan  : Tn (waktu eksekusi maksimum antarrank)
- Speedup   : S = T1 / Tn
- Efficiency: E = S / n (dengan n = total_processes_or_workers)

Hasil disimpan ke:
results/b2_results.csv
"""

import sys
import os
import re
import csv
import shutil
import subprocess
from pathlib import Path

def find_mpiexec():
    """Mencari executable mpiexec di PATH sistem atau lokasi instalasi standar."""
    exe = shutil.which("mpiexec")
    if exe:
        return exe
    
    # Standar Microsoft MPI di Windows
    msmpi_paths = [
        r"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe",
        r"C:\Program Files (x86)\Microsoft MPI\Bin\mpiexec.exe",
        os.path.expandvars(r"%MSMPI_BIN%\mpiexec.exe")
    ]
    for p in msmpi_paths:
        if os.path.exists(p):
            return p
    return None

def run_single_config(mpiexec_bin: str, script_path: Path, ranks: int, workers: int):
    """Menjalankan satu konfigurasi mpiexec dan mengekstrak makespan serta indikator."""
    cmd = [
        mpiexec_bin,
        "-n", str(ranks),
        sys.executable,
        str(script_path),
        "--workers", str(workers)
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if res.returncode != 0:
        raise RuntimeError(f"Eksekusi gagal (code {res.returncode}):\n{res.stderr}")

    stdout = res.stdout
    # Ekstrak makespan dari stdout
    makespan_match = re.search(r"Makespan\s*\(Execution Time\)\s*:\s*([0-9.]+)\s*detik", stdout)
    indicator_match = re.search(r"Oversubscription indicator\s*:\s*([A-Z_]+)", stdout)

    if not makespan_match:
        raise ValueError(f"Gagal mem-parsing output makespan dari:\n{stdout}")

    makespan = float(makespan_match.group(1))
    indicator = indicator_match.group(1) if indicator_match else "UNKNOWN"

    return makespan, indicator

def main():
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_file = results_dir / "b2_results.csv"
    script_path = base_dir / "mpi_processpool.py"

    mpiexec_bin = find_mpiexec()
    if not mpiexec_bin:
        print("[ERROR] mpiexec tidak ditemukan di sistem. Pastikan Microsoft MPI telah terpasang.")
        sys.exit(1)

    ranks_list = [1, 2, 4]
    workers_list = [1, 2, 4]

    print("=" * 75)
    print("  MEMULAI BENCHMARK B2: STRONG SCALING MPI + PROCESSPOOL (9 Konfigurasi)")
    print("=" * 75)
    print(f"mpiexec Path : {mpiexec_bin}")
    print(f"Target CSV   : {csv_file.resolve()}\n")

    # Jalankan konfigurasi baseline (1 rank x 1 worker) terlebih dahulu untuk mendapatkan T1
    print("[1/9] Mengukur baseline T1 (1 rank x 1 worker)...")
    t1_makespan, t1_indicator = run_single_config(mpiexec_bin, script_path, ranks=1, workers=1)
    print(f"      Baseline T1 = {t1_makespan:.4f} detik\n")

    results_data = []
    exp_num = 1
    total_configs = len(ranks_list) * len(workers_list)

    for r in ranks_list:
        for w in workers_list:
            total_procs = r * w
            print(f"[{exp_num}/{total_configs}] Menjalankan: {r} rank x {w} worker (Total: {total_procs} processes)... ", end="", flush=True)

            if r == 1 and w == 1:
                makespan = t1_makespan
                indicator = t1_indicator
            else:
                makespan, indicator = run_single_config(mpiexec_bin, script_path, ranks=r, workers=w)

            # Hitung speedup dan efisiensi
            speedup = t1_makespan / makespan if makespan > 0 else 0.0
            efficiency = speedup / total_procs if total_procs > 0 else 0.0

            record = {
                "mpi_ranks": r,
                "max_workers": w,
                "makespan": round(makespan, 6),
                "speedup": round(speedup, 4),
                "efficiency": round(efficiency, 4),
                "total_processes_or_workers": total_procs,
                "oversubscription_indicator": indicator
            }
            results_data.append(record)

            print(f"Makespan: {makespan:.4f}s | Speedup: {speedup:6.2f}x | Efficiency: {efficiency:6.2f} | [{indicator}]")
            exp_num += 1

    # Tulis hasil ke CSV
    fieldnames = [
        "mpi_ranks",
        "max_workers",
        "makespan",
        "speedup",
        "efficiency",
        "total_processes_or_workers",
        "oversubscription_indicator"
    ]

    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results_data)

    print("\n" + "=" * 75)
    print(f"[SUCCESS] Seluruh 9 eksperimen berhasil dijalankan dan disimpan ke:")
    print(f"          {csv_file.resolve()}")
    print("=" * 75)

if __name__ == "__main__":
    main()
