# Docker Tutorial: HE_mapping_CID867 (H&E mapping)

This document describes how to reproduce the **H&E (HE) mapping** results for **CID867** using the Cytobulk **Docker** workflow by running the provided **`he_mapping.py`** inside the container.

The input package **`HE_mapping_CID867/`** contains one task (one SVS image + one ground-truth expression reference + one LR table) plus multiple **anchor-gene** AnnData inputs at different gene-retention percentages (e.g., 5/10/15/20).

---

## 1) Download the `HE_mapping_CID867` package

Download the folder **`HE_mapping_CID867/`** from [https://doi.org/10.5281/zenodo.18495002](https://doi.org/10.5281/zenodo.18495002).

Folder structure (as provided):

- `HE_mapping_CID867/`
  - `input/`
    - `cropped_image_3_1.svs` *(input H&E SVS image)*
    - `demo_original_sc_adata.h5ad` *(ground-truth expression AnnData; used as `sc_adata` / `ori_adata`)*
    - `lrpairs.csv` *(ligand–receptor pairs table; columns should include `ligand`, `receptor`)*
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

## 2) Run HE mapping in Docker

### 2.1 Set paths (Linux / macOS)

Set your local package directory and output directory:

```bash
SAMPLE_DIR="/path/to/HE_mapping_CID867"
SAMPLE_OUT="/path/to/HE_mapping_CID867/out"
```
Create output dir if needed:
```bash
mkdir -p "${SAMPLE_OUT}"
```

### 2.2 Prepare `--out_dir` (required)

In this case, the segmentation-derived cell types/coordinates and the `.h5ad` coordinates were filtered to remove edge cells.  
For strict reproduction, copy `combinded_cent.txt` into the same folder you pass to `--out_dir` before running `he_mapping`.

```bash
OUT_SUBDIR="out_ncbi867_image_3_1_test"
mkdir -p "${SAMPLE_OUT}/${OUT_SUBDIR}"
cp "${SAMPLE_DIR}/input/combinded_cent.txt" "${SAMPLE_OUT}/${OUT_SUBDIR}/combinded_cent.txt"
```

### 2.3 Run he_mapping (5% anchor genes example)
```bash
ANCHOR_PCT="5"
ANCHOR_H5AD="NCBI867_1_3_cropped_coord_matched_filtered_5percent.h5ad"

docker run --rm -it \
  -e PYTHONUNBUFFERED=1 \
  -v "${SAMPLE_DIR}":/work \
  -v "${SAMPLE_DIR}/input":/inputs:ro \
  -v "${SAMPLE_OUT}":/outputs \
  -w /work \
  kristawang/cytobulk:1.0.0 \
  he_mapping \
    --svs_path /inputs/cropped_image_3_1.svs \
    --image_out_dir /outputs/ncbi867_image_3_1_test \
    --enable_cropping 0 \
    --sc /inputs/demo_original_sc_adata.h5ad \
    --lr_csv /inputs/lrpairs.csv \
    --annotation_key cell_type \
    --out_dir "/outputs/${OUT_SUBDIR}" \
    --project demo \
    --k_neighbor 30 \
    --batch_size 15000 \
    --mapping_sc 1 \
    --return_adata 1 \
    --sc_st true \
    --anchor_expression "/inputs/${ANCHOR_PCT}/${ANCHOR_H5AD}" \
    --expression_weight 0.5 \
    --skip_filtering true \
    --seed 20230602
```

## 3) Parameter explanation (what the main arguments mean)

This section explains the main arguments used by the Docker command (running `python he_mapping.py`).  
They correspond to two steps in your pipeline:

1) **SVS preprocessing (tiling/cropping)** via `ct.pp.process_svs_image(...)`  
2) **H&E ↔ expression mapping** via `ct.tl.he_mapping(...)`

---

### 3.1 SVS preprocessing (cropping / tiling)

These parameters control how the `.svs` image is converted into tiles.

- `--svs_path`  
  Path to the input `.svs` slide.  

- `--image_out_dir`  
  Output directory where the generated tiles will be saved.  

- `--enable_cropping` (0/1)  
  Whether to crop a specific region (1) or process without cropping (0).  

- `--crop_size`  
  Tile size in pixels (e.g., 224 means 224×224).

- `--magnification`  
  Magnification level used to read/crop the slide.

- `--center_x`, `--center_y`  
  Center coordinates (in slide coordinate system) for defining the crop grid.

- `--fold_width`, `--fold_height`  
  Grid size around the center. Roughly determines how many tiles are generated:
  approximately `fold_width × fold_height` tiles (exact behavior depends on implementation).

> Note: In your `he_mapping.py`, if `--svs_path` is provided, preprocessing will run and
> `image_dir` will be set to `image_out_dir` automatically.  
> If you already have tiles, you can leave `--svs_path` empty and instead pass `--image_dir`.

---

### 3.2 HE mapping (optimal transport alignment): `ct.tl.he_mapping(...)`

Run H&E-stained image cell type mapping with single-cell RNA-seq data.

This function predicts cell types from H&E-stained histology images and aligns them with single-cell RNA-seq (scRNA-seq) data using optimal transport. It computes spatial distributions and matches cell types between the image and single-cell data.

## 4) Parameters

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


- `annotation_key : str, optional (default: "curated_celltype")`  
  Key in `sc_adata.obs` for cell type annotations.  


- `k_neighbor : int, optional (default: 30)`  
  Number of neighbors used to build the graph for H&E-derived cells.

- `alpha : float | "auto_compute", optional (default: "auto_compute")`  
  Trade-off parameter for Fused Gromov–Wasserstein OT (range [0, 1]) controlling balance between
  graph structure alignment and feature/label matching.  


- `mapping_sc : bool, optional (default: True)`  
  Whether to map H&E image-derived cells to the single-cell/reference data.  

- `batch_size : int, optional (default: 3000)`  
  Max number of cells processed per batch (memory/runtime knob).  


- `downsampling : bool, optional (default: False)`  
  Whether to downsample single-cell data to match the distribution inferred from H&E images.

- `anchor_expression : anndata.AnnData, optional (default: None)`  
  Anchor expression AnnData for H&E coordinates.  
  For CID867, this is the per-percentage file under `input/<pct>/...percent.h5ad`
  (e.g., 5% anchor genes).

- `sc_st : bool, optional (default: False)`  
  Whether the input single-cell data is spatial single-cell (ST-like) data.  
  If `True`, the method uses looser filtering/normalization.  


- `expression_weight : float, optional (default: 0.0)`  
  Weight for gene-expression similarity in the cost matrix (range [0, 1]).  
  Higher values increase the influence of expression similarity vs. cell-type matching.  


- `skip_filtering : bool, optional (default: False)`  
  Whether to skip filtering of the single-cell/reference data.  


- `return_adata : bool`  
  Whether to save an AnnData object containing mapping outputs for downstream analysis.


