# Tugas Praktikum Hybrid Computing (Bagian B)

**Mata Kuliah**: Parallel & Distributed Computing  
**Dosen Pengampu**: Ir. Randi Rizal, Ph.D.  
**Nama**: Muhammad Kent Faiq Arifien  
**NPM**: 247006111192 (Kelas G)  
**Parameter Pribadi**: Digit terakhir NPM = 2 ($A = 2$)  

---

## 1. Deskripsi Project
Repositori ini berisi implementasi kode program, otomasi benchmark, visualisasi grafik, dan analisis performa untuk **Bagian B: Praktikum (50%)** tugas mata kuliah Parallel & Distributed Computing.

Eksperimen terdiri atas 3 bagian utama:
1. **B1. Hybrid Pipeline**: Pipeline produsen-konsumen multi-threaded (I/O loader) dan multi-process (worker pemroses) dengan antrean terbatas (*bounded queue*) untuk menguji throughput, latency, dan efek *backpressure*.
2. **B2. Strong Scaling MPI + ProcessPool**: Pengukuran *strong scaling* menggunakan kombinasi proses terdistribusi (MPI) dan proses lokal (*ProcessPoolExecutor*) untuk estimasi Monte Carlo dengan $SAMPLES\_PER\_TASK = 220.000$, serta analisis fenomena *oversubscription*.
3. **B3. Global Word Count**: Pengolahan kata global pada 32 file teks nyata menggunakan MPI antar-rank dan perbandingan performa antara `ThreadPoolExecutor` vs `ProcessPoolExecutor` di dalam setiap rank.

---

## 2. Spesifikasi Laptop Pengujian
Seluruh program dijalankan dan diukur secara nyata pada laptop dengan spesifikasi perangkat keras berikut:

- **Perangkat**: Laptop Pengujian Pribadi
- **CPU**: 13th Gen Intel® Core™ i5-13450HX
- **Physical Cores**: 14 Core (6 Performance-Cores + 8 Efficient-Cores, target parameter: 14 Core)
- **Logical Threads**: 20 Thread (Hyper-Threading / SMT)
- **Base Clock**: 2.40 GHz
- **RAM**: 16 GB DDR5 (Usable: 15.71 GB, Speed: 4800 MT/s)
- **GPU**: NVIDIA GeForce RTX (6 GB VRAM)
- **Storage**: 477 GB NVMe SSD
- **Sistem Operasi**: Windows 11 Pro 64-bit (x64)
- **Versi Python**: Python 3.11.9 (64-bit)
- **Implementasi MPI**: Microsoft MPI (MS-MPI) v10.1.12498.52
- **Binding Python MPI**: mpi4py v4.1.2

---

## 3. Struktur Direktori Project
```text
hybrid_computing/
├── README.md                   # Dokumentasi lengkap dan panduan eksekusi
├── requirements.txt            # Daftar dependensi library Python
├── check_environment.py        # Script inspeksi otomatis lingkungan sistem
│
├── b1_hybrid_pipeline/         # BAGIAN B1
│   ├── dataset/                # Berisi 120 file teks sintetis (doc_001.txt s.d. doc_120.txt)
│   ├── results/                # Output CSV dan grafik B1
│   │   ├── b1_results.csv
│   │   ├── throughput_vs_workers.png
│   │   ├── time_vs_workers.png
│   │   └── qmax_comparison.png
│   ├── generate_dataset.py     # Script pembuat 120 file teks (100 + 10*A)
│   ├── hybrid_pipeline.py      # Implementasi pipeline modular (I/O threads + Queue + Worker pool)
│   ├── run_benchmark.py        # Otomasi 24 kombinasi eksperimen
│   ├── plot_results.py         # Generator grafik visualisasi hasil B1
│   └── analyze_results.py      # Script analisis performa & backpressure
│
├── b2_mpi_processpool/         # BAGIAN B2
│   ├── results/                # Output CSV dan grafik B2
│   │   ├── b2_results.csv
│   │   ├── b2_makespan.png
│   │   ├── b2_speedup.png
│   │   └── b2_efficiency.png
│   ├── mpi_processpool.py      # Implementasi perbaikan bug slide 20 + Monte Carlo Pi
│   ├── run_benchmark.py        # Otomasi 9 kombinasi rank x worker
│   ├── plot_results.py         # Generator grafik makespan, speedup, efisiensi
│   └── analyze_results.py      # Script analisis speedup & oversubscription
│
└── b3_global_wordcount/        # BAGIAN B3
    ├── dataset/                # Berisi 32 file artikel teks nyata
    ├── results/                # Output CSV dan grafik B3
    │   ├── b3_results.csv
    │   └── b3_method_comparison.png
    ├── prepare_dataset.py      # Script pembuat dataset 32 artikel teks nyata
    ├── wordcount.py            # Program MPI Global Word Count (ThreadPool vs ProcessPool)
    ├── run_benchmark.py        # Otomasi benchmark kedua metode (18 kombinasi)
    ├── plot_results.py         # Generator grafik komparasi metode
    └── analyze_results.py      # Script analisis I/O vs regex & GIL
```

---

## 4. Instalasi dan Setup Lingkungan

### 4.1. Instalasi Library Python
Jalankan perintah berikut di terminal (PowerShell / Command Prompt):
```powershell
python -m pip install -r requirements.txt
```
Library yang dibutuhkan:
- `numpy`: Komputasi array numerik
- `pandas`: Pengolahan data CSV hasil benchmark
- `matplotlib`: Visualisasi grafik ilmiah
- `psutil`: Deteksi spesifikasi prosesor dan memori sistem
- `mpi4py`: Antarmuka Python untuk Message Passing Interface

### 4.2. Instalasi Microsoft MPI pada Windows 11
Jika belum terpasang, instal MS-MPI dan MS-MPI SDK via winget:
```powershell
winget install Microsoft.msmpi --silent --accept-package-agreements --accept-source-agreements
winget install Microsoft.msmpisdk --silent --accept-package-agreements --accept-source-agreements
```
*Catatan*: Pastikan path `C:\Program Files\Microsoft MPI\Bin` terdaftar di Environment Variable `PATH` sistem Anda.

### 4.3. Verifikasi Lingkungan
Jalankan script pengecekan:
```powershell
python check_environment.py
```

---

## 5. Panduan Menjalankan Program

### 5.1. Bagian B1 — Hybrid Pipeline

1. **Membuat Dataset (120 file .txt)**:
   ```powershell
   python b1_hybrid_pipeline/generate_dataset.py
   ```
2. **Uji Coba Single Run**:
   ```powershell
   python b1_hybrid_pipeline/hybrid_pipeline.py
   ```
3. **Menjalankan Otomasi Benchmark (24 Konfigurasi)**:
   ```powershell
   python b1_hybrid_pipeline/run_benchmark.py
   ```
   *Parameter yang diuji*:
   - `N_LOADER_THREADS`: 1, 2, 4
   - `N_WORKERS`: 1, 2, 4, 14
   - `Q_MAX`: 4, 32
   *Hasil*: Tersimpan di `b1_hybrid_pipeline/results/b1_results.csv`.
4. **Membuat Grafik Visualisasi**:
   ```powershell
   python b1_hybrid_pipeline/plot_results.py
   ```
5. **Melihat Analisis Otomatis**:
   ```powershell
   python b1_hybrid_pipeline/analyze_results.py
   ```

---

### 5.2. Bagian B2 — Strong Scaling MPI + ProcessPool

1. **Uji Coba Single Run (misal: 2 MPI Ranks, 2 Workers per Rank)**:
   ```powershell
   mpiexec -n 2 python b2_mpi_processpool/mpi_processpool.py --workers 2
   ```
2. **Menjalankan Otomasi Benchmark (9 Konfigurasi)**:
   ```powershell
   python b2_mpi_processpool/run_benchmark.py
   ```
   *Parameter yang diuji*:
   - Kombinasi Rank $\in \{1, 2, 4\} \times$ Workers $\in \{1, 2, 4\}$
   *Hasil*: Tersimpan di `b2_mpi_processpool/results/b2_results.csv`.
3. **Membuat Grafik Visualisasi**:
   ```powershell
   python b2_mpi_processpool/plot_results.py
   ```
4. **Melihat Analisis Otomatis (Termasuk Evaluasi Oversubscription)**:
   ```powershell
   python b2_mpi_processpool/analyze_results.py
   ```

---

### 5.3. Bagian B3 — Global Word Count

1. **Menyiapkan Dataset (32 File Teks Nyata)**:
   ```powershell
   python b3_global_wordcount/prepare_dataset.py
   ```
2. **Uji Coba Eksekusi Single Run**:
   - Versi ThreadPoolExecutor:
     ```powershell
     mpiexec -n 2 python b3_global_wordcount/wordcount.py --method threads --workers 2
     ```
   - Versi ProcessPoolExecutor:
     ```powershell
     mpiexec -n 2 python b3_global_wordcount/wordcount.py --method processes --workers 2
     ```
3. **Menjalankan Otomasi Benchmark (18 Konfigurasi)**:
   ```powershell
   python b3_global_wordcount/run_benchmark.py
   ```
   *Hasil*: Tersimpan di `b3_global_wordcount/results/b3_results.csv`.
4. **Membuat Grafik Komparasi Metode**:
   ```powershell
   python b3_global_wordcount/plot_results.py
   ```
5. **Melihat Analisis Otomatis**:
   ```powershell
   python b3_global_wordcount/analyze_results.py
   ```

---

## 6. Panduan Screenshot untuk Laporan PDF

Saat menyusun laporan tugas dalam format PDF, sertakan tangkapan layar (*screenshot*) berikut:

1. **Screenshot Pengecekan Lingkungan**:
   - Jalankan `python check_environment.py` dan screenshot tampilan terminal yang menampilkan Python version, CPU Intel Core i5-13450HX, 14 physical cores, RAM, dan status MS-MPI.
2. **Screenshot Bagian B1**:
   - Screenshot output terminal saat `run_benchmark.py` dan `analyze_results.py` selesai berjalan.
   - Cantumkan ketiga grafik hasil plot:
     - `throughput_vs_workers.png`
     - `time_vs_workers.png`
     - `qmax_comparison.png`
   - Cantumkan tabel hasil `b1_results.csv`.
3. **Screenshot Bagian B2**:
   - Screenshot output terminal eksekusi single run `mpi_processpool.py` (yang menunjukkan teks `MPI ranks`, `Workers per rank`, `Estimated worker processes`, dan `Oversubscription indicator`).
   - Screenshot output terminal `analyze_results.py`.
   - Cantumkan ketiga grafik:
     - `b2_makespan.png`
     - `b2_speedup.png`
     - `b2_efficiency.png`
4. **Screenshot Bagian B3**:
   - Screenshot output terminal eksekusi `wordcount.py` untuk kedua metode (format blok `GLOBAL WORD COUNT` beserta Top 10 kata).
   - Screenshot grafik komparasi `b3_method_comparison.png`.
   - Screenshot tabel hasil `b3_results.csv`.
