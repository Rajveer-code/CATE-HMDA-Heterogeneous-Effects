"""Repack the docx_unpacked directory back into CATE_HMDA_Revised.docx"""
import zipfile, shutil, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

unpacked = Path('D:/Projects/CATE-HMDA-Heterogeneous-Effects/manuscript/docx_unpacked')
out_docx  = Path('D:/Projects/CATE-HMDA-Heterogeneous-Effects/manuscript/CATE_HMDA_Revised.docx')

# Backup original
backup = out_docx.with_suffix('.docx.bak')
if out_docx.exists() and not backup.exists():
    shutil.copy2(out_docx, backup)
    print(f"Backed up original to: {backup.name}")

with zipfile.ZipFile(out_docx, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for fpath in sorted(unpacked.rglob('*')):
        if fpath.is_file():
            arcname = fpath.relative_to(unpacked).as_posix()
            zf.write(fpath, arcname)

size_kb = out_docx.stat().st_size // 1024
print(f"Repacked: {out_docx.name} ({size_kb} KB)")

# Quick sanity check: open the zip and verify document.xml exists
with zipfile.ZipFile(out_docx, 'r') as zf:
    names = zf.namelist()
    print(f"Files in DOCX: {len(names)}")
    assert 'word/document.xml' in names, "word/document.xml not found!"
    doc_size = zf.getinfo('word/document.xml').file_size
    print(f"word/document.xml: {doc_size:,} bytes")
    print("Sanity check PASSED")
