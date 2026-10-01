#!/usr/bin/env python3
"""
plot_results.py - Visualisasi Hasil Benchmark Global Word Count (Bagian B3)

Menghasilkan grafik perbandingan:
results/b3_method_comparison.png:
1. Perbandingan Total Time: ThreadPoolExecutor vs ProcessPoolExecutor
2. Waktu eksekusi berdasarkan jumlah worker
3. Waktu processing vs Waktu Total per metode
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Styling visual matplotlib
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

def plot_b3_comparison(df: pd.DataFrame, output_path: Path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5), dpi=300)

    # 1. Bar Chart: Rata-rata Total Time per Ranks & Workers
    threads_df = df[df['method'] == 'ThreadPoolExecutor']
    procs_df = df[df['method'] == 'ProcessPoolExecutor']

    # Buat label kombinasi ranks x workers
    combos = [f"{r}R x {w}W" for r, w in zip(threads_df['mpi_ranks'], threads_df['workers'])]
    x = range(len(combos))
    width = 0.38

    ax1.bar([i - width/2 for i in x], threads_df['total_time'], width=width, label='ThreadPoolExecutor', color='#3498db')
    ax1.bar([i + width/2 for i in x], procs_df['total_time'], width=width, label='ProcessPoolExecutor', color='#e67e22')

    ax1.set_title("Total Execution Time: ThreadPool vs ProcessPool", fontsize=11, fontweight='bold', pad=10)
    ax1.set_xlabel("Konfigurasi (MPI Ranks x Workers)", fontsize=10, labelpad=8)
    ax1.set_ylabel("Total Time (detik)", fontsize=10, labelpad=8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(combos, rotation=45, ha='right', fontsize=9)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(frameon=True, facecolor='white', loc='upper right')

    # 2. Line Chart: Rata-rata Total Time berdasarkan Workers per Rank
    w_threads = threads_df.groupby('workers')['total_time'].mean()
    w_procs = procs_df.groupby('workers')['total_time'].mean()

    workers_x = sorted(df['workers'].unique())
    ax2.plot(workers_x, [w_threads[w] for w in workers_x], marker='o', linewidth=2.5, markersize=8, color='#2980b9', label='ThreadPoolExecutor')
    ax2.plot(workers_x, [w_procs[w] for w in workers_x], marker='s', linewidth=2.5, markersize=8, color='#d35400', label='ProcessPoolExecutor')

    ax2.set_title("Rata-rata Waktu Eksekusi vs Jumlah Worker", fontsize=11, fontweight='bold', pad=10)
    ax2.set_xlabel("Jumlah Workers per Rank", fontsize=10, labelpad=8)
    ax2.set_ylabel("Rata-rata Total Time (detik)", fontsize=10, labelpad=8)
    ax2.set_xticks(workers_x)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(frameon=True, facecolor='white')

    plt.suptitle("Perbandingan Kinerja Eksekusi Global Word Count (B3)", fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[PLOT] Tersimpan: {output_path.resolve()}")

def main():
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir / "results"
    csv_file = results_dir / "b3_results.csv"

    if not csv_file.exists():
        print(f"[ERROR] File {csv_file} tidak ditemukan. Jalankan run_benchmark.py terlebih dahulu.")
        sys.exit(1)

    df = pd.read_csv(csv_file)
    print(f"[INFO] Membaca {len(df)} baris data hasil benchmark B3 dari {csv_file.name}")
    plot_b3_comparison(df, results_dir / "b3_method_comparison.png")
    print("[SUCCESS] Grafik perbandingan B3 berhasil dibuat!")

if __name__ == "__main__":
    main()
