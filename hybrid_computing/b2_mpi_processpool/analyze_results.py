#!/usr/bin/env python3
"""
analyze_results.py - Analisis Otomatis Hasil Strong Scaling MPI + ProcessPool (Bagian B2)

Menganalisis:
1. Baseline T1 dan percepatan (Speedup)
2. Efisiensi paralel (Parallel Efficiency)
3. Evaluasi fenomena Oversubscription (14 Physical Cores vs 20 Logical Threads)
4. Pengaruh pertambahan proses terhadap overhead komunikasi dan context switching.
"""

import sys
import pandas as pd
from pathlib import Path

def analyze(csv_path: Path):
    if not csv_path.exists():
        print(f"[ERROR] File {csv_path} tidak ditemukan. Jalankan run_benchmark.py terlebih dahulu.")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    print("=" * 80)
    print("      ANALISIS HASIL EKSPERIMEN B2: STRONG SCALING MPI + PROCESSPOOL")
    print("=" * 80)
    print(f"Total konfigurasi yang diuji: {len(df)} konfigurasi")
    print(f"Spesifikasi CPU Target       : 14 Physical Cores, 20 Logical Threads\n")

    # 1. Baseline T1
    t1_row = df[(df['mpi_ranks'] == 1) & (df['max_workers'] == 1)].iloc[0]
    t1_time = t1_row['makespan']
    print("-" * 80)
    print(f"1. BASELINE WAKTU SERIAL / SEKUANSIAL (T1):")
    print(f"   - Konfigurasi Baseline: 1 MPI Rank x 1 Worker")
    print(f"   - T1 Makespan         : {t1_time:.4f} detik")

    # 2. Konfigurasi Makespan Tercepat
    fastest_row = df.loc[df['makespan'].idxmin()]
    print("-" * 80)
    print(f"2. KONFIGURASI DENGAN MAKESPAN TERENDAH (TERCEPAT PADA PENGUJIAN):")
    print(f"   - Konfigurasi         : {int(fastest_row['mpi_ranks'])} MPI Rank(s) x {int(fastest_row['max_workers'])} Worker(s)")
    print(f"   - Total Proses/Worker : {int(fastest_row['total_processes_or_workers'])}")
    print(f"   - Makespan            : {fastest_row['makespan']:.4f} detik")
    print(f"   - Speedup             : {fastest_row['speedup']:.2f}x")
    print(f"   - Efisiensi           : {fastest_row['efficiency']:.2f} ({fastest_row['efficiency']*100:.1f}%)")
    print(f"   - Status Core         : {fastest_row['oversubscription_indicator']}")

    # 3. Tabel Ringkasan Speedup & Efisiensi
    print("-" * 80)
    print("3. TABEL RINGKASAN SELURUH KONFIGURASI:")
    print(f"{'Rank':>5} | {'Worker':>6} | {'Total Procs':>11} | {'Makespan (s)':>12} | {'Speedup':>8} | {'Efficiency':>10} | {'Status Core':<24}")
    print("-" * 88)
    for _, r in df.iterrows():
        print(f"{int(r['mpi_ranks']):5d} | {int(r['max_workers']):6d} | {int(r['total_processes_or_workers']):11d} | {r['makespan']:12.4f} | {r['speedup']:7.2f}x | {r['efficiency']:10.2f} | {r['oversubscription_indicator']:<24}")

    # 4. Analisis Oversubscription
    print("-" * 80)
    print("4. ANALISIS OVERSUBSCRIPTION (KONDISI PROSES > CORE FISIK):")
    print("   [Karakteristik Hardware]:")
    print("   - Laptop memiliki 14 Physical Cores dan 20 Logical Threads (Hyper-Threading / SMT).")
    print("   - Pada pengujian, total worker bervariasi dari 1 hingga 16 proses (4 Rank x 4 Worker).")
    
    within_df = df[df['oversubscription_indicator'] == 'WITHIN_PHYSICAL_CORES']
    exceeds_df = df[df['oversubscription_indicator'] == 'EXCEEDS_PHYSICAL_CORES']

    print(f"\n   [Konfigurasi Within Physical Cores (<= 14 proses)]:")
    print(f"   - Rata-rata efisiensi paralel: {within_df['efficiency'].mean():.2f}")
    
    if not exceeds_df.empty:
        print(f"\n   [Konfigurasi Exceeds Physical Cores (> 14 proses, misal 4R x 4W = 16 proses)]:")
        for _, ex in exceeds_df.iterrows():
            print(f"   - {int(ex['mpi_ranks'])}R x {int(ex['max_workers'])}W ({int(ex['total_processes_or_workers'])} proses): Makespan = {ex['makespan']:.4f}s | Speedup = {ex['speedup']:.2f}x | Efisiensi = {ex['efficiency']:.2f}")
        print("   [Dampak Oversubscription]:")
        print("   - Ketika jumlah proses (16) melampaui jumlah core fisik (14), OS scheduler harus melakukan")
        print("     time-slicing dan thread context switching yang sering pada core yang sama.")
        print("   - Walaupun masih berada di bawah batas logical thread (20), dua proses yang berbagi logical thread")
        print("     pada core fisik yang sama harus memperebutkan Arithmetic Logic Unit (ALU), L1/L2 cache,")
        print("     sehingga laju kenaikan speedup melambat dan efisiensi mengalami penurunan.")
    print("=" * 80)

def main():
    base_dir = Path(__file__).resolve().parent
    csv_file = base_dir / "results" / "b2_results.csv"
    analyze(csv_file)

if __name__ == "__main__":
    main()
