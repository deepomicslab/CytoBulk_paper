# Reproducing Results: **Bulk Deconvolution** on `BULK_HGSOC`

This document describes how to reproduce the **bulk deconvolution** results for **HGSOC** bulk RNA using our **Docker image**.

The input package `BULK_HGSOC/` contains **one HGSOC task** (one bulk cohort + one single-cell reference):

- `HGSOC`

---

## 1) Download the `BULK_HGSOC` package

Download the folder **`BULK_HGSOC/`** from [https://doi.org/10.5281/zenodo.18495002](https://doi.org/10.5281/zenodo.18495002).

Folder structure (as provided):

- `BULK_HGSOC/`
  - `input/`
    - `GSM6720925.h5ad` (single-cell reference)
    - `simulated_bulk_adata.h5ad` (bulk / simulated bulk)
  - `model/` (pretrained checkpoints and batch effect result for reproduction)
  - `result_data/` (reference results for validation)

> Note: this tutorial assumes `input/`, `model/`, and `result_data/` are directly under `BULK_HGSOC/`.

---

## 2) Choose your input and output folders (host-side)

Define:

- `CASE_DIR`: where you placed `BULK_HGSOC/`
- `OUTPUT_DIR`: a writable folder to store outputs

```bash
CASE_DIR="/path/to/BULK_HGSOC"
OUTPUT_DIR="/path/to/your/output_folder"
mkdir -p "${OUTPUT_DIR}"
```

Set dataset variables:
### 3.1 Set variables
```bash
DATASET_NAME="HGSOC"

DATASET_DIR="${CASE_DIR}"
DATASET_OUT="${OUTPUT_DIR}/${DATASET_NAME}"
mkdir -p "${DATASET_OUT}"
```

## 3) Reproduce: HGSOC

### 3.1 Copy pretrained checkpoints (required)
```bash
cp -r "${DATASET_DIR}/model" "${DATASET_OUT}/model"
```

### 3.2 Run Docker
```bash
docker run --rm -it \
  -e PYTHONUNBUFFERED=1 \
  -e HOST_UID="$(id -u)" \
  -e HOST_GID="$(id -g)" \
  -v "${DATASET_DIR}/input":/inputs:ro \
  -v "${DATASET_OUT}":/outputs \
  kristawang/cytobulk:1.0.0 \
  bulk_deconv \
  --sc "/inputs/GSM6720925.h5ad" \
  --bulk "/inputs/simulated_bulk_adata.h5ad" \
  --annotation_key "cellType" \
  --out_dir "/outputs/" \
  --dataset_name "HGSOC" \
  --n_cell 100 \
  --seed 64 \
  --reproduce True
```

Outputs will be written under:
```bash
${OUTPUT_DIR}/HGSOC/
```

## 4) Parameter explanations 

Below are the parameters used in the TCGA reproduction commands and what they mean.


- `--sc <path>`  
  Single-cell reference `.h5ad` file (inside container).

- `--bulk <path>`  
  Bulk dataset `.h5ad` file (inside container).

- `--annotation_key <str>`  
  Column name in `sc_adata.obs` that stores the cell-type labels.  


- `--out_dir <path>`  
  Output folder (inside container). In this tutorial always use `"/outputs/"`.

- `--dataset_name <str>`  
  A name used for organizing/logging outputs. 

### Reproduction / randomness

- `--seed <int>`  
  Random seed used for data simulation and training control. We use `64` as in the scripts.

- `--reproduce`  
  Load pretrained checkpoints from `out_dir/model/` and run in reproduction mode.  
  This is why you must copy `model/` into the output directory before running.


- `--n_cell <int>`  
  Number of cells used when simulating pseudo-bulk mixtures during training.  
  Here: `100`.


---
