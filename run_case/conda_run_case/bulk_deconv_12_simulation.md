# Reproducing Results: Bulk Deconvolution on `12 BULK_simulation` Datasets — Conda Version

This document describes how to reproduce the **bulk deconvolution** results for the **12 simulation datasets** in `BULK_simulation/` using a **Conda environment**.

---

## 1) Download the `BULK_simulation` package

Download the folder **`BULK_simulation/`** from **`XXXX`**.

It contains **12 datasets**:

- `BRCA_GSE114727`
- `CLL_GSE111014`
- `CRC_GSE139555`
- `HNSC_GSE103322`
- `LIHC_GSE140228`
- `LSCC_GSE150321`
- `NSCLC_GSE127471`
- `OV_GSE154600`
- `PAAD_GSE111672`
- `PBMC_30K`
- `SKCM_GSE123139`

> Note: the Docker reference list contained `CLL_GSE111014` twice; it should appear only once.

Each dataset folder contains:

- `input/`
  - single-cell reference (`sc`, `.h5ad`): `${DATASET_NAME}.h5ad`
  - bulk data (`bulk`, `.h5ad`): `${DATASET_NAME}_bulk.h5ad`

- `model/`
  - pretrained checkpoints for reproducibility:
    - `eigh_cache.pt`
    - `multi_graph_graphs.pkl`
    - `multi_graph_model.pt`

- `result_data/`
  - reference results provided for comparison/validation

### Input naming convention (important)

For dataset `${DATASET_NAME}` (example: `CLL_GSE111014`):

- `BULK_simulation/${DATASET_NAME}/input/${DATASET_NAME}.h5ad`
- `BULK_simulation/${DATASET_NAME}/input/${DATASET_NAME}_bulk.h5ad`

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

- `CASE_DIR`: where you placed `BULK_simulation/`
- `OUTPUT_DIR`: a writable folder where outputs will be saved

Example:

```bash
CASE_DIR="/path/to/BULK_simulation"
OUTPUT_DIR="/path/to/your/output_folder"
```

Create the output directory:
```bash
mkdir -p "${OUTPUT_DIR}"
```

## 4) Example: reproduce one dataset (e.g., CLL_GSE111014)
### 4.1 Set variables
```bash
DATASET_NAME="CLL_GSE111014"

DATASET_DIR="${CASE_DIR}/${DATASET_NAME}"
DATASET_OUT="${OUTPUT_DIR}/${DATASET_NAME}"

mkdir -p "${DATASET_OUT}"
```

To run another dataset, simply replace DATASET_NAME with the corresponding dataset folder name.

### 4.2 Copy pretrained checkpoints into OUT_DIR (required)
Copy the pretrained checkpoints into the output directory that you will pass to --out_dir:
```bash
cp -r "${DATASET_DIR}/model" "${DATASET_OUT}/model"
```

### 4.3 Run the reproduction script
```bash
python bulk_deconv_12_simulation.py \
  --sc_adata "${DATASET_DIR}/input/${DATASET_NAME}.h5ad" \
  --bulk_adata "${DATASET_DIR}/input/${DATASET_NAME}_bulk.h5ad" \
  --out_dir "${DATASET_OUT}" \
  --dataset_name "${DATASET_NAME}"
```

Outputs will be written under:
```bash
${OUTPUT_DIR}/${DATASET_NAME}/
```