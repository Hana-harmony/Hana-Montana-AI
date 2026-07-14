#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOURCE_DIR="$ROOT/docs/paper/acl"
BUILD_DIR="$ROOT/tmp/pdfs/k-fnspid-v3-arr"
OUTPUT_DIR="$ROOT/output/pdf"
STYLE_COMMIT="d5adc823ff0f80f98c80405ca0ab66c68e684409"
STYLE_BASE="https://raw.githubusercontent.com/acl-org/acl-style-files/${STYLE_COMMIT}"
export SOURCE_DATE_EPOCH="1784041200"
export FORCE_SOURCE_DATE=1

mkdir -p "$BUILD_DIR" "$OUTPUT_DIR"
python3 "$ROOT/scripts/paper/verify_k_fnspid_submission.py"

# 공식 스타일을 고정 커밋에서 받아 임의 수정 가능성을 차단한다.
curl --fail --silent --show-error --location "$STYLE_BASE/acl.sty" --output "$BUILD_DIR/acl.sty"
curl --fail --silent --show-error --location "$STYLE_BASE/acl_natbib.bst" --output "$BUILD_DIR/acl_natbib.bst"
install -m 0644 "$SOURCE_DIR/k-fnspid-v3-arr-review.tex" "$BUILD_DIR/k-fnspid-v3-arr-review.tex"
install -m 0644 "$SOURCE_DIR/references.bib" "$BUILD_DIR/references.bib"

(
  cd "$BUILD_DIR"
  tectonic --keep-logs --keep-intermediates k-fnspid-v3-arr-review.tex
)

install -m 0644 "$BUILD_DIR/k-fnspid-v3-arr-review.pdf" "$OUTPUT_DIR/k-fnspid-v3-arr-review.pdf"
pdfinfo "$OUTPUT_DIR/k-fnspid-v3-arr-review.pdf"
