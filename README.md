# inSight

Privacy-first, offline semantic search for your photo library. inSight will let you search
your photos in natural language ("sunset at the beach", "my dog in the snow") using a
quantized multimodal model and a local vector index, with nothing ever leaving your device.

> **Status: Week 1 of 9.** The ingestion pipeline is done: it scans a folder, fingerprints
> each image, and stores its metadata in a local SQLite catalog. Embeddings and search
> come next.

## How it works (so far)

```
photo folder ──> scanner ──> hash + metadata ──> SQLite catalog
                 (find .jpg/   (SHA-256, size,     (one row per file,
                  .jpeg/.png)   EXIF capture time)   safe to re-run)
```

- **Incremental:** unchanged files are detected by size and modified time and are not re-hashed,
  so re-running on the same folder is fast.
- **Idempotent:** running ingest twice never creates duplicate rows.
- **Robust:** corrupt or unreadable files are logged and skipped instead of stopping the run.

Design decisions are written up in [docs/design.md](docs/design.md).

## Quick start

Requires Python 3.11+.

```
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -e ".[dev]"
```

Ingest a folder of photos:

```
insight ingest "C:\path\to\your\photos" --db data\catalog.db
```

Example on 147 screenshots: the first run adds all 147 in 1.7 s; a second run reports all 147 as unchanged.

Run the tests:

```
pytest
```

## Roadmap

- [x] Week 1: Ingestion pipeline and SQLite catalog
- [ ] Week 2: Image and text embeddings with MobileCLIP
- [ ] Week 3: Vector storage and search
- [ ] Week 4: Evaluation harness (recall@k)
- [ ] Week 5: Quantization and model export (ONNX, LiteRT)
- [ ] Week 6: Incremental indexing and hybrid search
- [ ] Weeks 7 to 8: Android app, fully offline (no internet permission)
- [ ] Week 9: Benchmarks and write-up
