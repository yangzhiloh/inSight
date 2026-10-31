# inSight design notes 

## Module 1: photo catalog
The catalog is a SQLite database with one row per image file found on disk. It stores everything we can learn about a file without any machine learning.

## Photos table
| Column     | Type    | Nullable? | Notes                                    |
|------------|---------|-----------|------------------------------------------|
| id         | INTEGER | no        | PRIMARY KEY, auto-increments             |
| path       | TEXT    | no        | UNIQUE, absolute path                    |
| size_bytes | INTEGER | no        | from os.stat                             |
| mtime_ns   | INTEGER | no        | os.stat st_mtime_ns (nanoseconds)        |
| sha256     | TEXT    | no        | 64 hex chars, indexed but NOT unique     |
| width      | INTEGER | no        | pixels, from Pillow                      |
| height     | INTEGER | no        | pixels, from Pillow                      |
| taken_at   | TEXT    | yes       | EXIF capture time, ISO 8601, no timezone |
| indexed_at | INTEGER | no        | Unix seconds when we last saw the file   |

- Primary key: id
- Unique: path
- Index: sha256

## Design decisions
**1. Path or content hash as the identity?** 
Each row is identified by its path, because the catalog tracks files on disk and one file can only be one row. The SHA-256 identifies content, so it is indexed but not unique: the same photo in two folders gives two rows with one hash. A renamed file appears as a new path with a known hash, so later stages can reuse work already done for that hash. A file edited in place keeps its path but gets a new hash.

**2. Avoiding re-hashing unchanged files** 
For each file, compare the size and mtime from os.stat (which does not open the file) with the stored values. Only hash when they differ or the file is new. This turns a full read of every file into a cheap metadata lookup. The check can miss a change if a tool resets the timestamp, so a --rehash option will force a full hash of everything.

**3. Where embeddings go** 
Embeddings will live in a separate table keyed by (photo_id, model_name). This lets two models coexist while comparing them, means switching models never rewrites the photos table, and keeps the catalog small and fast to scan.

**4. Why SQLite**
SQLite is an embedded database: a library inside the app that stores everything in a single file, with no server. Transactions are atomic, so a crash mid-write rolls back instead of corrupting data, which a half-written JSON file cannot guarantee. It also gives indexes and SQL queries. PostgreSQL needs a separate server process that a phone app cannot run, while Android ships SQLite built in.