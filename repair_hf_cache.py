"""
Fix broken HuggingFace cache symlinks on Windows.
On Windows without Developer Mode, HF creates pointer files containing 
relative paths like '../../blobs/HASH' instead of actual symlinks.
This script replaces those pointer files with actual blob content.
"""
import shutil
from pathlib import Path

CACHE_DIR = Path("models/bge_cache/models--BAAI--bge-m3")

def fix_snapshot(snapshot_dir):
    print(f"\n--- Fixing: {snapshot_dir.name} ---")
    
    for file_path in snapshot_dir.rglob("*"):
        if file_path.is_dir():
            continue
        
        size = file_path.stat().st_size
        
        # Read file content to check if it's a pointer
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore').strip()
        except:
            continue
        
        # Check if it's a relative path pointer (e.g., "../../blobs/HASH")
        if "blobs/" in content and size < 200:
            # Resolve the pointer to the actual blob file
            blob_path = (file_path.parent / content).resolve()
            
            if blob_path.exists() and blob_path.stat().st_size > 0:
                blob_size = blob_path.stat().st_size
                print(f"  COPYING: {file_path.relative_to(snapshot_dir)}")
                print(f"           -> {blob_size:,} bytes from blob")
                shutil.copy2(blob_path, file_path)
            else:
                print(f"  ERROR: Blob not found for {file_path.relative_to(snapshot_dir)}")
        else:
            print(f"  OK: {file_path.relative_to(snapshot_dir)} ({size:,} bytes)")

def main():
    snapshots_dir = CACHE_DIR / "snapshots"
    for snapshot in snapshots_dir.iterdir():
        if snapshot.is_dir():
            fix_snapshot(snapshot)
    print("\n✅ Cache repair complete!")
    print("Now run: python indexer/vector_store.py --corpus data/processed/corpus.json")

if __name__ == "__main__":
    main()
