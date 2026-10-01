#!/usr/bin/env python3
"""
hybrid_pipeline.py - Implementasi Hybrid Pipeline (Bagian B1)

Arsitektur Pipeline:
    File Input
        ↓
    Loader Threads (I/O-bound: membaca file dari disk)
        ↓
    Queue (Bounded Buffer: kapasitas Q_MAX -> mekanisme Backpressure)
        ↓
    Worker Pool (CPU-bound: tokenisasi, pembersihan teks, word count)
        ↓
    Result Aggregation

Metrik Pengukuran:
1. Total Time   : Total durasi eksekusi pipeline (detik) menggunakan time.perf_counter()
2. Throughput   : Jumlah file yang diproses / total waktu (file/detik)
3. Avg Latency  : Rata-rata selang waktu dari file selesai dimuat/diantrekan hingga selesai diproses worker.

Catatan Implementasi:
Implementasi mandiri berdasarkan spesifikasi tugas praktikum Hybrid Computing.
"""

import os
import re
import sys
import time
import queue
import threading
from pathlib import Path
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED

def worker_task(filename: str, text: str, arrival_time: float):
    """
    Fungsi pemrosesan dokumen yang dijalankan oleh ProcessPool (CPU-bound).
    Melakukan tokenisasi regex, pembersihan teks, penghitungan frekuensi kata,
    dan menghitung latency per dokumen.
    """
    t_start = time.perf_counter()

    # CPU-bound: Tokenisasi teks dan pembersihan tanda baca
    words = re.findall(r"\b[a-zA-Z]{2,}\b", text.lower())
    
    # Hitung frekuensi kata
    word_counts = Counter(words)
    top_words = word_counts.most_common(5)

    # Tambahan komputasi checksum sederhana untuk memastikan beban CPU terukur
    checksum = sum(ord(c) for c in text)

    t_finish = time.perf_counter()

    # Latency: Waktu dari saat dokumen masuk antrean loader hingga selesai diproses worker
    latency = t_finish - arrival_time

    return {
        "filename": filename,
        "word_count": len(words),
        "top_words": top_words,
        "checksum": checksum,
        "latency": latency
    }

def loader_worker(file_queue: queue.Queue, data_queue: queue.Queue, backpressure_counter: list):
    """
    Worker thread untuk I/O (Loader Thread).
    Membaca file dari disk dan memasukkan konten teks ke dalam data_queue (bounded).
    Jika data_queue penuh (Q_MAX tercapai), pemanggilan put() akan memblokir (backpressure).
    """
    while True:
        try:
            file_path = file_queue.get_nowait()
        except queue.Empty:
            break

        try:
            # I/O operation
            text = file_path.read_text(encoding="utf-8")
            arrival_time = time.perf_counter()

            # Deteksi apakah antrean sedang penuh sebelum put (indikasi backpressure)
            if data_queue.full():
                backpressure_counter[0] += 1

            # Memasukkan data ke queue berkapasitas Q_MAX (akan memblokir jika penuh)
            data_queue.put((file_path.name, text, arrival_time))
        except Exception as e:
            print(f"[ERROR] Gagal memuat {file_path.name}: {e}", file=sys.stderr)
        finally:
            file_queue.task_done()

def run_hybrid_pipeline(dataset_dir: Path, n_loader_threads: int, n_workers: int, q_max: int):
    """
    Menjalankan pipeline hybrid dengan konfigurasi yang ditentukan.
    """
    files = sorted(list(dataset_dir.glob("*.txt")))
    total_files = len(files)
    if total_files == 0:
        raise FileNotFoundError(f"Tidak ada file .txt ditemukan di {dataset_dir}")

    # 1. Antrean tugas pembacaan file
    file_queue = queue.Queue()
    for f in files:
        file_queue.put(f)

    # 2. Antrean berbatas (Bounded Buffer) untuk menguji Backpressure
    data_queue = queue.Queue(maxsize=q_max)
    backpressure_events = [0]

    pipeline_start = time.perf_counter()

    # 3. Inisialisasi Loader Threads (I/O)
    loaders = []
    for _ in range(n_loader_threads):
        t = threading.Thread(
            target=loader_worker,
            args=(file_queue, data_queue, backpressure_events),
            daemon=True
        )
        t.start()
        loaders.append(t)

    # 4. Dispatcher ke ProcessPool (CPU Workers)
    results = []
    latencies = []

    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        active_futures = set()
        processed_count = 0

        # Loop sampai seluruh file selesai diproses
        while processed_count < total_files:
            # Ambil item dari data_queue selama masih ada file dan slot worker tersedia
            while len(active_futures) < n_workers and (processed_count + len(active_futures) < total_files):
                try:
                    # Timeout singkat agar tetap responsif memeriksa status loaders
                    item = data_queue.get(timeout=0.05)
                    filename, text, arrival_time = item
                    fut = executor.submit(worker_task, filename, text, arrival_time)
                    active_futures.add(fut)
                    data_queue.task_done()
                except queue.Empty:
                    # Queue sementara kosong karena loader belum selesai membaca
                    break

            # Jika ada task aktif, tunggu setidaknya satu selesai
            if active_futures:
                done, active_futures = wait(active_futures, return_when=FIRST_COMPLETED)
                for f in done:
                    res = f.result()
                    results.append(res)
                    latencies.append(res["latency"])
                    processed_count += 1
            else:
                # Jika antrean kosong dan belum ada task aktif, beri waktu sejenak
                time.sleep(0.001)

    # Pastikan seluruh loader threads selesai
    for t in loaders:
        t.join()

    pipeline_end = time.perf_counter()
    total_time = pipeline_end - pipeline_start
    throughput = total_files / total_time if total_time > 0 else 0.0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    return {
        "n_loader_threads": n_loader_threads,
        "n_workers": n_workers,
        "q_max": q_max,
        "total_files": total_files,
        "total_time": total_time,
        "throughput": throughput,
        "avg_latency": avg_latency,
        "backpressure_events": backpressure_events[0]
    }

def main():
    base_dir = Path(__file__).resolve().parent
    dataset_dir = base_dir / "dataset"
    if not dataset_dir.exists():
        print(f"[ERROR] Folder {dataset_dir} belum dibuat. Jalankan generate_dataset.py terlebih dahulu.")
        sys.exit(1)

    print("=== TEST RUN HYBRID PIPELINE ===")
    config = {"n_loader_threads": 2, "n_workers": 4, "q_max": 4}
    print(f"Konfigurasi Uji: Loaders={config['n_loader_threads']}, Workers={config['n_workers']}, Q_MAX={config['q_max']}")
    res = run_hybrid_pipeline(dataset_dir, config["n_loader_threads"], config["n_workers"], config["q_max"])
    print(f"Total Files   : {res['total_files']}")
    print(f"Total Time    : {res['total_time']:.4f} detik")
    print(f"Throughput    : {res['throughput']:.2f} file/detik")
    print(f"Avg Latency   : {res['avg_latency']:.4f} detik")
    print(f"Backpressure  : {res['backpressure_events']} kali antrean penuh")

if __name__ == "__main__":
    main()
