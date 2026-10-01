#!/usr/bin/env python3
"""
prepare_dataset.py - Menyiapkan Dataset Teks Nyata untuk Global Word Count (B3)

Ketentuan:
- Minimal 30 file teks nyata.
- Disimpan di folder: b3_global_wordcount/dataset/
- Memuat teks dalam Bahasa Indonesia dan Bahasa Inggris agar stopword:
  'dan', 'yang', 'di', 'the', 'of', 'and' dapat teruji pembuangannya secara nyata.
"""

from pathlib import Path

# Kumpulan teks nyata (artikel teknologi, sistem komputasi, sejarah komputer, dan esai ilmiah)
ARTICLES = [
    ("artikel_01_sejarah_komputasi.txt", """
    Sejarah komputasi modern dimulai dari perkembangan mesin analitik oleh Charles Babbage dan pemikiran visioner Ada Lovelace.
    Pada abad kedua puluh, penemuan tabung hampa dan transistor memungkinkan pembuatan komputer elektronik pertama seperti ENIAC di Amerika Serikat.
    Perkembangan arsitektur von Neumann meletakkan dasar bagi komputer terprogram yang memisahkan memori dan unit pemrosesan pusat.
    Seiring berjalannya waktu, sirkuit terpadu atau integrated circuit memungkinkan miliaran transistor dimampatkan ke dalam satu chip silikon mikroprosesor.
    Sistem komputer modern kini mampu melakukan miliaran instruksi per detik dan menjadi tulang punggung revolusi informasi digital.
    """),

    ("artikel_02_distributed_systems.txt", """
    Distributed computing refers to a model where components located on networked computers communicate and coordinate actions.
    The primary goal of a distributed system is to achieve high availability, fault tolerance, and horizontal scalability.
    Key challenges in distributed systems include partial failures, network partitions, latency spikes, and clock synchronization.
    The CAP theorem states that a distributed data store can simultaneously provide at most two out of three guarantees:
    consistency, availability, and partition tolerance. Modern platforms utilize consensus algorithms like Raft and Paxos to maintain state.
    """),

    ("artikel_03_hybrid_computing_concept.txt", """
    Konsep hybrid computing mengintegrasikan model shared memory dan distributed memory ke dalam satu kesatuan sistem komputasi berkinerja tinggi.
    Di tingkat inter-node, proses berkomunikasi melalui protokol message passing seperti MPI melalui jaringan interkoneksi berkecepatan tinggi.
    Di dalam masing-masing node komputasi, thread atau sub-proses berbagi memori lokal melalui multi-threading atau OpenMP.
    Pendekatan ini meminimalkan overhead komunikasi antar-node dan memaksimalkan pemanfaatan arsitektur prosesor multi-core modern.
    Perancangan algoritma hybrid menuntut pemahaman mendalam tentang hierarki cache, latensi bus memori, dan topologi jaringan.
    """),

    ("artikel_04_python_gil_analysis.txt", """
    The Global Interpreter Lock or GIL is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once.
    This lock is necessary primarily because CPython's memory management is not thread-safe and relies on reference counting.
    For I/O-bound operations such as reading disk files or querying network sockets, Python threads release the GIL and achieve concurrency.
    However, for CPU-bound tasks such as heavy numerical calculation or regular expression matching, multi-threading cannot achieve speedup.
    To harness multiple physical CPU cores in Python, developers must leverage multiprocessing or process pools that run separate interpreter instances.
    """),

    ("artikel_05_parallel_file_io.txt", """
    Operasi input dan output pada sistem berkas skala besar sering kali menjadi hambatan utama dalam pipeline pemrosesan data analitik.
    Ketika ratusan proses secara bersamaan mencoba membaca berkas dari sistem penyimpanan yang sama, contention pada disk I/O tidak terhindarkan.
    Teknik buffering, prefetching, dan penggunaan distributed file systems seperti HDFS atau Lustre membantu mendistribusikan beban I/O.
    Dalam arsitektur pipeline, thread pembaca bertindak sebagai loader yang memuat data ke memori sebelum diserahkan kepada worker pemroses.
    Pemisahan peran antara I/O thread dan CPU worker memastikan pemanfaatan siklus komputasi prosesor tetap optimal tanpa harus menganggur menunggu disk.
    """),

    ("artikel_06_mapreduce_paradigm.txt", """
    The MapReduce programming model was designed by Google to simplify data processing across vast clusters of commodity hardware.
    The Map phase processes input key-value pairs to generate intermediate key-value pairs representing transformed data records.
    The intermediate values associated with the same key are grouped together by an automatic shuffle and sort mechanism.
    The Reduce phase then merges all values associated with the key to form a smaller set of aggregated final results.
    Global word count is the classic canonical example that demonstrates the full lifecycle of mapping tokens and reducing frequency counts.
    """),

    ("artikel_07_cache_memory_hierarchy.txt", """
    Hierarki memori komputer tersusun dari register prosesor, cache Level satu, cache Level dua, cache Level tiga, memori utama RAM, dan media penyimpanan sekunder.
    Semakin dekat posisi memori ke unit pemroses, semakin cepat waktu akses yang diperoleh namun dengan kapasitas penyimpanan yang semakin terbatas.
    Prinsip lokalitas spasial dan lokalitas temporal menjadi dasar perancangan cache untuk memprediksi data yang akan dieksekusi berikutnya.
    Kegagalan cache atau cache miss memaksa prosesor menunggu ratusan siklus clock hingga data berhasil diambil dari RAM utama.
    Dalam pemrograman berkinerja tinggi, penataan struktur data yang ramah terhadap cache line menjadi faktor penentu kecepatan komputasi.
    """),

    ("artikel_08_openmp_multithreading.txt", """
    OpenMP is an open specification for multi-platform shared-memory parallel programming in C, C++, and Fortran compilers.
    It provides a set of compiler directives, library routines, and environment variables that control run-time execution parameters.
    The fork-join model forms the foundation of OpenMP execution where a master thread forks a team of parallel worker threads.
    Each thread in the team executes the statements inside the parallel region simultaneously across multiple physical CPU cores.
    Synchronization constructs such as critical sections, barriers, and atomic directives prevent data races on shared memory variables.
    """),

    ("artikel_09_cloud_computing_infrastructure.txt", """
    Komputasi awan menyediakan sumber daya infrastruktur, platform, dan perangkat lunak melalui jaringan internet dengan model pembayaran sesuai pemakaian.
    Pusat data modern menampung puluhan ribu server yang dihubungkan dengan topologi jaringan leaf-spine berkecepatan tinggi.
    Teknologi virtualisasi dan kontainerisasi seperti Docker dan Kubernetes memungkinkan isolasi aplikasi yang efisien serta deployment otomatis.
    Elastisitas komputasi awan memungkinkan alokasi sumber daya secara dinamis saat lonjakan lalu lintas pengguna terjadi.
    Tantangan utama komputasi awan mencakup keamanan data, privasi pengguna, kepatuhan regulasi, dan manajemen biaya operasional server.
    """),

    ("artikel_10_network_protocols_cluster.txt", """
    Interconnection networks inside supercomputing clusters demand extremely high bandwidth and ultra-low communication latency.
    Technologies such as InfiniBand, Omni-Path, and RoCE or RDMA over Converged Ethernet bypass OS kernel networking stacks.
    Remote Direct Memory Access allows an MPI process to read or write directly into the virtual memory space of a remote node.
    This zero-copy architecture eliminates CPU involvement in data transfer operations, maximizing communication throughput.
    Point-to-point and collective communications in MPI heavily rely on the underlying hardware fabric topology to avoid link congestion.
    """),

    ("artikel_11_operating_system_scheduling.txt", """
    Penjadwal sistem operasi bertanggung jawab untuk mengalokasikan waktu prosesor bagi semua thread dan proses yang sedang berjalan.
    Algoritma penjadwalan seperti Round Robin, Completely Fair Scheduler, dan Priority Preemptive berusaha menyeimbangkan keadilan dan latensi respons.
    Ketika jumlah thread aktif melebihi jumlah core fisik prosesor, overhead context switching meningkat secara signifikan.
    Penyimpanan register prosesor dan pergantian tabel halaman virtual memory menghabiskan siklus komputasi yang berharga.
    Oleh karena itu, penentuan jumlah worker dalam thread pool atau process pool harus disesuaikan dengan kapasitas core perangkat keras.
    """),

    ("artikel_12_regex_and_tokenization.txt", """
    Text tokenization is the foundational preliminary step in modern natural language processing and information retrieval pipelines.
    Regular expressions provide a concise pattern matching language to filter punctuation, strip whitespace, and isolate alphanumeric words.
    Evaluating complex regular expressions across millions of text tokens demands substantial CPU cycles and memory bandwidth.
    Case normalization transforms all character sequences to lowercase so that identical words with different capitalizations match correctly.
    Stopword removal filters frequent functional words that carry minimal semantic information, shrinking the feature dictionary size.
    """),

    ("artikel_13_amdahl_law_implications.txt", """
    Hukum Amdahl menyatakan bahwa percepatan maksimum yang dapat dicapai oleh program paralel dibatasi oleh fraksi serial dari algoritma tersebut.
    Bahkan jika suatu sistem memiliki jumlah prosesor tak terbatas, speedup teoritis tidak akan pernah melampaui kebalikan dari komponen serial.
    Sebagai contoh, jika sebuah program memiliki sepuluh persen bagian yang wajib berjalan secara sekuensial, speedup maksimum adalah sepuluh kali lipat.
    Konsekuensi hukum ini menekankan pentingnya mereduksi bagian serial dan meminimalkan ketergantungan data antar-proses.
    Dalam praktiknya, hukum Amdahl memandu arsitek perangkat lunak untuk mengidentifikasi bottleneck utama sebelum menambah prosesor.
    """),

    ("artikel_14_gustafson_law_scaling.txt", """
    Gustafson's law provides a complementary perspective to Amdahl's law by arguing that parallel problems naturally expand in scale.
    As computational resources increase, scientists and engineers do not simply solve fixed-size problems faster, but solve larger, more detailed models.
    Scaled speedup assumes that parallel workload scales linearly with the number of processors, keeping execution time relatively constant.
    This perspective underpins weak scaling benchmarks in supercomputers where problem dimensions expand alongside processor counts.
    Understanding the interplay between strong scaling and weak scaling is essential for proper supercomputer benchmarking and capacity planning.
    """),

    ("artikel_15_database_indexing_structures.txt", """
    Struktur data indeks pada basis data relasional seperti B-Tree dan B+ Tree dirancang untuk mempercepat pencarian record pada media penyimpanan sekunder.
    Indeks mengorganisir kunci pencarian ke dalam pohon seimbang dengan percabangan yang lebar untuk meminimalkan jumlah akses blok disk.
    Pada basis data noSQL dan search engine, indeks terbalik atau inverted index memetakan setiap kata kunci ke daftar dokumen yang memuatnya.
    Proses pembangunan inverted index memerlukan tokenisasi teks berskala besar yang sering kali diparalelkan menggunakan paradigma map-reduce.
    Pembaruan indeks secara konkuren menuntut mekanisme penguncian bertingkat untuk menjaga konsistensi tanpa memblokir pembacaan.
    """),

    ("artikel_16_gpu_accelerated_computing.txt", """
    Graphics Processing Units or GPUs have evolved from dedicated rasterization engines into powerful general-purpose massively parallel accelerators.
    While a typical modern CPU comprises between eight and thirty-two powerful cores optimized for sequential latency, a GPU houses thousands of cores.
    The Single Instruction Multiple Threads or SIMT architecture enables high arithmetic throughput for data-parallel algorithms like matrix multiplication.
    Frameworks such as CUDA and OpenCL allow developers to write compute kernels that execute across streaming multiprocessors.
    Data transfer across the PCI Express bus between host CPU memory and device GPU memory remains a critical performance consideration.
    """),

    ("artikel_17_deadlock_detection_prevention.txt", """
    Kebuntuan atau deadlock adalah kondisi ketika dua atau lebih proses saling menunggu sumber daya yang sedang ditahan oleh proses lain.
    Empat kondisi Coffman yang harus terpenuhi agar terjadi deadlock adalah mutual exclusion, hold and wait, no preemption, dan circular wait.
    Dalam komputasi hybrid MPI dan threading, deadlock dapat terjadi jika urutan pengiriman pesan dan perolehan lock tidak teratur dengan disiplin.
    Sebagai contoh, jika Rank A menunggu pesan dari Rank B sementara Rank B menunggu lock lokal yang sedang ditahan oleh thread lain di Rank A.
    Pencegahan deadlock dapat dilakukan dengan menerapkan urutan perolehan sumber daya secara global atau menggunakan non-blocking communication primitives.
    """),

    ("artikel_18_microservices_architecture.txt", """
    Microservice architecture decomposes monolithic enterprise applications into collections of loosely coupled, independently deployable services.
    Each microservice encapsulates a distinct business capability and communicates with peer services through lightweight APIs or message brokers.
    Decentralized data management allows each service to select the most suitable database technology, embracing polyglot persistence.
    Continuous integration and continuous deployment pipelines automate testing, container building, and deployment into cluster orchestrators.
    Observability tools such as distributed tracing, structured logging, and metric aggregators monitor service interactions and latency bottlenecks.
    """),

    ("artikel_19_quantum_computing_principles.txt", """
    Komputasi kuantum memanfaatkan fenomena mekanika kuantum seperti superposisi dan keterikatan kuantum atau entanglement untuk memproses data.
    Berbeda dengan bit klasik yang hanya dapat bernilai nol atau satu, qubit dapat berada dalam kombinasi linier dari kedua status tersebut.
    Algoritma kuantum seperti algoritma Shor dan algoritma Grover menawarkan percepatan eksponensial dan kuadratik untuk masalah matematika tertentu.
    Tantangan fisik terbesar dalam realisasi komputer kuantum praktis adalah dekoherensi kuantum akibat kebisingan lingkungan termal dan elektromagnetik.
    Komputasi hybrid klasik-kuantum memadukan CPU tradisional untuk kontrol logika dengan prosesor kuantum untuk komputasi aljabar linier khusus.
    """),

    ("artikel_20_big_data_streaming_analytics.txt", """
    Streaming analytics processes continuous feeds of real-time event records with sub-second latencies rather than waiting for periodic batch intervals.
    Distributed streaming engines like Apache Flink, Apache Spark Streaming, and Kafka Streams provide event-time processing and windowing constructs.
    Sliding windows, tumbling windows, and session windows partition unbounded data streams into finite chunks for aggregation.
    Exactly-once processing guarantees ensure that state updates remain mathematically accurate even when worker nodes crash during stream ingestion.
    State backends utilize local memory and persistent storage to track aggregate counts, moving averages, and pattern detections over time.
    """),

    ("artikel_21_compiler_optimizations_parallel.txt", """
    Pengoptimalan kompilator memainkan peran krusial dalam mengubah kode sumber tingkat tinggi menjadi instruksi biner yang efisien pada target prosesor.
    Teknik seperti loop unrolling, vectorization menggunakan instruksi SIMD, dan function inlining membantu memaksimalkan pemanfaatan unit fungsional CPU.
    Kompilator modern mampu menganalisis dependensi data untuk memvalidasi apakah suatu loop dapat diparalelkan secara otomatis tanpa race condition.
    Petunjuk kompilator atau pragmas membantu memberikan informasi eksplisit mengenai aliasing memori dan batas iterasi kepada optimizer.
    Efisiensi kode biner yang dihasilkan secara langsung menentukan throughput komputasi pada kernel pemrosesan teks dan kalkulasi numerik.
    """),

    ("artikel_22_storage_systems_nas_san.txt", """
    Network Attached Storage and Storage Area Networks furnish centralized file and block storage solutions for enterprise computing clusters.
    NAS devices deliver file-level storage accessed through network protocols such as NFS and SMB over standard Ethernet infrastructure.
    SAN networks provide block-level storage over dedicated high-speed Fibre Channel or iSCSI networks, appearing to servers as local physical disks.
    Solid state drives utilizing NVMe protocols over PCIe lanes dramatically reduce access latency compared to traditional mechanical spinning platters.
    Data deduplication and snapshot mechanisms conserve storage capacity and facilitate continuous disaster recovery workflows.
    """),

    ("artikel_23_cryptography_and_hashing.txt", """
    Kriptografi modern menjamin kerahasiaan, integritas data, dan autentikasi dalam komunikasi digital melalui algoritma matematis yang kompleks.
    Fungsi hash kriptografis seperti SHA-256 memetakan data dengan ukuran sembarang menjadi digest berukuran tetap yang unik secara deterministik.
    Sifat one-way dan collision resistance memastikan bahwa sangat tidak mungkin untuk merekonstruksi data asli atau menemukan dua masukan berbeda dengan hash yang sama.
    Operasi hashing intensif sering digunakan dalam verifikasi integritas berkas, struktur blockchain, dan penyimpanan kata sandi terproteksi.
    Implementasi hashing paralel memanfaatkan instruksi prosesor khusus untuk memproses blok data independen secara simultan.
    """),

    ("artikel_24_graph_algorithms_parallel.txt", """
    Graph processing algorithms analyze complex networks of interconnected entities across social graphs, biological networks, and transportation grids.
    Fundamental graph operations including Breadth-First Search, PageRank, and Single-Source Shortest Paths exhibit irregular memory access patterns.
    Partitioning large graphs across distributed cluster nodes requires minimizing edge cuts to reduce inter-process communication volume.
    Bulk Synchronous Parallel or BSP frameworks execute computation in supersteps separated by global synchronization barriers.
    Managing dynamic frontier sets efficiently across multiple threads demands concurrent lock-free queue implementations.
    """),

    ("artikel_25_artificial_intelligence_inference.txt", """
    Inferensi model kecerdasan buatan bertugas menjalankan model jaringan saraf tiruan terlatih untuk memprediksi data masukan baru secara cepat.
    Kuantisasi bobot model dari presisi tunggal tiga puluh dua bit ke format integer delapan bit memperkecil konsumsi memori dan mempercepat kalkulasi.
    Teknik batching menggabungkan beberapa permintaan inferensi menjadi satu operasi matriks besar untuk memaksimalkan throughput akselerator komputasi.
    Sistem inferensi real-time harus memenuhi batasan service level agreement dengan latensi rendah pada sistem transaksi digital dan otomotif otonom.
    Optimasi pipeline inferensi melibatkan pemangkasan bobot yang tidak aktif dan penggabungan lapisan konvolusi dengan fungsi aktivasi.
    """),

    ("artikel_26_fault_tolerance_heartbeats.txt", """
    Fault tolerance mechanisms ensure that a distributed computing cluster continues correct operation despite the unexpected failure of individual nodes.
    Heartbeat protocols periodically transmit keep-alive packets between worker nodes and coordinator processes to monitor health status.
    When a coordinator detects missed heartbeats exceeding a predefined timeout threshold, it initiates failover procedures and task reassignment.
    Checkpointing algorithms periodically serialize and persist complete program states to distributed storage for rollback recovery.
    Message logging and deterministic replay enable failed processes to reconstruct their state without requiring full cluster restarts.
    """),

    ("artikel_27_virtual_memory_paging.txt", """
    Memori virtual menyediakan ilusi ruang alamat memori yang besar, privat, dan seragam bagi setiap proses yang berjalan di sistem operasi.
    Manajemen memori menggunakan Memory Management Unit pada prosesor untuk menerjemahkan alamat virtual menjadi alamat fisik melalui tabel halaman.
    Ketika proses mengakses halaman memori yang belum dipetakan ke RAM fisik, sistem operasi memicu page fault untuk memuat halaman dari disk.
    Translation Lookaside Buffer bertindak sebagai cache berkecepatan tinggi untuk translasi alamat guna menghindari akses memori berulang ke tabel halaman.
    Fragmentasi memori dan thrashing terjadi ketika sistem terlalu sering melakukan swap halaman antara RAM dan disk sekunder.
    """),

    ("artikel_28_message_queues_broker.txt", """
    Message broker systems such as Apache Kafka and RabbitMQ decouple data producers from asynchronous consumers across enterprise architectures.
    Brokers store incoming message streams in partitioned append-only commit logs that support high ingestion throughput and fault tolerance.
    Consumer groups enable horizontal scaling by assigning distinct topic partitions to individual consumer instances across worker nodes.
    Backpressure regulation ensures that slow consumers signal upstream publishers to throttle throughput, preventing buffer overflow exhaustion.
    Message acknowledgment protocols guarantee delivery semantics ranging from at-most-once to at-least-once and strictly idempotent processing.
    """),

    ("artikel_29_distributed_consensus_raft.txt", """
    Algoritma konsensus Raft dirancang agar lebih mudah dipahami dan diimplementasikan dibandingkan algoritma Paxos klasik.
    Raft membagi masalah konsensus menjadi sub-masalah independen yaitu pemilihan pemimpin, replikasi log, dan keamanan status mesin.
    Sebuah node dalam kluster Raft dapat berada dalam salah satu dari tiga peran: pemimpin, pengikut, atau kandidat pemilihan.
    Pemimpin kluster bertanggung jawab menerima perintah dari klien, menuliskannya ke log lokal, dan mereplikasikannya ke mayoritas node pengikut.
    Dengan memanfaatkan quorum mayoritas, Raft menjamin bahwa sistem tetap konsisten meskipun beberapa node mengalami kegagalan jaringan atau crash.
    """),

    ("artikel_30_data_compression_algorithms.txt", """
    Data compression algorithms reduce the physical storage footprint and network transmission bandwidth required for digital information.
    Lossless algorithms such as Huffman coding, Lempel-Ziv-Welch, and Snappy guarantee that the original data stream can be perfectly reconstructed.
    Entropy encoding assigns shorter variable-length bit codes to frequently occurring symbols while assigning longer codes to rare symbols.
    In distributed computing environments, compressing intermediate map results before network shuffle significantly diminishes network transfer time.
    The trade-off between CPU compression decompression latency and network bandwidth savings dictates optimal compression level selection.
    """),

    ("artikel_31_performance_profiling_tools.txt", """
    Alat pemrofilan kinerja perangkat lunak membantu pengembang menganalisis konsumsi waktu eksekusi dan alokasi memori pada fungsi program.
    Pemrofil berbasis sampling secara berkala memeriksa program counter prosesor untuk membangun estimasi statistik waktu yang dihabiskan.
    Pemrofil berbasis instrumentasi menyisipkan kode pengukuran pada setiap fungsi untuk mencatat durasi panggilan secara tepat dan menyeluruh.
    Visualisasi flame graph menampilkan tumpukan panggilan fungsi yang memudahkan identifikasi jalur eksekusi yang paling banyak menyita waktu CPU.
    Analisis profil merupakan langkah fundamental sebelum menerapkan paralelisasi atau optimasi algoritma pada perangkat lunak berskala besar.
    """),

    ("artikel_32_heterogeneous_computing_future.txt", """
    Heterogeneous computing architectures integrate diverse types of execution cores into single unified processing platforms to maximize efficiency.
    Modern mobile and desktop processors combine high-performance cores with power-efficient cores to dynamically handle variable computing workloads.
    Domain-specific accelerators such as Tensor Processing Units, Neural Processing Units, and FPGAs deliver orders of magnitude higher throughput per watt.
    Software stacks must evolve to intelligently schedule heterogeneous tasks across CPUs, GPUs, and specialized accelerators without manual intervention.
    Unified virtual memory architectures simplify programming by allowing host and accelerator processors to seamlessly share pointers to identical address spaces.
    """)
]

def generate_b3_dataset(target_dir: Path):
    """Menulis seluruh file teks nyata ke folder dataset target."""
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Menyiapkan {len(ARTICLES)} file teks nyata pada {target_dir.resolve()}...")

    for filename, content in ARTICLES:
        file_path = target_dir / filename
        # Bersihkan indentasi multiline string
        cleaned_text = "\n".join(line.strip() for line in content.strip().splitlines())
        file_path.write_text(cleaned_text + "\n", encoding="utf-8")

    print(f"[SUCCESS] Berhasil menulis {len(ARTICLES)} file teks nyata (minimal 30 file terpenuhi)!")

def main():
    base_dir = Path(__file__).resolve().parent
    dataset_dir = base_dir / "dataset"
    generate_b3_dataset(dataset_dir)

if __name__ == "__main__":
    main()
