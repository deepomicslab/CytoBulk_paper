# Reproducing Results: ST Deconvolution and ST Reconstruction on 10x_BRCA

This document describes how to reproduce the **10x_BRCA spatial transcriptomics (ST) deconvolution and ST reconstruction** results using our **Docker image**.

---

## 1) Download the `ST_10X_BRCA` package

Download the folder **`ST_10X_BRCA/`** from [https://doi.org/10.5281/zenodo.18495002](https://doi.org/10.5281/zenodo.18495002).

It contains **six sample subfolders**:

- `sample1/`
- `sample2/`
- `sample3/`
- `sample4/`
- `sample5/`
- `sample6/`

Each `sampleX/` folder contains three subfolders:

- `input/`  
  - single-cell reference (`sc`, `.h5ad`): `sc_adata.h5ad` (shared across all samples)
  - spatial transcriptomics data (`st`, `.h5ad`): `st_adata_sub_X.h5ad` (sample-specific)

- `st_model/`  
  **Pretrained model checkpoints** for the **10x_BRCA** case (sample-specific).

- `result_data/`  
  Reference results provided for comparison/validation.

### Input naming convention (important)

- `sc_adata.h5ad` is shared across all samples.
- `st_adata_sub_X.h5ad` corresponds to sample `X`.

Example (sample3):

- `ST_10X_BRCA/sample3/input/sc_adata.h5ad`
- `ST_10X_BRCA/sample3/input/st_adata_sub_3.h5ad`

---

## 2) Notes on reproducibility

Even with a fixed random seed, strict reproduction may be affected by:

1. **Platform-dependent numerical variation**  
   Parts of the pipeline rely on matrix factorization and low-level linear algebra routines. Numerical results can differ slightly across hosts due to differences in BLAS/LAPACK backends (e.g., MKL vs OpenBLAS), CPU vectorization, thread scheduling, and floating-point non-associativity. These small differences can propagate downstream and lead to measurable output deviations.

2. **Default Top-50 feature selection behavior**  
   The pipeline uses a default **Top-50 feature selection** step (`top_k=50`). When this set is recomputed, ties or near-ties may be resolved differently across environments or library versions, which can further contribute to differences in outputs.

### Recommendation for strict reproduction

To reproduce our reported results as closely as possible:

- **Reuse the provided pretrained checkpoints** (copy `st_model/` into your chosen output directory), and
- Run the pipeline with `--reproduce True`.

---

## 3) Choose your input and output folders (host-side)

Define two host directories:

- `CASE_DIR`: where you placed `ST_10X_BRCA/`
- `OUTPUT_DIR`: a writable folder where outputs will be saved

Example:

```bash
CASE_DIR="/path/to/ST_10X_BRCA"
OUTPUT_DIR="/path/to/your/output_folder"
```

Create the output directory:
```bash
mkdir -p "${OUTPUT_DIR}"
```

## 4) Example: reproduce sample3

## 4.1 Set variables
```bash
SAMPLE="sample3"
SUB_ID="3"

SAMPLE_DIR="${CASE_DIR}/${SAMPLE}"
SAMPLE_OUT="${OUTPUT_DIR}/${SAMPLE}"

mkdir -p "${SAMPLE_OUT}"
```

## 4.2 Copy pretrained checkpoints into OUTPUT_DIR (required)

Before running Docker, copy the pretrained checkpoints into the output directory you will use for --out_dir:
```bash
cp -r "${SAMPLE_DIR}/st_model" "${SAMPLE_OUT}/st_model"
```
This ensures the run loads the same pretrained checkpoints rather than producing environment-dependent parameters.

## 5) Run Docker to reproduce the results (sample3)
```bash
docker run --rm -it \
  -e PYTHONUNBUFFERED=1 \
  -e HOST_UID="$(id -u)" \
  -e HOST_GID="$(id -g)" \
  -v "${SAMPLE_DIR}/input":/inputs:ro \
  -v "${SAMPLE_OUT}":/outputs \
  kristawang/cytobulk:1.0.0 \
  st_deconv \
  --sc /inputs/sc_adata.h5ad \
  --st /inputs/st_adata_sub_${SUB_ID}.h5ad \
  --annotation_key cell_type \
  --out_dir "/outputs/" \
  --dataset_name 10x_sub${SUB_ID} \
  --n_cell 8 \
  --seed 64 \
  --reproduce True
```

Outputs will be written under:
```bash
${OUTPUT_DIR}/sample3/
```
For other samples, just update:

```bash
SAMPLE="samplex"
SUB_ID="x"
```
accordingly.

## 6) ST reconstruction (st_mapping) from the deconvolution outputs (sample3)

After finishing ST deconvolution (Section 5), run **ST reconstruction** using the `st_reconstruction` entrypoint in the same Docker image.

### 6.1 Inputs

- **sc_adata_path**: same as in the deconvolution step  
  - `/inputs/sc_adata.h5ad`

- **st_adata_path**: the ST AnnData written by the deconvolution step, located inside the previous `--out_dir` output folder.  
  For sample3 this is typically:

  - `${SAMPLE_OUT}/output/10x_sub3_st_adata.h5ad`

- **out_dir**: keep the same output directory as before (so all artifacts stay together)  
  - `/outputs/`

### 6.2 Run Docker (sample3)
First set (or reuse) the same dataset name as in deconvolution:

```bash
DATASET_NAME="10x_sub3"
```

Then run reconstruction:
```bash
docker run --rm -it \
  -e PYTHONUNBUFFERED=1 \
  -e HOST_UID="$(id -u)" \
  -e HOST_GID="$(id -g)" \
  -v "${SAMPLE_DIR}/input":/inputs:ro \
  -v "${SAMPLE_OUT}":/outputs \
  kristawang/cytobulk:1.0.0 \
  st_reconstruction \
  --sc /inputs/sc_adata.h5ad \
  --st "/outputs/output/${DATASET_NAME}_st_adata.h5ad" \
  --annotation_key cell_type \
  --out_dir "/outputs/" \
  --dataset_name "${DATASET_NAME}" \
  --seed 64
```

Reconstruction outputs will be written under:
```bash
${OUTPUT_DIR}/sample3/
```

