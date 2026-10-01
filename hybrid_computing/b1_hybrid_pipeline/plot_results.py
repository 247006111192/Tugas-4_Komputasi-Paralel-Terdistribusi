#!/usr/bin/env python3
"""
plot_results.py - Visualisasi Hasil Benchmark Hybrid Pipeline (Bagian B1)

Menghasilkan 3 grafik utama sesuai ketentuan:
1. results/throughput_vs_workers.png : Grafik Throughput vs N_WORKERS
2. results/time_vs_workers.png       : Grafik Total Time vs N_WORKERS
3. results/qmax_comparison.png      : Grafik Perbandingan Q_MAX = 4 vs Q_MAX = 32
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

def plot_throughput_vs_workers(df: pd.DataFrame, output_path: Path):
    """Grafik Throughput terhadap N_WORKERS untuk berbagai kombinasi Loaders & Q_MAX."""
    plt.figure(figsize=(9, 5.5), dpi=300)
    
    # Kelompokkan berdasarkan loader threads dan q_max
    loaders_list = sorted(df['n_loader_threads'].unique())
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    markers = {'4': 'o', '32': 's'}
    linestyles = {'4': '--', '32': '-'}

    for idx, loader in enumerate(loaders_list):
        for q_max in sorted(df['q_max'].unique()):
            sub = df[(df['n_loader_threads'] == loader) & (df['q_max'] == q_max)].sort_values('n_workers')
            label = f"Loaders={loader}, Q_MAX={q_max}"
            plt.plot(
                sub['n_workers'],
                sub['throughput'],
                marker=markers[str(q_max)],
                linestyle=linestyles[str(q_max)],
                color=colors[idx],
                linewidth=2,
                markersize=6,
                label=label
            )

    plt.title("Throughput vs N_WORKERS (Hybrid Pipeline B1)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Jumlah Workers (N_WORKERS)", fontsize=11, labelpad=8)
    plt.ylabel("Throughput (file / detik)", fontsize=11, labelpad=8)
    plt.xticks([1, 2, 4, 14])
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(title="Konfigurasi", frameon=True, facecolor='white', framealpha=0.9, fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[PLOT] Tersimpan: {output_path.resolve()}")

def plot_time_vs_workers(df: pd.DataFrame, output_path: Path):
    """Grafik Total Waktu Eksekusi terhadap N_WORKERS."""
    plt.figure(figsize=(9, 5.5), dpi=300)
    
    loaders_list = sorted(df['n_loader_threads'].unique())
    colors = ['#d62728', '#9467bd', '#8c564b']

    for idx, loader in enumerate(loaders_list):
        for q_max in sorted(df['q_max'].unique()):
            sub = df[(df['n_loader_threads'] == loader) & (df['q_max'] == q_max)].sort_values('n_workers')
            linestyle = '-' if q_max == 32 else '--'
            marker = 'D' if q_max == 32 else '^'
            plt.plot(
                sub['n_workers'],
                sub['total_time'],
                marker=marker,
                linestyle=linestyle,
                color=colors[idx],
                linewidth=2,
                markersize=6,
                label=f"Loaders={loader}, Q={q_max}"
            )

    plt.title("Total Waktu Eksekusi vs N_WORKERS (Hybrid Pipeline B1)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Jumlah Workers (N_WORKERS)", fontsize=11, labelpad=8)
    plt.ylabel("Total Waktu (detik)", fontsize=11, labelpad=8)
    plt.xticks([1, 2, 4, 14])
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(title="Konfigurasi", frameon=True, facecolor='white', framealpha=0.9, fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[PLOT] Tersimpan: {output_path.resolve()}")

def plot_qmax_comparison(df: pd.DataFrame, output_path: Path):
    """Perbandingan rata-rata Throughput dan Latency antara Q_MAX = 4 dan Q_MAX = 32."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=300)

    # Rata-rata throughput per N_WORKERS untuk Q_MAX 4 vs 32
    q_grouped = df.groupby(['n_workers', 'q_max'])['throughput'].mean().unstack()
    lat_grouped = df.groupby(['n_workers', 'q_max'])['avg_latency'].mean().unstack()

    workers = q_grouped.index.tolist()
    x = range(len(workers))
    width = 0.35

    # Subplot 1: Throughput
    ax1.bar([i - width/2 for i in x], q_grouped[4], width=width, label='Q_MAX = 4 (Buffer Kecil)', color='#4c72b0')
    ax1.bar([i + width/2 for i in x], q_grouped[32], width=width, label='Q_MAX = 32 (Buffer Besar)', color='#55a868')
    ax1.set_title("Rata-rata Throughput: Q_MAX 4 vs 32", fontsize=11, fontweight='bold')
    ax1.set_xlabel("N_WORKERS", fontsize=10)
    ax1.set_ylabel("Throughput (file/detik)", fontsize=10)
    ax1.set_xticks(x)
    ax1.set_xticklabels(workers)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(frameon=True, facecolor='white')

    # Subplot 2: Latency
    ax2.bar([i - width/2 for i in x], lat_grouped[4], width=width, label='Q_MAX = 4', color='#c44e52')
    ax2.bar([i + width/2 for i in x], lat_grouped[32], width=width, label='Q_MAX = 32', color='#8172b3')
    ax2.set_title("Rata-rata Latency: Q_MAX 4 vs 32", fontsize=11, fontweight='bold')
    ax2.set_xlabel("N_WORKERS", fontsize=10)
    ax2.set_ylabel("Average Latency (detik)", fontsize=10)
    ax2.set_xticks(x)
    ax2.set_xticklabels(workers)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(frameon=True, facecolor='white')

    plt.suptitle("Analisis Pengaruh Ukuran Antrean (Q_MAX) terhadap Throughput dan Latency", fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[PLOT] Tersimpan: {output_path.resolve()}")

def main():
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir / "results"
    csv_file = results_dir / "b1_results.csv"

    if not csv_file.exists():
        print(f"[ERROR] File hasil {csv_file} tidak ditemukan. Jalankan run_benchmark.py terlebih dahulu.")
        sys.exit(1)

    df = pd.read_csv(csv_file)
    print(f"[INFO] Membaca {len(df)} baris data hasil eksperimen dari {csv_file.name}")

    plot_throughput_vs_workers(df, results_dir / "throughput_vs_workers.png")
    plot_time_vs_workers(df, results_dir / "time_vs_workers.png")
    plot_qmax_comparison(df, results_dir / "qmax_comparison.png")
    print("[SUCCESS] Seluruh grafik B1 berhasil dibuat!")

if __name__ == "__main__":
    main()
