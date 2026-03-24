# Reproducing Results: Bulk Deconvolution on HGSOC — Conda Version

This document describes how to reproduce the **bulk deconvolution** results for **HGSOC** bulk RNA using a **Conda environment**.

---

## 1) Download the `BULK_HGSOC` package

Download the folder **`BULK_HGSOC/`** from [https://doi.org/10.5281/zenodo.18495002](https://doi.org/10.5281/zenodo.18495002).

Folder structure (as provided):

- `BULK_HGSOC/`
  - `input/`
    - `GSM6720925.h5ad` *(single-cell reference)*
    - `simulated_bulk_adata.h5ad` *(bulk / simulated bulk)*
  - `model/` *(pretrained checkpoints for reproduction)*
  - `result_data/` *(reference results for validation)*

> Note: this tutorial assumes `input/`, `model/`, and `result_data/` are directly under `BULK_HGSOC/`.

---

## 2) Choose your input and output folders

You only need to define:

- `CASE_DIR`: where you placed `BULK_HGSOC/`
- `OUTPUT_DIR`: a writable folder to store outputs

Example (replace with your own paths):

```bash
CASE_DIR="/path/to/BULK_HGSOC"
OUTPUT_DIR="/path/to/your/output_folder"
mkdir -p "${OUTPUT_DIR}"
```

---

## 3) Run the reproduction script (Conda)

### 3.1 Copy pretrained checkpoints (required for strict reproduction)

Before running the script, copy the pretrained model into your output directory:

```bash
DATASET_NAME="HGSOC"
DATASET_OUT="${OUTPUT_DIR}/${DATASET_NAME}"
mkdir -p "${DATASET_OUT}"

cp -r "${CASE_DIR}/model" "${DATASET_OUT}/model"
```

### 3.2 Run the deconvolution

```bash
python bulk_deconv_HGSOC.py \
  --sc_adata "${CASE_DIR}/input/GSM6720925.h5ad" \
  --bulk_adata "${CASE_DIR}/input/simulated_bulk_adata.h5ad" \
  --out_dir "${DATASET_OUT}" \
  --dataset_name "HGSOC"
```

Outputs will be written to:
```bash
${OUTPUT_DIR}/HGSOC/
```

---

## 4) Parameter explanations

Below are the parameters used in the reproduction command and what they mean.

### Input parameters

- `--sc_adata <path>`  
  Path to the single-cell reference `.h5ad` file.  
  In HGSOC: `GSM6720925.h5ad`.

- `--bulk_adata <path>`  
  Path to the bulk dataset `.h5ad` file (or simulated bulk).  
  In HGSOC: `simulated_bulk_adata.h5ad`.

- `--out_dir <path>`  
  Output folder where deconvolution results will be saved.

- `--dataset_name <str>`  
  A name used for organizing/logging outputs.

### Hardcoded parameters (fixed in script)

The following parameters are set within the script and cannot be changed via command line:

- `annotation_key`: `"cellType"`  
  Column name in `sc_adata.obs` that stores cell-type labels.

- `n_cell`: `100`  
  Number of cells used when simulating pseudo-bulk mixtures during training.

- `seed`: `64`  
  Random seed for reproducibility.

- `use_adversarial`: `True`  
  Enable adversarial training.

- `specificity`: `True`  
  Enable cell-type specificity constraints.

- `giotto_gene_num`: `150`  
  Number of genes used for marker detection.

- `downsampling`: `False`  
  Do not downsample single-cell data.

---

