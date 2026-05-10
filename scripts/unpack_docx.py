"""Unpack DOCX to a working directory for XML editing"""
import zipfile, shutil, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

src  = Path('D:/Projects/CATE-HMDA-Heterogeneous-Effects/manuscript/CATE_HMDA_Revised.docx')
dest = Path('D:/Projects/CATE-HMDA-Heterogeneous-Effects/manuscript/docx_unpacked')

if dest.exists():
    shutil.rmtree(dest)
dest.mkdir(parents=True)

with zipfile.ZipFile(src, 'r') as z:
    z.extractall(dest)

files = sorted(dest.rglob('*'))
print(f"Unpacked {len(files)} files to {dest}")
for f in files:
    if f.is_file():
        print(f"  {f.relative_to(dest)}")
