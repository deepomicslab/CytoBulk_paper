# Reproducing Results: **Bulk Deconvolution** on `12 BULK_simulation datasets`

This document describes how to reproduce the **bulk deconvolution** results for datasets in `BULK_simulation/` using our **Docker image**.

---

## 1) Download the `BULK_simulation` package

Download the folder **`BULK_simulation/`** from [https://doi.org/10.5281/zenodo.18495002](https://doi.org/10.5281/zenodo.18495002).

It contains **12 datasets**:

- `BRCA_GSE114727`
- `CLL_GSE111014`
- `CRC_GSE139555`
- `CLL_GSE111014`
- `HNSC_GSE103322`
- `LIHC_GSE140228`
- `LSCC_GSE150321`
- `NSCLC_GSE127471`
- `OV_GSE154600`
- `PAAD_GSE111672`
- `PBMC_30K`
- `SKCM_GSE123139`

Each dataset folder contains:

- `input/`
  - single-cell reference (`sc`, `.h5ad`): `${DATASET_NAME}.h5ad`
  - bulk data (`bulk`, `.h5ad`): `${DATASET_NAME}_bulk.h5ad`

- `model/`
  - pretrained checkpoints (to ensure reproducibility), including:
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

### Recommendation for strict reproduction

To reproduce our reported results as closely as possible:

- **Reuse the provided pretrained checkpoints** (copy `model/` into your chosen output directory), and
- Run the pipeline with `--reproduce` (enables reproduce mode inside Cytobulk).

---

## 3) Choose your input and output folders (host-side)

Define two host directories:

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
To run another dataset, simply replace `DATASET_NAME` with the corresponding dataset folder name.
### 4.2 Copy pretrained checkpoints into OUTPUT_DIR (required)

Before running Docker, copy the pretrained checkpoints into the output directory you will use for --out_dir:
```bash
cp -r "${DATASET_DIR}/model" "${DATASET_OUT}/model"
```
This ensures the run loads the same pretrained checkpoints rather than producing environment-dependent parameters.

## 5) Run Docker to reproduce the results (bulk deconvolution)
```bash
docker run --rm -it \
  -e PYTHONUNBUFFERED=1 \
  -e HOST_UID="$(id -u)" \
  -e HOST_GID="$(id -g)" \
  -v "${DATASET_DIR}/input":/inputs:ro \
  -v "${DATASET_OUT}":/outputs \
  kristawang/cytobulk:1.0.0 \
  bulk_deconv \
  --sc "/inputs/${DATASET_NAME}.h5ad" \
  --bulk "/inputs/${DATASET_NAME}_bulk.h5ad" \
  --annotation_key "Celltype_minor" \
  --out_dir "/outputs/" \
  --dataset_name "${DATASET_NAME}" \
  --n_cell 100 \
  --seed 64 \
  --specificity False \
  --reproduce True
```

Outputs will be written under:
```bash
${OUTPUT_DIR}/${DATASET_NAME}/
```

## 6) `bulk_deconv` arguments

- `--sc <path>`  
  Path (inside the container) to the single-cell reference `.h5ad` file.

  Example:
  - `--sc /inputs/CLL_GSE111014.h5ad`

- `--bulk <path>`  
  Path (inside the container) to the bulk expression `.h5ad` file.

  Example:
  - `--bulk /inputs/CLL_GSE111014_bulk.h5ad`

- `--annotation_key <key>`  
  The column name in `sc` `AnnData.obs` that contains cell-type labels used by the method.

  Example:
  - `--annotation_key Celltype_minor`

- `--out_dir <path>`  
  Output directory (inside the container). Must be under `/outputs/...` so that results are written to the bind-mounted host output directory.

  **Important for reproduction:**  
  `--out_dir` should contain a pretrained checkpoint folder:
  - `/outputs/.../model/` (copied from `BULK_simulation/<DATASET_NAME>/model/`)

- `--dataset_name <name>`  
  Dataset identifier used for internal configuration and naming output files.

  Example:
  - `--dataset_name CLL_GSE111014`

- `--n_cell <int>`  
  A method hyperparameter used in the benchmark configuration (kept consistent with the reported settings).

  Example:
  - `--n_cell 100`

- `--seed <int>`  
  Random seed for controlled randomness.

  Example:
  - `--seed 64`

- `--reproduce True`  
  Enables reproduction mode (intended to load and use the provided pretrained checkpoints for this benchmark case).

- `--specificity False`  
  Sets `specificity=False`.

  `specificity=False` indicates using the **random strategy** to simulate the training bulk data.

