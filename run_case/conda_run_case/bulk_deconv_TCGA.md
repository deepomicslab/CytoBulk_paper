# Reproducing Results: **Bulk Deconvolution** on `BULK_TCGA` — Conda Version

This document describes how to reproduce the **bulk deconvolution** results for **TCGA bulk RNA** using a **Conda environment**.

The input package `BULK_TCGA/` contains **three TCGA tasks** (each task = one bulk cohort + one single-cell reference):

- `TCGA_HNSC`
- `TCGA_LIHC`
- `TCGA_SKCM`

---

## 1) Download the `BULK_TCGA` package

Download the folder **`BULK_TCGA/`** from **`XXXX`**.

It contains three subfolders (tasks):

- `TCGA_HNSC/`
  - `input/`
    - single-cell reference (`sc`, `.h5ad`): `HNSC_GSE103322_adata.h5ad`
    - bulk data (`bulk`, `.h5ad`): `TCGA_HNSC_adata.h5ad`
  - `model/`  
    **Pretrained model checkpoints** for reproduction.
  - `result_data/`  
    Reference results provided for comparison/validation.

- `TCGA_LIHC/`
  - `input/`
    - single-cell reference (`sc`, `.h5ad`): `GSE125449.h5ad`
    - bulk data (`bulk`, `.h5ad`): `RNA_TCGA_LIHC.h5ad`
  - `model/`
  - `result_data/`

- `TCGA_SKCM/`
  - `input/`
    - single-cell reference (`sc`, `.h5ad`): `GSE115978.h5ad`
    - bulk data (`bulk`, `.h5ad`): `RNA_TCGA_SKCM.h5ad`
  - `model/`
  - `result_data/`

> Note: dataset names in this tutorial **must match** the folder names above:  
> `TCGA_HNSC`, `TCGA_LIHC`, `TCGA_SKCM`.

---

## 2) Notes on reproducibility

Even with a fixed random seed, strict reproduction may be affected by:

1. **Platform-dependent numerical variation**  
   Parts of the pipeline rely on matrix factorization and low-level linear algebra routines. Numerical results can differ slightly across hosts due to differences in BLAS/LAPACK backends (e.g., MKL vs OpenBLAS), CPU vectorization, thread scheduling, and floating-point non-associativity. These small differences can propagate downstream and lead to measurable output deviations.

2. **Feature selection / tie-breaking differences**  
   Some internal steps may involve selecting top features. Ties or near-ties can be resolved differently across environments or library versions, contributing to small output differences.

### Recommendation for strict reproduction

To reproduce our reported results as closely as possible:

- **Reuse the provided pretrained checkpoints**: copy each task’s `model/` into your chosen output directory (the folder you pass to `--out_dir`).

> The Docker CLI uses `--reproduce` to force loading checkpoints from `out_dir/model/`.  
> In the Conda script (`bulk_deconv_TCGA.py`), reproduction is achieved by **copying `model/` into `out_dir/`** so the run can pick up the same pretrained checkpoints (as intended for this package).

---

## 3) Choose your input and output folders

You only need to define:

- `PKG_DIR`: where you placed `BULK_TCGA/`
- `OUTPUT_DIR`: a writable folder where outputs will be saved

Example (replace with your own paths):

```bash
PKG_DIR="/path/to/BULK_TCGA"
OUTPUT_DIR="/path/to/your/output_folder"
mkdir -p "${OUTPUT_DIR}"
```

## 4) Example: reproduce one TCGA task (e.g., TCGA_LIHC)
### 4.1 Set variables
```bash
DATASET_NAME="TCGA_LIHC"

DATASET_DIR="${PKG_DIR}/${DATASET_NAME}"
DATASET_OUT="${OUTPUT_DIR}/${DATASET_NAME}"

mkdir -p "${DATASET_OUT}"
```
### 4.2 Copy pretrained checkpoints (required)
```bash
cp -r "${DATASET_DIR}/model" "${DATASET_OUT}/model"
```
### 4.3 Run the reproduction script
```bash
python bulk_deconv_TCGA.py \
  --sc_adata "${DATASET_DIR}/input/GSE125449.h5ad" \
  --bulk_adata "${DATASET_DIR}/input/RNA_TCGA_LIHC.h5ad" \
  --annotation_key "Type" \
  --out_dir "${DATASET_OUT}" \
  --dataset_name "${DATASET_NAME}" \
```
Outputs will be written under:
```bash
${OUTPUT_DIR}/TCGA_LIHC/
```
## 5) Run the other two tasks
### 5.1 TCGA_HNSC
```bash
DATASET_NAME="TCGA_HNSC"
DATASET_DIR="${PKG_DIR}/${DATASET_NAME}"
DATASET_OUT="${OUTPUT_DIR}/${DATASET_NAME}"
mkdir -p "${DATASET_OUT}"

cp -r "${DATASET_DIR}/model" "${DATASET_OUT}/model"

python bulk_deconv_TCGA.py \
  --sc_adata "${DATASET_DIR}/input/HNSC_GSE103322_adata.h5ad" \
  --bulk_adata "${DATASET_DIR}/input/TCGA_HNSC_adata.h5ad" \
  --annotation_key "Celltype (original)" \
  --out_dir "${DATASET_OUT}" \
  --dataset_name "${DATASET_NAME}" \
```

Outputs will be written under:
```bash
${OUTPUT_DIR}/TCGA_HNSC/
```
### 5.2 TCGA_SKCM

```bash
DATASET_NAME="TCGA_SKCM"
DATASET_DIR="${PKG_DIR}/${DATASET_NAME}"
DATASET_OUT="${OUTPUT_DIR}/${DATASET_NAME}"
mkdir -p "${DATASET_OUT}"

cp -r "${DATASET_DIR}/model" "${DATASET_OUT}/model"

python bulk_deconv_TCGA.py \
  --sc_adata "${DATASET_DIR}/input/GSE115978.h5ad" \
  --bulk_adata "${DATASET_DIR}/input/RNA_TCGA_SKCM.h5ad" \
  --annotation_key "cell_type" \
  --out_dir "${DATASET_OUT}" \
  --dataset_name "${DATASET_NAME}" \
```

Outputs will be written under:
```bash
${OUTPUT_DIR}/TCGA_SKCM/
```