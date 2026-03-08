# Reproducing Results: **Bulk Deconvolution** on `BULK_Flu_sdy67`

This document describes how to reproduce the **bulk deconvolution** results on **SDY67 bulk** (with flow-cytometry ground-truth proportions) using our **Docker image**.

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
    - `model/` (pretrained checkpoints for reproduction)
    - `result_data/` (reference results for validation)
  - `PBMC_30K/`
    - `input/`
      - `PBMC_30K_seven_cell_type.h5ad` (single-cell reference)
      - `SDY67_bulk_with_gt.h5ad` (bulk with ground truth)
    - `model/` (pretrained checkpoints for reproduction)
    - `result_data/` (reference results for validation)

---

## 2) Choose your input and output folders (host-side)

Define:

- `CASE_DIR`: where you placed `BULK_Flu_sdy67/`
- `OUTPUT_DIR`: a writable folder to store outputs

```bash
CASE_DIR="/path/to/BULK_Flu_sdy67"
OUTPUT_DIR="/path/to/your/output_folder"
mkdir -p "${OUTPUT_DIR}"
```

## 3) Reproduce with GSE132044 as reference
### 3.1 Set variables
```bash
REF_NAME="GSE132044"

DATASET_DIR="${CASE_DIR}/${REF_NAME}"
DATASET_OUT="${OUTPUT_DIR}/${REF_NAME}"
mkdir -p "${DATASET_OUT}"
```
### 3.2 Copy pretrained checkpoints (required)
```bash
cp -r "${DATASET_DIR}/model" "${DATASET_OUT}/model"
```
Even with a fixed random seed, strict reproduction may be affected by:
### 3.3 Run Docker
```bash
docker run --rm -it \
  -e PYTHONUNBUFFERED=1 \
  -e HOST_UID="$(id -u)" \
  -e HOST_GID="$(id -g)" \
  -v "${DATASET_DIR}/input":/inputs:ro \
  -v "${DATASET_OUT}":/outputs \
  kristawang/cytobulk:1.0.0 \
  bulk_deconv \
  --sc "/inputs/GSE132044.h5ad" \
  --bulk "/inputs/SDY67_bulk_with_gt.h5ad" \
  --annotation_key "CellType" \
  --out_dir "/outputs/" \
  --dataset_name "SDY67" \
  --n_cell 500 \
  --seed 64 \
  --reproduce True
```
Outputs will be written under:
```bash
${OUTPUT_DIR}/GSE132044/
```

## 4) Reproduce with PBMC_30K as reference
### 4.1 Set variables
```bash
REF_NAME="PBMC_30K"

DATASET_DIR="${CASE_DIR}/${REF_NAME}"
DATASET_OUT="${OUTPUT_DIR}/${REF_NAME}"
mkdir -p "${DATASET_OUT}"
```
### 4.2 Copy pretrained checkpoints (required)
```bash
cp -r "${DATASET_DIR}/model" "${DATASET_OUT}/model"
```
Even with a fixed random seed, strict reproduction may be affected by:
### 4.3 Run Docker
```bash
docker run --rm -it \
  -e PYTHONUNBUFFERED=1 \
  -e HOST_UID="$(id -u)" \
  -e HOST_GID="$(id -g)" \
  -v "${DATASET_DIR}/input":/inputs:ro \
  -v "${DATASET_OUT}":/outputs \
  kristawang/cytobulk:1.0.0 \
  bulk_deconv \
  --sc "/inputs/PBMC_30K_seven_cell_type.h5ad" \
  --bulk "/inputs/SDY67_bulk_with_gt.h5ad" \
  --annotation_key "cell_type" \
  --out_dir "/outputs/" \
  --dataset_name "SDY67" \
  --n_cell 500 \
  --seed 64 \
  --reproduce
```
Outputs will be written under:
```bash
${OUTPUT_DIR}/PBMC_30K/
```

