#!/usr/bin/env python3
"""
scripts/fetch_ias_data.py

Fetches and verifies the authentic Intermittent Androgen Suppression (IAS)
clinical benchmark dataset from Bruchovsky 2006 / Tanaka 2010.

Dataset Sources:
  - Bruchovsky et al., Cancer 2006; 107:389-395
  - Tanaka et al., Phil. Trans. R. Soc. A 2010; 368:5029-5044
  - URL: http://www.nicholasbruchovsky.com/dataTanaka.zip
  - Expected SHA-256: 845683954e99253ddf68e488a48223e89c19247a92aec27daa79130d8f46904f
  - 90 Patients total (72 Bruchovsky et al. + 18 Shaw et al.)

Destination:
  data/ias_bruchovsky/
    ├── Bruchovsky_et_al/ (72 txt files)
    └── Shaw_et_al/       (18 txt files)
"""

import argparse
import hashlib
import io
import os
import sys
import urllib.request
import zipfile
from pathlib import Path

DATA_URL = "http://www.nicholasbruchovsky.com/dataTanaka.zip"
EXPECTED_SHA256 = "845683954e99253ddf68e488a48223e89c19247a92aec27daa79130d8f46904f"
EXPECTED_BRUCHOVSKY_PATIENTS = 72
EXPECTED_SHAW_PATIENTS = 18


def get_default_target_dir() -> Path:
    repo_root = Path(__file__).resolve().parent.parent
    return repo_root / "data" / "ias_bruchovsky"


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_extracted_data(target_dir: Path) -> tuple[bool, str]:
    bruchovsky_dir = target_dir / "Bruchovsky_et_al"
    shaw_dir = target_dir / "Shaw_et_al"

    if not bruchovsky_dir.is_dir() or not shaw_dir.is_dir():
        return False, f"Missing directories in {target_dir}"

    bruchovsky_files = list(bruchovsky_dir.glob("*.txt"))
    shaw_files = list(shaw_dir.glob("*.txt"))

    if len(bruchovsky_files) != EXPECTED_BRUCHOVSKY_PATIENTS:
        return False, (
            f"Expected {EXPECTED_BRUCHOVSKY_PATIENTS} Bruchovsky files, "
            f"found {len(bruchovsky_files)}"
        )
    if len(shaw_files) != EXPECTED_SHAW_PATIENTS:
        return False, (
            f"Expected {EXPECTED_SHAW_PATIENTS} Shaw files, "
            f"found {len(shaw_files)}"
        )

    return True, f"Verified {len(bruchovsky_files)} Bruchovsky + {len(shaw_files)} Shaw patient files."


def fetch_and_extract(target_dir: Path, force: bool = False) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)

    if not force:
        is_valid, msg = verify_extracted_data(target_dir)
        if is_valid:
            print(f"[OK] Dataset already present and verified: {msg}")
            return

    print(f"Downloading IAS clinical benchmark dataset from: {DATA_URL}")
    req = urllib.request.Request(
        DATA_URL,
        headers={"User-Agent": "PERSEPHONE-Research/1.0 (Clinical Oncology Benchmark)"}
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        zip_bytes = resp.read()

    actual_hash = compute_sha256(zip_bytes)
    print(f"Downloaded {len(zip_bytes)} bytes. SHA-256: {actual_hash}")

    if actual_hash != EXPECTED_SHA256:
        raise ValueError(
            f"SHA-256 checksum mismatch!\n"
            f"  Expected: {EXPECTED_SHA256}\n"
            f"  Actual:   {actual_hash}"
        )

    print("Checksum verified successfully. Extracting archive...")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for member in zf.infolist():
            # Strips top-level 'dataTanaka/' prefix if present
            parts = Path(member.filename).parts
            if not parts:
                continue
            if parts[0].lower() == "datatanaka":
                rel_parts = parts[1:]
            else:
                rel_parts = parts

            if not rel_parts:
                continue

            dest_path = target_dir.joinpath(*rel_parts)
            if member.is_dir():
                dest_path.mkdir(parents=True, exist_ok=True)
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src_file, open(dest_path, "wb") as dst_file:
                    dst_file.write(src_file.read())

    is_valid, msg = verify_extracted_data(target_dir)
    if not is_valid:
        raise RuntimeError(f"Post-extraction verification failed: {msg}")

    print(f"[SUCCESS] {msg}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch and verify Bruchovsky IAS benchmark data.")
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=get_default_target_dir(),
        help="Destination directory (default: data/ias_bruchovsky)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download and re-extraction even if present",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing data without downloading",
    )

    args = parser.parse_args()

    if args.verify_only:
        is_valid, msg = verify_extracted_data(args.target_dir)
        print(f"Verification: {msg}")
        return 0 if is_valid else 1

    try:
        fetch_and_extract(args.target_dir, force=args.force)
        return 0
    except Exception as e:
        print(f"[ERROR] Failed to fetch or verify dataset: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
