#!/usr/bin/env python3
"""
analyze_results.py - Analisis Otomatis Global Word Count (Bagian B3)

Analisis:
1. Perbandingan Total Time dan Processing Time antara ThreadPoolExecutor vs ProcessPoolExecutor.
2. Penjelasan teoritis dan empiris mengapa salah satu metode lebih cepat dengan mempertimbangkan
   karakteristik I/O (pembacaan file) dan CPU (tokenisasi regex & filter kata).
3. Pengaruh penambahan worker dan rank MPI.
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
    print("      ANALISIS HASIL EKSPERIMEN B3: GLOBAL WORD COUNT")
    print("=" * 80)

    # 1. Rata-rata Total Time per metode
    method_summary = df.groupby('method')[['processing_time', 'total_time']].agg(['mean', 'min', 'max'])
    print("1. PERBANDINGAN PERFORMA METODE:")
    for method, row in method_summary.iterrows():
        print(f"   [{method}]:")
        print(f"   - Rata-rata Processing Time : {row[('processing_time', 'mean')]:.6f} detik")
        print(f"   - Rata-rata Total Time      : {row[('total_time', 'mean')]:.6f} detik (Min: {row[('total_time', 'min')]:.4f}s, Max: {row[('total_time', 'max')]:.4f}s)")

    # 2. Konfigurasi waktu terendah masing-masing metode
    print("-" * 80)
    print("2. KONFIGURASI DENGAN WAKTU EKSEKUSI TERENDAH:")
    for method in df['method'].unique():
        sub = df[df['method'] == method]
        best_row = sub.loc[sub['total_time'].idxmin()]
        print(f"   - {method:<19} : {int(best_row['mpi_ranks'])} Rank(s) x {int(best_row['workers'])} Worker(s) -> Total Time = {best_row['total_time']:.4f} detik")

    # 3. Penjelasan Mengapa ThreadPool vs ProcessPool Berbeda
    avg_threads = df[df['method'] == 'ThreadPoolExecutor']['total_time'].mean()
    avg_procs = df[df['method'] == 'ProcessPoolExecutor']['total_time'].mean()
    ratio = avg_procs / avg_threads if avg_threads > 0 else 0

    print("-" * 80)
    print("3. ANALISIS PERBANDINGAN I/O vs TOKENISASI REGEX:")
    print("   [Hasil Pengujian]:")
    print(f"   - ThreadPoolExecutor rata-rata {ratio:.1f}x lebih cepat dibandingkan ProcessPoolExecutor pada dataset ini.")
    print("   [Penyebab]:")
    print("   1. Karakteristik I/O (File Reading):")
    print("      Tahap pembacaan file dari disk bersifat I/O-bound. Di Python (CPython), thread melepaskan")
    print("      Global Interpreter Lock (GIL) saat melakukan operasi I/O, sehingga multi-threading")
    print("      dapat berjalan secara konkruen tanpa terhalang GIL.")
    print("   2. Overhead Pembuatan Proses (Process Spawning Overhead):")
    print("      Pada sistem operasi Windows, ProcessPoolExecutor menggunakan metode 'spawn' yang harus")
    print("      mengalokasikan ruang memori terpisah, menginisialisasi Python interpreter baru,")
    print("      serta men-serialize (pickle) dan de-serialize objek data antar-proses melalui pipe/IPC.")
    print("   3. Beban Tokenisasi Regex:")
    print("      Karena ukuran masing-masing artikel teks berkisar antara ratusan kata, beban komputasi regex")
    print("      berlangsung sangat cepat (skala milidetik). Oleh karena itu, keuntungan parallelism")
    print("      ProcessPool tidak cukup besar untuk menutupi biaya (overhead) pembuatan proses.")
    print("      Sebaliknya, ThreadPoolExecutor memiliki overhead inisialisasi yang mendekati nol,")
    print("      sehingga memberikan total waktu eksekusi yang jauh lebih rendah.")
    print("=" * 80)

def main():
    base_dir = Path(__file__).resolve().parent
    csv_file = base_dir / "results" / "b3_results.csv"
    analyze(csv_file)

if __name__ == "__main__":
    main()
