# Reproducing Results: HE_mapping_CID867 (H&E mapping) — Conda Version

This document describes how to reproduce the **H&E (HE) mapping** results for **CID867** using a **Conda environment**, based on the provided **`HE_mapping_CID867.py`** script.

The input package **`HE_mapping_CID867/`** contains one task (one SVS image + one ground-truth expression reference + one LR table) plus multiple **anchor-gene** AnnData inputs at different gene-retention percentages (e.g., 5/10/15/20).

The workflow includes two stages:

1. **SVS preprocessing / tiling (optional)** via `ct.pp.process_svs_image(...)`
2. **H&E ↔ scRNA mapping** via `ct.tl.he_mapping(...)`

The **default case in this tutorial is 5% anchor genes**.

---

## 1) Download the `HE_mapping_CID867` package

Download the folder **`HE_mapping_CID867/`** from **`XXXX`**.

Folder structure (as provided):

- `HE_mapping_CID867/`
  - `input/`
    - `cropped_image_3_1.svs` *(input H&E SVS image)*
    - `demo_original_sc_adata.h5ad` *(ground-truth expression AnnData; used as `sc_adata` / `ori_adata`)*
    - `lrpairs.csv` *(ligand–receptor pairs table; columns should include `ligand`, `receptor`)*
    - `combinded_cent.txt` *(filtered segmentation cell-type + coordinate table; must be copied into each run `out_dir` for strict reproduction)*
    - `5/`
      - `NCBI867_1_3_cropped_coord_matched_filtered_5percent.h5ad` *(anchor expression; ~5% genes kept)*
    - `10/` *(anchor expression files; ~10% genes kept)*
    - `15/` *(anchor expression files; ~15% genes kept)*
    - `20/` *(anchor expression files; ~20% genes kept)*
  - `result_data/`
    - `5/`
      - `demo_matching_adata_cytobulk.h5ad` *(reference: Cytobulk matching result using 5% anchor genes)*
      - `demo_matching_adata_expression.h5ad` *(reference: expression-only OT result using 5% anchor genes)*
    - `10/` *(reference results for 10% anchor genes)*
    - `15/` *(reference results for 15% anchor genes)*
    - `20/` *(reference results for 20% anchor genes)*

> This tutorial assumes `input/` and `result_data/` are directly under `HE_mapping_CID867/`.

---

## 2) Choose your input and output folders

You only need to define:

- `SAMPLE_DIR`: where you placed `HE_mapping_CID867/`
- `DATA_DIR`: where the input files are stored (`${SAMPLE_DIR}/input`)
- `SAMPLE_OUT`: a writable folder where outputs will be saved

Example (replace with your own paths):

```bash
SAMPLE_DIR="/path/to/HE_mapping_CID867"
DATA_DIR="${SAMPLE_DIR}/input"
SAMPLE_OUT="/path/to/HE_mapping_CID867/out"
```

Create the output directory:

```bash
mkdir -p "${SAMPLE_OUT}"
```

---

## 3) Run HE mapping (5% anchor genes example)

### 3.1 Set anchor gene percentage and output subfolder

```bash
ANCHOR_PCT="5"
ANCHOR_H5AD="NCBI867_1_3_cropped_coord_matched_filtered_5percent.h5ad"
OUT_SUBDIR="out_ncbi867_image_3_1_test"
```

### 3.2 Prepare `--out_dir` (`combinded_cent.txt` check)

In this case, the segmentation-derived cell types/coordinates and the `.h5ad` coordinates were filtered to remove edge cells.  
For strict reproduction, it is recommended to copy `combinded_cent.txt` into the same folder you pass to `--out_dir` before running `HE_mapping_CID867.py`.

The current script behavior is:

- first check whether `${SAMPLE_OUT}/${OUT_SUBDIR}/combinded_cent.txt` already exists;
- if missing, try to copy it automatically from input-related paths (or from `--combinded_cent` if provided).

```bash
mkdir -p "${SAMPLE_OUT}/${OUT_SUBDIR}"
cp "${DATA_DIR}/combinded_cent.txt" "${SAMPLE_OUT}/${OUT_SUBDIR}/combinded_cent.txt"
```

### 3.3 Run the reproduction script

```bash
python HE_mapping_CID867.py \
  --svs_path "${DATA_DIR}/cropped_image_3_1.svs" \
  --image_out_dir "${SAMPLE_OUT}/ncbi867_image_3_1_test" \
  --sc "${DATA_DIR}/demo_original_sc_adata.h5ad" \
  --lr_csv "${DATA_DIR}/lrpairs.csv" \
  --annotation_key cell_type \
  --out_dir "${SAMPLE_OUT}/${OUT_SUBDIR}" \
  --project demo \
  --anchor_expression "${DATA_DIR}/${ANCHOR_PCT}/${ANCHOR_H5AD}" \
  --seed 20230602
```

Outputs will be written to:

```bash
${SAMPLE_OUT}/${OUT_SUBDIR}/
```

---

## 4) Run with different anchor gene percentages

To reproduce results using other anchor-gene retention percentages (10%, 15%, 20%), use the same script structure but change `ANCHOR_PCT` and `ANCHOR_H5AD`.

For each new `--out_dir`, you can still copy `combinded_cent.txt` first (recommended); otherwise the script will check and auto-copy when possible.

### 10% anchor genes:
```bash
ANCHOR_PCT="10"
ANCHOR_H5AD="NCBI867_1_3_cropped_coord_matched_filtered_10percent.h5ad"

OUT_SUBDIR="out_ncbi867_image_3_1_test_10pct"
mkdir -p "${SAMPLE_OUT}/${OUT_SUBDIR}"
cp "${DATA_DIR}/combinded_cent.txt" "${SAMPLE_OUT}/${OUT_SUBDIR}/combinded_cent.txt"

python HE_mapping_CID867.py \
  --svs_path "${DATA_DIR}/cropped_image_3_1.svs" \
  --image_out_dir "${SAMPLE_OUT}/ncbi867_image_3_1_test_10pct" \
  --enable_cropping 0 \
  --sc "${DATA_DIR}/demo_original_sc_adata.h5ad" \
  --lr_csv "${DATA_DIR}/lrpairs.csv" \
  --annotation_key cell_type \
  --out_dir "${SAMPLE_OUT}/${OUT_SUBDIR}" \
  --project demo \
  --k_neighbor 30 \
  --batch_size 15000 \
  --mapping_sc 1 \
  --return_adata 1 \
  --sc_st true \
  --anchor_expression "${DATA_DIR}/${ANCHOR_PCT}/${ANCHOR_H5AD}" \
  --expression_weight 0.5 \
  --skip_filtering true \
  --seed 20230602
```

### 15% anchor genes:
```bash
ANCHOR_PCT="15"
ANCHOR_H5AD="NCBI867_1_3_cropped_coord_matched_filtered_15percent.h5ad"

OUT_SUBDIR="out_ncbi867_image_3_1_test_15pct"
mkdir -p "${SAMPLE_OUT}/${OUT_SUBDIR}"
cp "${DATA_DIR}/combinded_cent.txt" "${SAMPLE_OUT}/${OUT_SUBDIR}/combinded_cent.txt"

python HE_mapping_CID867.py \
  --svs_path "${DATA_DIR}/cropped_image_3_1.svs" \
  --image_out_dir "${SAMPLE_OUT}/ncbi867_image_3_1_test_15pct" \
  --enable_cropping 0 \
  --sc "${DATA_DIR}/demo_original_sc_adata.h5ad" \
  --lr_csv "${DATA_DIR}/lrpairs.csv" \
  --annotation_key cell_type \
  --out_dir "${SAMPLE_OUT}/${OUT_SUBDIR}" \
  --project demo \
  --k_neighbor 30 \
  --batch_size 15000 \
  --mapping_sc 1 \
  --return_adata 1 \
  --sc_st true \
  --anchor_expression "${DATA_DIR}/${ANCHOR_PCT}/${ANCHOR_H5AD}" \
  --expression_weight 0.5 \
  --skip_filtering true \
  --seed 20230602
```

### 20% anchor genes:
```bash
ANCHOR_PCT="20"
ANCHOR_H5AD="NCBI867_1_3_cropped_coord_matched_filtered_20percent.h5ad"
# ... (same structure as above, with updated paths)
```

---

## 5) DeepCMorph version note and troubleshooting

Because different `DeepCMorph` versions may be used in different environments, reproduced results may have slight differences.

If you need to **fully reproduce** our results, please download our provided `DeepCMorph` model version from:

`xxx`

Then place it in your pip-installed package path at:

```bash
cytobulk/tools/model/pretrained_models/DeepCMorph_Datasets_Combined_41_classes_acc_8159.pth
```

If you encounter the following error while running `ct.tl.he_mapping`:

```text
_pickle.UnpicklingError: invalid load key, '<'.
```

This error usually means the pretrained model file was not fully downloaded (corrupted/incomplete file). To resolve it, manually download the model file and place it in the package pretrained-model directory.

Download link:

`xxx/DeepCMorph_Datasets_Combined_41_classes_acc_8159.pth`

Then place it at:

```bash
cytobulk/tools/model/pretrained_models/DeepCMorph_Datasets_Combined_41_classes_acc_8159.pth
```

---

## 6) Parameter explanation

This section explains the main arguments used by the `HE_mapping_CID867.py` command.  
They correspond to two steps in your pipeline:

1) **SVS preprocessing (tiling/cropping)** via `ct.pp.process_svs_image(...)`  
2) **H&E ↔ expression mapping** via `ct.tl.he_mapping(...)`

---

### 6.1 SVS preprocessing (cropping / tiling)

These parameters control how the `.svs` image is converted into tiles.

- `--svs_path`  
  Path to the input `.svs` slide.  
  In CID867: `${DATA_DIR}/cropped_image_3_1.svs`.

- `--image_out_dir`  
  Output directory where the generated tiles will be saved.  
  In CID867 example: `${SAMPLE_OUT}/ncbi867_image_3_1_test`.

- `--enable_cropping` (0/1)  
  Whether to crop a specific region (1) or process without cropping (0).  
  In the CID867 reference script: `enable_cropping=False` → use `0`.

- `--crop_size`  
  Tile size in pixels (e.g., 224 means 224×224).

- `--magnification`  
  Magnification level used to read/crop the slide.

- `--center_x`, `--center_y`  
  Center coordinates (in slide coordinate system) for defining the crop grid.

- `--fold_width`, `--fold_height`  
  Grid size around the center. Roughly determines how many tiles are generated:
  approximately `fold_width × fold_height` tiles (exact behavior depends on implementation).

> Note: In your `HE_mapping_CID867.py`, if `--svs_path` is provided, preprocessing will run and
> `image_dir` will be set to `--image_out_dir` automatically.  
> If you already have tiles, you can leave `--svs_path` empty and instead pass `--image_dir`.

---

### 6.2 HE mapping (optimal transport alignment): `ct.tl.he_mapping(...)`

Run H&E-stained image cell type mapping with single-cell RNA-seq data.

This function predicts cell types from H&E-stained histology images and aligns them with single-cell RNA-seq (scRNA-seq) data using optimal transport. It computes spatial distributions and matches cell types between the image and single-cell data.

---

## 7) Parameters

- `image_dir : str`  
  Directory containing H&E image tiles.  
  In your script, when `--svs_path` is used, `image_dir` is set to `--image_out_dir`.

- `out_dir : str`  
  Directory where output files will be saved.

- `project : str`  
  Project name used for naming output files.

- `lr_data : pandas.DataFrame, optional (default: None)`  
  Ligand–receptor pairs table with columns `ligand` and `receptor`.

- `sc_adata : anndata.AnnData, optional (default: None)`  
  Single-cell / reference expression AnnData.  
  In CID867: `demo_original_sc_adata.h5ad`.

- `annotation_key : str, optional (default: "curated_celltype")`  
  Key in `sc_adata.obs` for cell type annotations.  
  In CID867: `cell_type`.

- `k_neighbor : int, optional (default: 30)`  
  Number of neighbors used to build the graph for H&E-derived cells.

- `alpha : float | "auto_compute", optional (default: "auto_compute")`  
  Trade-off parameter for Fused Gromov–Wasserstein OT (range [0, 1]) controlling balance between
  graph structure alignment and feature/label matching.  
  In CID867 reference run: `alpha=0`.

- `mapping_sc : bool, optional (default: True)`  
  Whether to map H&E image-derived cells to the single-cell/reference data.  
  In the CLI: `--mapping_sc 1`.

- `batch_size : int, optional (default: 3000)`  
  Max number of cells processed per batch (memory/runtime knob).  
  In CID867 reference run: `15000`.

- `downsampling : bool, optional (default: False)`  
  Whether to downsample single-cell data to match the distribution inferred from H&E images.

- `anchor_expression : anndata.AnnData, optional (default: None)`  
  Anchor expression AnnData for H&E coordinates.  
  For CID867, this is the per-percentage file under `input/<pct>/...percent.h5ad`
  (e.g., 5% anchor genes).

- `sc_st : bool, optional (default: False)`  
  Whether the input single-cell data is spatial single-cell (ST-like) data.  
  If `True`, the method uses looser filtering/normalization.  
  In CID867 reference run: `True` (CLI: `--sc_st true`).

- `expression_weight : float, optional (default: 0.0)`  
  Weight for gene-expression similarity in the cost matrix (range [0, 1]).  
  Higher values increase the influence of expression similarity vs. cell-type matching.  
  In CID867 reference run: `0.5`.

- `skip_filtering : bool, optional (default: False)`  
  Whether to skip filtering of the single-cell/reference data.  
  In CID867 reference run: `True` (CLI: `--skip_filtering true`).

- `return_adata : bool` *(exposed in your CLI wrapper)*  
  Whether to save an AnnData object containing mapping outputs for downstream analysis.

- `seed : int, optional (default: None)`  
  Random seed for reproducibility.  
  In CID867 reference run: `20230602`.
