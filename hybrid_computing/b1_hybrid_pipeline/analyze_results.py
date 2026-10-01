#!/usr/bin/env python3
"""
analyze_results.py - Analisis Otomatis Hasil Benchmark Hybrid Pipeline (Bagian B1)

Fitur Analisis:
1. Konfigurasi dengan throughput tertinggi pada hasil eksperimen
2. Konfigurasi dengan total time terendah pada pengujian
3. Rata-rata throughput berdasarkan N_WORKERS
4. Perbandingan performa Q_MAX 4 vs 32
5. Perbandingan performa Loader Threads
6. Analisis teoritis dan empiris indikasi fenomena backpressure
"""

import sys
import pandas as pd
from pathlib import Path

def analyze(csv_path: Path):
    if not csv_path.exists():
        print(f"[ERROR] File {csv_path} tidak ditemukan. Silakan jalankan run_benchmark.py terlebih dahulu.")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    print("=" * 75)
    print("        ANALISIS HASIL EKSPERIMEN B1: HYBRID PIPELINE")
    print("=" * 75)
    print(f"Total konfigurasi yang diuji: {len(df)} konfigurasi")
    print(f"Total file per konfigurasi : {df['total_files'].iloc[0]} file (.txt)\n")

    # 1. Konfigurasi throughput tertinggi
    best_tp_row = df.loc[df['throughput'].idxmax()]
    print("-" * 75)
    print("1. KONFIGURASI DENGAN THROUGHPUT TERTINGGI PADA HASIL EKSPERIMEN:")
    print(f"   - Experiment ID     : Exp #{int(best_tp_row['experiment_id'])}")
    print(f"   - Loader Threads    : {int(best_tp_row['n_loader_threads'])} thread")
    print(f"   - N_WORKERS         : {int(best_tp_row['n_workers'])} worker")
    print(f"   - Q_MAX (Queue Cap) : {int(best_tp_row['q_max'])}")
    print(f"   - Throughput        : {best_tp_row['throughput']:.2f} file/detik")
    print(f"   - Total Time        : {best_tp_row['total_time']:.4f} detik")
    print(f"   - Avg Latency       : {best_tp_row['avg_latency']:.6f} detik")

    # 2. Konfigurasi waktu terendah
    best_time_row = df.loc[df['total_time'].idxmin()]
    print("-" * 75)
    print("2. KONFIGURASI DENGAN WAKTU EKSEKUSI TERENDAH PADA PENGUJIAN:")
    print(f"   - Experiment ID     : Exp #{int(best_time_row['experiment_id'])}")
    print(f"   - Loader Threads    : {int(best_time_row['n_loader_threads'])} thread")
    print(f"   - N_WORKERS         : {int(best_time_row['n_workers'])} worker")
    print(f"   - Q_MAX (Queue Cap) : {int(best_time_row['q_max'])}")
    print(f"   - Total Time        : {best_time_row['total_time']:.4f} detik")
    print(f"   - Throughput        : {best_tp_row['throughput']:.2f} file/detik")

    # 3. Rata-rata Throughput berdasarkan N_WORKERS
    print("-" * 75)
    print("3. RATA-RATA THROUGHPUT BERDASARKAN JUMLAH WORKER (N_WORKERS):")
    tp_by_workers = df.groupby('n_workers')['throughput'].agg(['mean', 'min', 'max', 'std'])
    for w, row in tp_by_workers.iterrows():
        print(f"   - Workers = {w:2d} : Rata-rata = {row['mean']:8.2f} f/s | Min = {row['min']:8.2f} | Max = {row['max']:8.2f}")

    # 4. Perbandingan Q_MAX 4 vs 32
    print("-" * 75)
    print("4. PERBANDINGAN PENGARUH UKURAN ANTREAN (Q_MAX):")
    q_stats = df.groupby('q_max')[['throughput', 'avg_latency', 'total_time']].mean()
    for q, row in q_stats.iterrows():
        print(f"   - Q_MAX = {q:2d} : Throughput = {row['throughput']:8.2f} f/s | Avg Latency = {row['avg_latency']:.6f} s | Total Time = {row['total_time']:.4f} s")

    # 5. Perbandingan Loader Threads
    print("-" * 75)
    print("5. PERBANDINGAN PENGARUH JUMLAH LOADER THREADS:")
    loader_stats = df.groupby('n_loader_threads')[['throughput', 'total_time']].mean()
    for ldr, row in loader_stats.iterrows():
        print(f"   - Loaders = {ldr} : Throughput = {row['throughput']:8.2f} f/s | Total Time = {row['total_time']:.4f} s")

    # 6. Analisis Backpressure
    print("-" * 75)
    print("6. ANALISIS MEKANISME BACKPRESSURE:")
    print("   [Konsep]:")
    print("   - Queue bertindak sebagai bounded buffer berkapasitas Q_MAX antara tahap I/O dan tahap Worker.")
    print("   - Pada Q_MAX = 4, kapasitas buffer sangat terbatas. Jika loader membaca file lebih cepat")
    print("     daripada laju worker memprosesnya, antrean akan cepat terisi penuh dan thread loader akan terblokir")
    print("     pada queue.put(). Kondisi ini menghasilkan efek backpressure yang menahan laju produsen.")
    print("   - Pada Q_MAX = 32, buffer memiliki kelonggaran penampungan yang lebih besar sehingga loader dapat")
    print("     terus memuat item ke memori tanpa sering terblokir, namun item yang mengantre mengalami waktu")
    print("     tunggu (queue residence time) yang dapat memengaruhi rata-rata latency.")
    print("=" * 75)

def main():
    base_dir = Path(__file__).resolve().parent
    csv_file = base_dir / "results" / "b1_results.csv"
    analyze(csv_file)

if __name__ == "__main__":
    main()
