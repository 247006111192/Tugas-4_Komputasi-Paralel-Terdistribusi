#!/usr/bin/env python3
"""
run_benchmark.py - Benchmark Global Word Count: ThreadPoolExecutor vs ProcessPoolExecutor (B3)

Menguji:
- Metode     : ThreadPoolExecutor vs ProcessPoolExecutor
- MPI Ranks  : [1, 2, 4]
- Workers    : [1, 2, 4]

Metrik yang diukur:
- reading_time     : waktu pembacaan file
- processing_time  : waktu pembersihan regex dan penghitungan kata
- total_time       : total waktu eksekusi (makespan termasuk aggregasi MPI)

Hasil disimpan ke:
results/b3_results.csv
"""

import sys
import os
import re
import csv
import shutil
import subprocess
from pathlib import Path

def find_mpiexec():
    exe = shutil.which("mpiexec")
    if exe:
        return exe
    msmpi_paths = [
        r"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe",
        r"C:\Program Files (x86)\Microsoft MPI\Bin\mpiexec.exe",
        os.path.expandvars(r"%MSMPI_BIN%\mpiexec.exe")
    ]
    for p in msmpi_paths:
        if os.path.exists(p):
            return p
    return None

def run_single_b3(mpiexec_bin: str, script_path: Path, method: str, ranks: int, workers: int):
    cmd = [
        mpiexec_bin,
        "-n", str(ranks),
        sys.executable,
        str(script_path),
        "--method", "threads" if "Thread" in method else "processes",
        "--workers", str(workers)
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if res.returncode != 0:
        raise RuntimeError(f"Eksekusi gagal:\n{res.stderr}")

    stdout = res.stdout
    time_match = re.search(r"Execution time:\s*([0-9.]+)\s*seconds", stdout)
    breakdown_match = re.search(r"Reading time:\s*([0-9.]+)s,\s*Processing time:\s*([0-9.]+)s", stdout)

    total_time = float(time_match.group(1)) if time_match else 0.0
    read_time = float(breakdown_match.group(1)) if breakdown_match else 0.0
    proc_time = float(breakdown_match.group(2)) if breakdown_match else 0.0

    return read_time, proc_time, total_time

def main():
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_file = results_dir / "b3_results.csv"
    script_path = base_dir / "wordcount.py"

    mpiexec_bin = find_mpiexec()
    if not mpiexec_bin:
        print("[ERROR] mpiexec tidak ditemukan.")
        sys.exit(1)

    methods = ["ThreadPoolExecutor", "ProcessPoolExecutor"]
    ranks_list = [1, 2, 4]
    workers_list = [1, 2, 4]

    print("=" * 75)
    print("  MEMULAI BENCHMARK B3: GLOBAL WORD COUNT (ThreadPool vs ProcessPool)")
    print("=" * 75)
    print(f"Target CSV: {csv_file.resolve()}\n")

    results_data = []
    total_runs = len(methods) * len(ranks_list) * len(workers_list)
    run_idx = 1

    for method in methods:
        for ranks in ranks_list:
            for workers in workers_list:
                print(f"[{run_idx:02d}/{total_runs}] {method:<19} | Ranks={ranks}, Workers={workers} ... ", end="", flush=True)
                read_t, proc_t, tot_t = run_single_b3(mpiexec_bin, script_path, method, ranks, workers)
                
                record = {
                    "method": method,
                    "mpi_ranks": ranks,
                    "workers": workers,
                    "processing_time": round(proc_t, 6),
                    "total_time": round(tot_t, 6)
                }
                results_data.append(record)
                print(f"Read: {read_t:.4f}s | Proc: {proc_t:.4f}s | Total: {tot_t:.4f}s")
                run_idx += 1

    fieldnames = ["method", "mpi_ranks", "workers", "processing_time", "total_time"]
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results_data)

    print("\n" + "=" * 75)
    print(f"[SUCCESS] Seluruh benchmark B3 selesai dan disimpan ke:")
    print(f"          {csv_file.resolve()}")
    print("=" * 75)

if __name__ == "__main__":
    main()
