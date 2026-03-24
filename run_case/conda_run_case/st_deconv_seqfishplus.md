# Reproducing Results: ST Deconvolution on SeqFISH+ (seqfishPLUS) — Conda Version

This document describes how to reproduce the **SeqFISH+ spatial transcriptomics (ST) deconvolution** results using a **Conda environment**.

---

## 1) Download the `ST_seqfishplus` package

Download the folder **`ST_seqfishplus/`** from [https://doi.org/10.5281/zenodo.18495002](https://doi.org/10.5281/zenodo.18495002).

It contains three subfolders:

- `input_data/`  
  Input data for this case:
  - single-cell reference (`sc`, `.h5ad`): `seqfish_adata.h5ad`
  - spatial transcriptomics data (`st`, `.h5ad`): `simulated_spot_seqfish_adata.h5ad`

- `st_model/`  
  **Pretrained model checkpoints** for the seqfishPLUS case.

- `result_data/`  
  Reference results provided for comparison/validation.

---

## 2) Notes on reproducibility

Even with a fixed random seed, strict reproduction may be affected by:

1. **Platform-dependent numerical variation**  
   Parts of the pipeline rely on matrix factorization and low-level linear algebra routines. Numerical results can differ slightly across hosts due to differences in BLAS/LAPACK backends (e.g., MKL vs OpenBLAS), CPU vectorization, thread scheduling, and floating-point non-associativity. These small differences can propagate downstream and lead to measurable output deviations.

2. **Default Top-50 selection behavior**  
   The pipeline uses a default **Top-50 selection feature** step. When this set is recomputed, ties or near-ties may be resolved differently across environments or library versions, which can further contribute to differences in outputs.

### Recommendation for strict reproduction

To reproduce our reported results as closely as possible:

- **Reuse the provided pretrained checkpoints** (copy `st_model/` into your chosen output directory), and
- Run the pipeline with `--reproduce TRUE` (or enable `reproduce=True` in the Python function call, depending on your script interface).

---

## 3) Choose your input and output folders

You only need to define:

- `PKG_DIR`: where you placed `ST_seqfishplus/`
- `DATA_DIR`: where the input `.h5ad` files are stored (`${PKG_DIR}/input_data`)
- `OUTPUT_DIR`: a writable folder where outputs will be saved

Example (replace with your own paths):

```bash
PKG_DIR="/path/to/ST_seqfishplus"
DATA_DIR="${PKG_DIR}/input_data"
OUTPUT_DIR="/path/to/your/output_folder"
```

Create the output directory:
```bash
mkdir -p "${OUTPUT_DIR}"
```

## 4) Copy pretrained checkpoints into OUT_DIR (required)

Before running, copy the pretrained checkpoints into the output directory you will use for --out_dir:
```bash
cp -r "${PKG_DIR}/st_model" "${OUTPUT_DIR}/st_model"
```

This ensures the run loads the same pretrained checkpoints rather than producing environment-dependent parameters.

## 5) Run the reproduction script
```bash
python st_deconv_seqfishplus.py \
  --sc_adata "${DATA_DIR}/seqfish_adata.h5ad" \
  --st_adata "${DATA_DIR}/simulated_spot_seqfish_adata.h5ad" \
  --out_dir "${OUTPUT_DIR}"
  ```
Outputs will be written to:
```bash
${OUTPUT_DIR}/
```
