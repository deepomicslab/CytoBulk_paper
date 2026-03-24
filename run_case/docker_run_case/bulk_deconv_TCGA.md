# Reproducing Results: **Bulk Deconvolution** on `BULK_TCGA`

This document describes how to reproduce the **bulk deconvolution** results for **TCGA bulk RNA** using our **Docker image**.

The input package `BULK_TCGA/` contains **three TCGA tasks** (each task = one bulk cohort + one single-cell reference):

- `TCGA_HNSC`
- `TCGA_LIHC`
- `TCGA_SKCM`

---

## 1) Download the `BULK_TCGA` package

Download the folder **`BULK_TCGA/`** from [https://doi.org/10.5281/zenodo.18495002](https://doi.org/10.5281/zenodo.18495002).

Folder structure (as provided):

- `BULK_TCGA/`
  - `TCGA_HNSC/`
    - `input/`
      - `HNSC_GSE103322_adata.h5ad` (single-cell reference)
      - `TCGA_HNSC_adata.h5ad` (bulk)
    - `model/` (pretrained checkpoints for reproduction)
    - `result_data/` (reference results for validation)
  - `TCGA_LIHC/`
    - `input/`
      - `GSE125449.h5ad` (single-cell reference)
      - `RNA_TCGA_LIHC.h5ad` (bulk)
    - `model/`
    - `result_data/`
  - `TCGA_SKCM/`
    - `input/`
      - `GSE115978.h5ad` (single-cell reference)
      - `RNA_TCGA_SKCM.h5ad` (bulk)
    - `model/`
    - `result_data/`

> Note: dataset names in this tutorial **must match** the folder names above:
`TCGA_HNSC`, `TCGA_LIHC`, `TCGA_SKCM`.

---

## 2) Choose your input and output folders (host-side)

Define:

- `CASE_DIR`: where you placed `BULK_TCGA/`
- `OUTPUT_DIR`: a writable folder to store outputs

```bash
CASE_DIR="/path/to/BULK_TCGA"
OUTPUT_DIR="/path/to/your/output_folder"
mkdir -p "${OUTPUT_DIR}"
```

## 3) Reproduce: TCGA_LIHC
### 3.1 Set variables
```bash
DATASET_NAME="TCGA_LIHC"

DATASET_DIR="${CASE_DIR}/${DATASET_NAME}"
DATASET_OUT="${OUTPUT_DIR}/${DATASET_NAME}"
mkdir -p "${DATASET_OUT}"
```

### 3.2 Copy pretrained checkpoints (required)
```bash
cp -r "${DATASET_DIR}/model" "${DATASET_OUT}/model"
```

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
  --sc "/inputs/GSE125449.h5ad" \
  --bulk "/inputs/RNA_TCGA_LIHC.h5ad" \
  --annotation_key "Type" \
  --out_dir "/outputs/" \
  --dataset_name "TCGA_LIHC" \
  --n_cell 500 \
  --high_purity True \
  --seed 64 \
  --reproduce True
```

Outputs will be written under:
```bash
${OUTPUT_DIR}/TCGA_LIHC/
```

## 4) Reproduce: TCGA_HNSC
### 4.1 Set variables
```bash
DATASET_NAME="TCGA_HNSC"

DATASET_DIR="${CASE_DIR}/${DATASET_NAME}"
DATASET_OUT="${OUTPUT_DIR}/${DATASET_NAME}"
mkdir -p "${DATASET_OUT}"
```
### 4.2 Copy pretrained checkpoints (required)
```bash
cp -r "${DATASET_DIR}/model" "${DATASET_OUT}/model"
```

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
  --sc "/inputs/HNSC_GSE103322_adata.h5ad" \
  --bulk "/inputs/TCGA_HNSC_adata.h5ad" \
  --annotation_key "Celltype (original)" \
  --out_dir "/outputs/" \
  --dataset_name "TCGA_HNSC" \
  --n_cell 500 \
  --high_purity True \
  --seed 64 \
  --reproduce
```

Outputs will be written under:
```bash
${OUTPUT_DIR}/TCGA_HNSC/
```



## 5) Reproduce: TCGA_SKCM
### 5.1 Set variables
```bash
DATASET_NAME="TCGA_SKCM"

DATASET_DIR="${CASE_DIR}/${DATASET_NAME}"
DATASET_OUT="${OUTPUT_DIR}/${DATASET_NAME}"
mkdir -p "${DATASET_OUT}"
```
### 5.2 Copy pretrained checkpoints (required)
```bash
cp -r "${DATASET_DIR}/model" "${DATASET_OUT}/model"
```

### 5.3 Run Docker
```bash
docker run --rm -it \
  -e PYTHONUNBUFFERED=1 \
  -e HOST_UID="$(id -u)" \
  -e HOST_GID="$(id -g)" \
  -v "${DATASET_DIR}/input":/inputs:ro \
  -v "${DATASET_OUT}":/outputs \
  kristawang/cytobulk:1.0.0 \
  bulk_deconv \
  --sc "/inputs/GSE115978.h5ad" \
  --bulk "/inputs/RNA_TCGA_SKCM.h5ad" \
  --annotation_key "cell_type" \
  --out_dir "/outputs/" \
  --dataset_name "TCGA_SKCM" \
  --n_cell 500 \
  --high_purity True \
  --seed 64 \
  --reproduce
```

Outputs will be written under:
```bash
${OUTPUT_DIR}/TCGA_SKCM/
```

## 6) Parameter explanations (`bulk_deconv`)

Below are the parameters used in the TCGA reproduction commands and what they mean.

- `--sc <path>`  
  Single-cell reference `.h5ad` file (inside container).

- `--bulk <path>`  
  Bulk dataset `.h5ad` file (inside container).

- `--annotation_key <str>`  
  Column name in `sc_adata.obs` that stores the cell-type labels.  
  Examples in this package:
  - `Type` (LIHC)
  - `Celltype (original)` (HNSC)
  - `cell_type` (SKCM)

- `--out_dir <path>`  
  Output folder (inside container). In this tutorial always use `"/outputs/"`.

- `--dataset_name <str>`  
  A name used for organizing/logging outputs. Must match the dataset name you are reproducing:  
  `TCGA_LIHC`, `TCGA_HNSC`, `TCGA_SKCM`


- `--seed <int>`  
  Random seed used for data simulation and training control. We use `64` as in the scripts.

- `--reproduce`  
  Load pretrained checkpoints from `out_dir/model/` and run in reproduction mode.  
  This is why you must copy `model/` into the output directory before running.


- `--n_cell <int>`  
  Number of cells used when simulating pseudo-bulk mixtures during training.  
  Here: `500`.

- `--high_purity <True|False>`  
  Whether to use the `high_purity` strategy when simulating training mixtures.  
  `high_purity=True` means we simulate data with a high-purity strategy.  
  For TCGA bulk data, we recommend setting this to `True`.


---
