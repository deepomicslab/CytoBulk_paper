# Reproducing Results: **Bulk Deconvolution** on `BULK_Flu_sdy67` — Conda Version

This document describes how to reproduce the **bulk deconvolution** results on **SDY67 bulk** (with flow-cytometry ground-truth proportions) using a **Conda environment**.

We provide **two alternative single-cell references** for the same bulk dataset:

- `GSE132044` (reference 1)
- `PBMC_30K` (reference 2)

Both references deconvolve the same bulk file: `SDY67_bulk_with_gt.h5ad`.

---

## 1) Download the `BULK_Flu_sdy67` package

Download the folder **`BULK_Flu_sdy67/`** from **`XXXX`**.

Folder structure:

- `BULK_Flu_sdy67/`
  - `GSE132044/`
    - `input/`
      - `GSE132044.h5ad` (single-cell reference)
      - `SDY67_bulk_with_gt.h5ad` (bulk with ground truth)
    - `model/` (pretrained checkpoints for reproducibility)
    - `result_data/` (reference results for validation)
  - `PBMC_30K/`
    - `input/`
      - `PBMC_30K_seven_cell_type.h5ad` (single-cell reference)
      - `SDY67_bulk_with_gt.h5ad` (bulk with ground truth)
    - `model/` (pretrained checkpoints for reproducibility)
    - `result_data/` (reference results for validation)

### Input naming convention (important)

For each reference folder `${REF_NAME}`:

- Single-cell reference (sc, `.h5ad`)
  - `BULK_Flu_sdy67/${REF_NAME}/input/<reference_file>.h5ad`
  - `GSE132044` uses: `GSE132044.h5ad`
  - `PBMC_30K` uses: `PBMC_30K_seven_cell_type.h5ad`

- Bulk data (bulk, `.h5ad`)
  - `BULK_Flu_sdy67/${REF_NAME}/input/SDY67_bulk_with_gt.h5ad`

---

## 2) Notes on reproducibility

Even with a fixed random seed, strict reproduction may be affected by:

1. **Platform-dependent numerical variation**  
   Parts of the pipeline rely on matrix factorization and low-level linear algebra routines. Numerical results can differ slightly across hosts due to differences in BLAS/LAPACK backends (e.g., MKL vs OpenBLAS), CPU vectorization, thread scheduling, and floating-point non-associativity.

2. **Feature selection / tie-breaking differences**  
   Some internal steps may involve selecting top features. Ties or near-ties can be resolved differently across environments or library versions, contributing to small output differences.
---

## 3) Choose your case folder and output folder

Define:

- `CASE_DIR`: where you placed `BULK_Flu_sdy67/`
- `OUTPUT_DIR`: a writable folder where outputs will be saved

Example:

```bash
CASE_DIR="/path/to/BULK_Flu_sdy67"
OUTPUT_DIR="/path/to/your/output_folder"
mkdir -p "${OUTPUT_DIR}"
```

## 4) Reproduce with GSE132044 as reference
### 4.1 Set variables
```bash
REF_NAME="GSE132044"

DATASET_DIR="${CASE_DIR}/${REF_NAME}"
DATASET_OUT="${OUTPUT_DIR}/${REF_NAME}"
mkdir -p "${DATASET_OUT}"
```
### 4.2 Copy pretrained checkpoints (required)
```bash
cp -r "${DATASET_DIR}/model" "${DATASET_OUT}/model"
```
### 4.3 Run the reproduction script
```bash
python bulk_deconv_Flu_sdy67.py \
  --sc_adata "${DATASET_DIR}/input/GSE132044.h5ad" \
  --bulk_adata "${DATASET_DIR}/input/SDY67_bulk_with_gt.h5ad" \
  --annotation_key "CellType" \
  --out_dir "${DATASET_OUT}" \
  --dataset_name "SDY67" 
```
Outputs will be written under:
```bash
${OUTPUT_DIR}/GSE132044/
```
## 5) Reproduce with PBMC_30K as reference
### 5.1 Set variables
```bash
REF_NAME="PBMC_30K"

DATASET_DIR="${CASE_DIR}/${REF_NAME}"
DATASET_OUT="${OUTPUT_DIR}/${REF_NAME}"

mkdir -p "${DATASET_OUT}"
```
### 5.2 Copy pretrained checkpoints (required)
```bash
cp -r "${DATASET_DIR}/model" "${DATASET_OUT}/model"
```
### 5.3 Run the reproduction script
```bash
python bulk_deconv_Flu_sdy67.py \
  --sc_adata "${DATASET_DIR}/input/PBMC_30K_seven_cell_type.h5ad" \
  --bulk_adata "${DATASET_DIR}/input/SDY67_bulk_with_gt.h5ad" \
  --annotation_key "cell_type" \
  --out_dir "${DATASET_OUT}" \
  --dataset_name "SDY67" 
```
Outputs will be written under:
```bash
${OUTPUT_DIR}/PBMC_30K/
```