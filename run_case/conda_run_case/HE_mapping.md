# Reproducing Results: HE Mapping (H&E mapping) — Conda Version

This document describes how to reproduce the **H&E (HE) mapping** results using a **Conda environment**, based on the provided `he_mapping.py` script (which corresponds to the Docker `he_mapping` entrypoint).

The workflow includes two stages:

1. **SVS preprocessing / tiling (optional)** via `ct.pp.process_svs_image(...)`
2. **H&E ↔ scRNA mapping** via `ct.tl.he_mapping(...)`

---

## 1) Download the `HE_mapping_TCGA-37-4132` package

Download the folder **`HE_mapping_TCGA-37-4132/`** from **`XXXX`**.

It contains two subfolders:

- `input/`  
  Input data for this case:
  - single-cell reference (`sc`, `.h5ad`): `HTAN_MSK.h5ad`
  - ligand–receptor pairs table (`.csv`): `lrpairs.csv` (should include columns `ligand`, `receptor`)
  - H&E whole-slide image (`.svs`): `TCGA-37-4132.svs`

- `result_data/`  
  Reference results provided for comparison/validation:
  - `combinded_cent.txt`
  - `commot_result_adata.h5ad`

> This tutorial assumes `input/` and `result_data/` are directly under `HE_mapping_TCGA-37-4132/`.

---

## 2) Choose your input and output folders

You only need to define:

- `PKG_DIR`: where you placed `HE_mapping_TCGA-37-4132/`
- `DATA_DIR`: where the input files are stored (`${PKG_DIR}/input`)
- `OUTPUT_DIR`: a writable folder where outputs will be saved

Example (replace with your own paths):

```bash
PKG_DIR="/path/to/HE_mapping_TCGA-37-4132"
DATA_DIR="${PKG_DIR}/input"
OUTPUT_DIR="/path/to/HE_mapping_TCGA-37-4132/out"
```

Create the output directory:


```bash
mkdir -p "${OUTPUT_DIR}"
```

## 3) Run the reproduction script
```bash
python he_mapping.py \
  --svs_path "${DATA_DIR}/TCGA-37-4132.svs" \
  --image_out_dir "${OUTPUT_DIR}/demo_split_test" \
  --enable_cropping 1 \
  --sc "${DATA_DIR}/HTAN_MSK.h5ad" \
  --lr_csv "${DATA_DIR}/lrpairs.csv" \
  --annotation_key "he_cell_type" \
  --out_dir "${OUTPUT_DIR}/demo" \
  --project "demo" \
  --seed 20230602
```
Outputs will be written to:
```bash
${OUTPUT_DIR}/demo/
```