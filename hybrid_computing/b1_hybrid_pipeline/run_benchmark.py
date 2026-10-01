#!/usr/bin/env python3
"""
run_benchmark.py - Otomasi Benchmark 24 Konfigurasi Hybrid Pipeline (Bagian B1)

Kombinasi Parameter:
- N_LOADER_THREADS : [1, 2, 4]
- N_WORKERS        : [1, 2, 4, 14]
- Q_MAX            : [4, 32]
Total kombinasi = 3 * 4 * 2 = 24 konfigurasi.

Hasil disimpan ke:
results/b1_results.csv
"""

import sys
import csv
from pathlib import Path

# Import fungsi runner dari hybrid_pipeline.py
from hybrid_pipeline import run_hybrid_pipeline

def main():
    base_dir = Path(__file__).resolve().parent
    dataset_dir = base_dir / "dataset"
    results_dir = base_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_file = results_dir / "b1_results.csv"

    if not dataset_dir.exists():
        print(f"[ERROR] Dataset belum ditemukan pada {dataset_dir}. Jalankan generate_dataset.py terlebih dahulu.")
        sys.exit(1)

    loader_threads_list = [1, 2, 4]
    workers_list = [1, 2, 4, 14]
    q_max_list = [4, 32]

    total_runs = len(loader_threads_list) * len(workers_list) * len(q_max_list)
    print("=" * 70)
    print(f"  MEMULAI BENCHMARK B1: HYBRID PIPELINE ({total_runs} Konfigurasi)")
    print("=" * 70)
    print(f"Target Output CSV: {csv_file.resolve()}\n")

    results_data = []
    exp_id = 1

    # Header CSV sesuai spesifikasi soal
    fieldnames = [
        "experiment_id",
        "n_loader_threads",
        "n_workers",
        "q_max",
        "total_files",
        "total_time",
        "throughput",
        "avg_latency"
    ]

    for loaders in loader_threads_list:
        for workers in workers_list:
            for q_max in q_max_list:
                print(f"[{exp_id:02d}/{total_runs}] Running: Loaders={loaders}, Workers={workers:2d}, Q_MAX={q_max:2d} ... ", end="", flush=True)
                
                # Eksekusi pipeline
                res = run_hybrid_pipeline(
                    dataset_dir=dataset_dir,
                    n_loader_threads=loaders,
                    n_workers=workers,
                    q_max=q_max
                )

                record = {
                    "experiment_id": exp_id,
                    "n_loader_threads": loaders,
                    "n_workers": workers,
                    "q_max": q_max,
                    "total_files": res["total_files"],
                    "total_time": round(res["total_time"], 6),
                    "throughput": round(res["throughput"], 4),
                    "avg_latency": round(res["avg_latency"], 6)
                }
                results_data.append(record)
                print(f"Time: {record['total_time']:.4f}s | Throughput: {record['throughput']:8.2f} f/s | Latency: {record['avg_latency']:.4f}s")
                exp_id += 1

    # Tulis hasil ke CSV
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results_data)

    print("\n" + "=" * 70)
    print(f"[SUCCESS] Seluruh 24 eksperimen berhasil dijalankan dan disimpan ke:")
    print(f"          {csv_file.resolve()}")
    print("=" * 70)

if __name__ == "__main__":
    main()
