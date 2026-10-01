#!/usr/bin/env python3
"""
mpi_processpool.py - Strong Scaling MPI + ProcessPool (Bagian B2)

================================================================================
ANALISIS ERROR KODE SLIDE 20 (PRAKTIKUM 2):
================================================================================
1. Masalah Utama (Windows Spawning & Missing Guard):
   Pada sistem operasi Windows, multiprocessing menggunakan metode 'spawn' (bukan 'fork').
   Jika kode tidak dilindungi dengan 'if __name__ == "__main__":', setiap child process
   yang dibuat oleh ProcessPoolExecutor akan mengimpor ulang file dari awal. Hal ini
   memicu rekursi tak terbatas (infinite process spawning) dan menghasilkan:
   RuntimeError: An attempt has been made to start a new process before the current
   process has finished its bootstrapping phase.

2. Masalah Pickling MPI Communicator:
   Jika objek MPI (seperti MPI.COMM_WORLD) dikirimkan sebagai argumen ke fungsi worker
   dalam ProcessPoolExecutor, Python akan melempar:
   TypeError / PicklingError: cannot pickle 'mpi4py.MPI.Comm' object.
   Objek MPI adalah pointer C native yang tidak dapat diserialisasi oleh pickle.

3. Tabrakan Konteks MPI pada Sub-proses:
   Jika sub-proses mencoba mengakses atau memanggil fungsi MPI tanpa inisialisasi terisolasi,
   driver MS-MPI akan mengalami race-condition atau hang.

================================================================================
PERBAIKAN YANG DITERAPKAN:
================================================================================
1. Memastikan seluruh blok eksekusi berada di bawah 'if __name__ == "__main__":'.
2. Memisahkan fungsi worker murni (CPU-bound) agar tidak menyentuh objek MPI sama sekali.
3. Seluruh komunikasi MPI (Barrier, Gather, Reduce) hanya dijalankan oleh proses utama rank.
4. Parameter SAMPLES_PER_TASK diatur ke 200.000 + 10.000 * A = 220.000 (untuk A = 2).
================================================================================
"""

import sys
import time
import math
import random
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

# Import mpi4py
try:
    from mpi4py import MPI
except ImportError:
    MPI = None

# Parameter tugas
A = 2
SAMPLES_PER_TASK = 200_000 + (10_000 * A)  # 220.000
TOTAL_TASKS = 16  # Fixed total workload untuk Strong Scaling

def pure_compute_task(task_id: int, num_samples: int) -> int:
    """
    Fungsi komputasi murni CPU-bound: Estimasi Monte Carlo Pi.
    Fungsi ini bebas dari pemanggilan MPI dan aman di-pickle oleh ProcessPoolExecutor.
    Menghitung berapa banyak titik acak (x, y) yang berada di dalam lingkaran kuadran satuan.
    """
    # Deterministic pseudo-random seed per task
    rng = random.Random(1000 + task_id * 17)
    inside_circle = 0

    for _ in range(num_samples):
        x = rng.random()
        y = rng.random()
        if (x * x + y * y) <= 1.0:
            inside_circle += 1

    return inside_circle

def get_oversubscription_indicator(total_workers: int, physical_cores: int = 14, logical_threads: int = 20) -> str:
    """
    Menghitung indikator oversubscription konfigurasi:
    - WITHIN_PHYSICAL_CORES   : total_workers <= physical_cores (14)
    - EXCEEDS_PHYSICAL_CORES  : physical_cores < total_workers <= logical_threads (15-20)
    - EXCEEDS_LOGICAL_THREADS : total_workers > logical_threads (>20)
    """
    if total_workers <= physical_cores:
        return "WITHIN_PHYSICAL_CORES"
    elif total_workers <= logical_threads:
        return "EXCEEDS_PHYSICAL_CORES"
    else:
        return "EXCEEDS_LOGICAL_THREADS"

def run_experiment(max_workers: int, samples_per_task: int = SAMPLES_PER_TASK):
    if MPI is None:
        print("[ERROR] mpi4py belum terpasang. Jalankan dengan MPI terinstal.", file=sys.stderr)
        sys.exit(1)

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Bagi daftar tasks di antara MPI rank (Round-robin partitioning)
    rank_tasks = [t_id for t_id in range(TOTAL_TASKS) if t_id % size == rank]

    # Sinkronisasi awal sebelum pengukuran
    comm.Barrier()
    rank_start_time = time.perf_counter()

    local_inside_sum = 0
    # Eksekusi task lokal menggunakan ProcessPoolExecutor
    if rank_tasks:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Map setiap task ke ProcessPool
            futures = [
                executor.submit(pure_compute_task, t_id, samples_per_task)
                for t_id in rank_tasks
            ]
            for f in futures:
                local_inside_sum += f.result()

    rank_end_time = time.perf_counter()
    rank_duration = rank_end_time - rank_start_time

    # Kumpulkan hasil dan hitung Makespan (waktu terlama di antara semua rank)
    all_durations = comm.gather(rank_duration, root=0)
    total_inside = comm.reduce(local_inside_sum, op=MPI.SUM, root=0)

    if rank == 0:
        makespan = max(all_durations)
        total_samples_all = TOTAL_TASKS * samples_per_task
        pi_estimate = 4.0 * total_inside / total_samples_all
        total_workers = size * max_workers
        indicator = get_oversubscription_indicator(total_workers, physical_cores=14, logical_threads=20)

        return {
            "mpi_ranks": size,
            "max_workers": max_workers,
            "total_tasks": TOTAL_TASKS,
            "samples_per_task": samples_per_task,
            "makespan": makespan,
            "pi_estimate": pi_estimate,
            "total_workers": total_workers,
            "indicator": indicator,
            "all_durations": all_durations
        }
    return None

def main():
    parser = argparse.ArgumentParser(description="Strong Scaling MPI + ProcessPool (Bagian B2)")
    parser.add_argument("--workers", type=int, default=1, help="Jumlah worker per rank pada ProcessPoolExecutor")
    parser.add_argument("--samples", type=int, default=SAMPLES_PER_TASK, help="Jumlah samples per task")
    args = parser.parse_args()

    comm = MPI.COMM_WORLD if MPI else None
    rank = comm.Get_rank() if comm else 0

    res = run_experiment(max_workers=args.workers, samples_per_task=args.samples)

    if rank == 0 and res:
        print("\n" + "=" * 55)
        print("     STRONG SCALING MPI + PROCESSPOOL (B2)")
        print("=" * 55)
        print(f"MPI ranks                   : {res['mpi_ranks']}")
        print(f"Workers per rank            : {res['max_workers']}")
        print(f"Estimated worker processes  : {res['total_workers']}")
        print(f"Physical cores              : 14")
        print(f"Logical threads             : 20")
        print(f"Oversubscription indicator  : {res['indicator']}")
        print(f"SAMPLES_PER_TASK            : {res['samples_per_task']:,}")
        print(f"Makespan (Execution Time)   : {res['makespan']:.4f} detik")
        print(f"Pi Estimate                 : {res['pi_estimate']:.6f} (Error: {abs(res['pi_estimate'] - math.pi):.6f})")
        print("=" * 55)

if __name__ == "__main__":
    main()
