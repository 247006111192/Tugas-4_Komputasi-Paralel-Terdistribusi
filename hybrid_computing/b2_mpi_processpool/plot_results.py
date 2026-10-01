#!/usr/bin/env python3
"""
plot_results.py - Visualisasi Hasil Benchmark Strong Scaling MPI + ProcessPool (Bagian B2)

Menghasilkan 3 grafik utama:
1. results/b2_makespan.png   : Makespan vs Jumlah Worker/Proses
2. results/b2_speedup.png    : Speedup vs Konfigurasi (disertai garis ideal speedup)
3. results/b2_efficiency.png : Efficiency vs Konfigurasi (disertai baseline ideal E=1.0)
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

def plot_makespan(df: pd.DataFrame, output_path: Path):
    """Grafik Makespan terhadap konfigurasi rank & worker."""
    plt.figure(figsize=(9, 5.5), dpi=300)
    
    ranks = sorted(df['mpi_ranks'].unique())
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    markers = ['o', 's', '^']

    for idx, r in enumerate(ranks):
        sub = df[df['mpi_ranks'] == r].sort_values('max_workers')
        plt.plot(
            sub['max_workers'],
            sub['makespan'],
            marker=markers[idx],
            color=colors[idx],
            linewidth=2,
            markersize=7,
            label=f"{r} MPI Rank(s)"
        )

    plt.title("Makespan vs Max Workers per Rank (Strong Scaling B2)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Max Workers per MPI Rank (ProcessPool)", fontsize=11, labelpad=8)
    plt.ylabel("Makespan (detik)", fontsize=11, labelpad=8)
    plt.xticks([1, 2, 4])
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(title="MPI Ranks", frameon=True, facecolor='white', framealpha=0.9, fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[PLOT] Tersimpan: {output_path.resolve()}")

def plot_speedup(df: pd.DataFrame, output_path: Path):
    """Grafik Speedup terukur dibandingkan Speedup Ideal Linier."""
    plt.figure(figsize=(9, 5.5), dpi=300)

    # Urutkan berdasarkan total processes/workers
    df_sorted = df.sort_values(['total_processes_or_workers', 'mpi_ranks'])
    labels = [f"{r}R x {w}W\n({t}p)" for r, w, t in zip(df_sorted['mpi_ranks'], df_sorted['max_workers'], df_sorted['total_processes_or_workers'])]
    x_positions = range(len(df_sorted))

    # Bar speedup terukur
    colors = ['#2b5c8f' if ind == 'WITHIN_PHYSICAL_CORES' else '#e26d5c' for ind in df_sorted['oversubscription_indicator']]
    bars = plt.bar(x_positions, df_sorted['speedup'], color=colors, width=0.55, label='Speedup Terukur')

    # Garis ideal speedup
    plt.plot(x_positions, df_sorted['total_processes_or_workers'], color='#2a9d8f', linestyle='--', marker='o', linewidth=2, label='Ideal Linear Speedup')

    # Anotasi nilai di atas bar
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'{height:.2f}x',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    plt.title("Speedup vs Konfigurasi Eksekusi (Strong Scaling B2)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Konfigurasi (Rank x Worker, Total Proses)", fontsize=11, labelpad=8)
    plt.ylabel("Speedup (S = T1 / Tn)", fontsize=11, labelpad=8)
    plt.xticks(x_positions, labels, fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[PLOT] Tersimpan: {output_path.resolve()}")

def plot_efficiency(df: pd.DataFrame, output_path: Path):
    """Grafik Efisiensi Paralel terhadap Konfigurasi."""
    plt.figure(figsize=(9, 5.5), dpi=300)

    df_sorted = df.sort_values(['total_processes_or_workers', 'mpi_ranks'])
    labels = [f"{r}R x {w}W\n({t}p)" for r, w, t in zip(df_sorted['mpi_ranks'], df_sorted['max_workers'], df_sorted['total_processes_or_workers'])]
    x_positions = range(len(df_sorted))

    colors = ['#2a9d8f' if ind == 'WITHIN_PHYSICAL_CORES' else '#e76f51' for ind in df_sorted['oversubscription_indicator']]
    bars = plt.bar(x_positions, df_sorted['efficiency'], color=colors, width=0.55, label='Efisiensi Terukur')

    # Garis ideal efisiensi E = 1.0 (100%)
    plt.axhline(1.0, color='#e63946', linestyle='--', linewidth=1.5, label='Ideal Efficiency (1.0)')

    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'{height:.2f}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points",
                     ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    plt.title("Parallel Efficiency vs Konfigurasi (Strong Scaling B2)", fontsize=13, fontweight='bold', pad=12)
    plt.xlabel("Konfigurasi (Rank x Worker, Total Proses)", fontsize=11, labelpad=8)
    plt.ylabel("Efficiency (E = S / n)", fontsize=11, labelpad=8)
    plt.ylim(0, 1.25)
    plt.xticks(x_positions, labels, fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[PLOT] Tersimpan: {output_path.resolve()}")

def main():
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir / "results"
    csv_file = results_dir / "b2_results.csv"

    if not csv_file.exists():
        print(f"[ERROR] File hasil {csv_file} tidak ditemukan. Jalankan run_benchmark.py terlebih dahulu.")
        sys.exit(1)

    df = pd.read_csv(csv_file)
    print(f"[INFO] Membaca {len(df)} baris data hasil benchmark dari {csv_file.name}")

    plot_makespan(df, results_dir / "b2_makespan.png")
    plot_speedup(df, results_dir / "b2_speedup.png")
    plot_efficiency(df, results_dir / "b2_efficiency.png")
    print("[SUCCESS] Seluruh grafik B2 berhasil dibuat!")

if __name__ == "__main__":
    main()
