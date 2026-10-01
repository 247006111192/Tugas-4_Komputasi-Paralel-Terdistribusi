#!/usr/bin/env python3
"""
wordcount.py - Global Word Count Menggunakan MPI + Worker Pool (Bagian B3)

Arsitektur:
    MPI (Inter-node / Inter-process):
    ├── Rank 0 (Koordinator & Reducer Global)
    ├── Rank 1
    ├── Rank 2
    └── Rank 3
         └── Di dalam setiap rank terdapat Worker Pool:
             (a) ThreadPoolExecutor, ATAU
             (b) ProcessPoolExecutor

Tahapan Pemrosesan:
1. Membaca file teks dari folder dataset (I/O)
2. Mengubah teks menjadi huruf kecil (lowercase)
3. Tokenisasi menggunakan regular expression
4. Membersihkan karakter tanda baca/angka non-alfabet
5. Membuang stopwords minimal: 'dan', 'yang', 'di', 'the', 'of', 'and'
6. Menghitung frekuensi kata lokal per rank
7. Menggabungkan frekuensi global melalui MPI (COMM.reduce / COMM.gather)
8. Menampilkan 10 kata paling sering muncul di Rank 0.
"""

import re
import sys
import time
import argparse
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Import mpi4py
try:
    from mpi4py import MPI
except ImportError:
    MPI = None

# Stopwords minimal sesuai ketentuan soal
STOPWORDS = {"dan", "yang", "di", "the", "of", "and"}

def process_file_content(file_path: Path):
    """
    Fungsi pemrosesan dokumen:
    Membaca file, tokenisasi regex, filter stopwords, dan hitung frekuensi kata lokal.
    Mengukur waktu I/O (pembacaan) dan waktu komputasi (tokenisasi).
    """
    # 1. Tahap I/O: Membaca file
    t_read_start = time.perf_counter()
    try:
        text = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[ERROR] Gagal membaca {file_path}: {e}", file=sys.stderr)
        text = ""
    t_read_end = time.perf_counter()
    read_duration = t_read_end - t_read_start

    # 2. Tahap CPU: Lowercase, Regex Tokenization, Stopwords Removal
    t_proc_start = time.perf_counter()
    # Mengambil kata alfabet minimal 2 karakter
    tokens = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
    
    # Filter stopwords
    filtered_tokens = [tok for tok in tokens if tok not in STOPWORDS]
    
    # Penghitungan frekuensi kata lokal
    local_counter = Counter(filtered_tokens)
    t_proc_end = time.perf_counter()
    proc_duration = t_proc_end - t_proc_start

    return local_counter, read_duration, proc_duration

def run_global_wordcount(method: str, workers: int, dataset_dir: Path):
    if MPI is None:
        print("[ERROR] mpi4py belum terpasang. Jalankan dengan MPI terinstal.", file=sys.stderr)
        sys.exit(1)

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Seluruh rank menemukan file secara deterministik
    all_files = sorted(list(dataset_dir.glob("*.txt")))
    total_files = len(all_files)

    if total_files == 0:
        if rank == 0:
            print(f"[ERROR] Tidak ada file .txt di {dataset_dir}", file=sys.stderr)
        sys.exit(1)

    # Round-robin partitioning file antar-rank MPI
    assigned_files = [f for idx, f in enumerate(all_files) if idx % size == rank]

    # Sinkronisasi awal sebelum timer dimulai
    comm.Barrier()
    rank_start_time = time.perf_counter()

    rank_counter = Counter()
    total_read_time = 0.0
    total_proc_time = 0.0

    # Pilih executor pool di dalam rank
    executor_cls = ThreadPoolExecutor if method == "threads" else ProcessPoolExecutor

    if assigned_files:
        with executor_cls(max_workers=workers) as executor:
            futures = [executor.submit(process_file_content, f) for f in assigned_files]
            for fut in futures:
                res_counter, r_time, p_time = fut.result()
                rank_counter.update(res_counter)
                total_read_time += r_time
                total_proc_time += p_time

    rank_end_time = time.perf_counter()
    rank_total_time = rank_end_time - rank_start_time

    # Kumpulkan hasil dari semua rank ke Rank 0 menggunakan MPI.reduce / MPI.gather
    all_counters = comm.gather(rank_counter, root=0)
    all_read_times = comm.gather(total_read_time, root=0)
    all_proc_times = comm.gather(total_proc_time, root=0)
    all_total_times = comm.gather(rank_total_time, root=0)

    if rank == 0:
        # Gabungkan semua Counter menjadi Global Word Count
        global_counter = Counter()
        for c in all_counters:
            global_counter.update(c)

        makespan_total = max(all_total_times)
        avg_read_time = sum(all_read_times) / size
        avg_proc_time = sum(all_proc_times) / size
        top_10 = global_counter.most_common(10)

        method_display = "ThreadPoolExecutor" if method == "threads" else "ProcessPoolExecutor"

        return {
            "method": method_display,
            "raw_method": method,
            "mpi_ranks": size,
            "workers": workers,
            "total_files": total_files,
            "reading_time": avg_read_time,
            "processing_time": avg_proc_time,
            "total_time": makespan_total,
            "top_10": top_10
        }
    return None

def main():
    parser = argparse.ArgumentParser(description="Global Word Count (Bagian B3)")
    parser.add_argument("--method", choices=["threads", "processes"], default="threads",
                        help="Metode worker di dalam rank: 'threads' (ThreadPoolExecutor) atau 'processes' (ProcessPoolExecutor)")
    parser.add_argument("--workers", type=int, default=2, help="Jumlah worker per MPI rank")
    parser.add_argument("--dataset", type=str, default="", help="Path direktori dataset teks")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    dataset_dir = Path(args.dataset) if args.dataset else (base_dir / "dataset")

    comm = MPI.COMM_WORLD if MPI else None
    rank = comm.Get_rank() if comm else 0

    res = run_global_wordcount(method=args.method, workers=args.workers, dataset_dir=dataset_dir)

    if rank == 0 and res:
        print("\n" + "=" * 40)
        print("GLOBAL WORD COUNT")
        print("=" * 40)
        print(f"Method:")
        print(f"{res['method']}")
        print(f"\nMPI ranks:")
        print(f"{res['mpi_ranks']}")
        print(f"\nWorkers:")
        print(f"{res['workers']}")
        print(f"\nTotal files:")
        print(f"{res['total_files']}+")
        print(f"\nExecution time:")
        print(f"{res['total_time']:.4f} seconds")
        print(f"(Reading time: {res['reading_time']:.4f}s, Processing time: {res['processing_time']:.4f}s)")
        print(f"\nTop 10 words:")
        for idx, (word, count) in enumerate(res["top_10"], start=1):
            print(f"{idx:2d}. {word}: {count}")
        print("=" * 40 + "\n")

if __name__ == "__main__":
    main()
