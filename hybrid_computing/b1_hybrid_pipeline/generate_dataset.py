#!/usr/bin/env python3
"""
generate_dataset.py - Generator Dataset Tugas Hybrid Computing (Bagian B1)

Ketentuan:
- A = 2 (digit terakhir NPM 247006111192)
- Total file = 100 + 10 * A = 100 + 20 = 120 file .txt
- Menyimpan file ke folder 'dataset/'
- Nama file teratur: doc_001.txt s.d. doc_120.txt
- Berisi konten teks yang memadai untuk diproses secara komputasi.
"""

import os
import random
from pathlib import Path

# Vocabulary & kalimat bertema komputasi paralel dan terdistribusi
TOPICS = [
    "Hybrid computing combines shared memory parallelism and distributed memory systems to maximize throughput.",
    "Message Passing Interface or MPI facilitates inter-node communication across distinct physical computing nodes.",
    "ThreadPoolExecutor handles I/O bound workloads efficiently while releasing the Global Interpreter Lock in Python.",
    "ProcessPoolExecutor bypasses the GIL by spawning separate OS processes for compute-intensive tasks.",
    "Queues act as bounded buffers between loader threads and worker processes, preventing unbounded memory growth.",
    "Backpressure occurs when the processing rate of consumer workers falls behind the generation rate of producer loaders.",
    "Amdahl's law demonstrates that the serial portion of an algorithm fundamentally constrains maximum theoretical speedup.",
    "Gustafson's law provides an alternative perspective by scaling the problem size proportionally with compute resources.",
    "Network latency and serialization overhead represent critical bottlenecks in large-scale cluster computing environments.",
    "Cache locality and NUMA memory architecture dictate performance characteristics in multi-socket server motherboards.",
    "Pipelining breaks complex multi-stage tasks into sequential overlapping phases executed by specialized execution units.",
    "Strong scaling evaluates execution time reduction as worker count increases for a strictly fixed overall problem size.",
    "Weak scaling measures throughput retention when both workload size and processor count increase by identical ratios.",
    "Oversubscription takes place when active worker processes exceed available hardware execution units leading to context switches.",
    "Deadlock prevention requires rigorous ordering of resource acquisition across all concurrent threads and processes.",
    "Tokenization and regular expression parsing represent CPU-intensive text preprocessing stages in data mining pipelines.",
    "Stopword removal eliminates highly frequent grammatical particles allowing algorithms to focus on meaningful semantic terms.",
    "Throughput is defined as total processed items divided by total wall-clock duration in seconds.",
    "Latency measures the elapsed residence time of an individual unit of work from arrival to complete resolution.",
    "Intel Core hybrid architectures feature high-performance P-cores alongside energy-efficient E-cores for heterogeneous loads."
]

def generate_text_content(file_index: int, target_words: int = 500) -> str:
    """Menghasilkan teks sintetis yang kaya kata untuk kebutuhan pengujian pipeline."""
    # Seed per file agar konten bervariasi namun deterministik
    rng = random.Random(42 + file_index * 13)
    paragraphs = []
    current_words = 0

    while current_words < target_words:
        para_sentences = rng.sample(TOPICS, k=min(6, len(TOPICS)))
        rng.shuffle(para_sentences)
        para_text = " ".join(para_sentences)
        paragraphs.append(para_text)
        current_words += len(para_text.split())

    header = f"=== DOCUMENT {file_index:03d} (Hybrid Computing Dataset Benchmark) ===\n"
    return header + "\n\n".join(paragraphs) + "\n"

def create_dataset(output_dir: Path, num_files: int = 120):
    """Membuat folder dataset dan menulis file .txt secara berurutan."""
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Memulai pembuatan {num_files} file teks pada: {output_dir.resolve()}")

    for i in range(1, num_files + 1):
        filename = f"doc_{i:03d}.txt"
        file_path = output_dir / filename
        content = generate_text_content(i, target_words=450)
        file_path.write_text(content, encoding="utf-8")

    print(f"[SUCCESS] Berhasil membuat {num_files} file .txt di folder '{output_dir.name}'.")

def main():
    base_dir = Path(__file__).resolve().parent
    dataset_dir = base_dir / "dataset"
    a_param = 2
    total_files = 100 + (10 * a_param)  # 120 file
    create_dataset(dataset_dir, total_files)

if __name__ == "__main__":
    main()
