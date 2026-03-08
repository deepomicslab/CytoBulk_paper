# Docker Tutorial: HE_mapping (H&E mapping)

This document describes how to reproduce the **H&E (HE) mapping** results using the Cytobulk **Docker** workflow with the **`he_mapping`** entrypoint.

The input package **`HE_mapping_TCGA-37-4132/`** contains one task (one SVS slide + one scRNA reference + one LR table).

---

## 1) Download the `HE_mapping_TCGA-37-4132` package

Download the folder **`HE_mapping_TCGA-37-4132/`** from **`XXXX`**.

Folder structure (as provided):

- `HE_mapping_TCGA-37-4132/`
  - `input/`
    - `HTAN_MSK.h5ad` *(single-cell reference, scRNA AnnData)*
    - `lrpairs.csv` *(ligand–receptor pairs table; columns should include `ligand`, `receptor`)*
    - `TCGA-37-4132.svs` *(H&E whole-slide image)*
  - `result_data/`
    - `combinded_cent.txt` *(reference: predicted cell coordinates + predicted cell type)*
    - `commot_result_adata.h5ad` *(reference: CommOT analysis output AnnData)*

> This tutorial assumes `input/` and `result_data/` are directly under `HE_mapping_TCGA-37-4132/`.

---

## 2) Run HE mapping in Docker

### 2.1 Set paths

Set your local package directory and output directory:

```bash
SAMPLE_DIR="/path/to/HE_mapping_TCGA-37-4132"
SAMPLE_OUT="/path/to/HE_mapping_TCGA-37-4132/out"
```

Create output dir if needed:
```bash
mkdir -p "${SAMPLE_OUT}"
```

### 2.2 Run he_mapping
This run will:

crop/split the .svs into image tiles (via ct.pp.process_svs_image), then
run H&E-to-scRNA mapping (via ct.tl.he_mapping).
```bash
docker run --rm -it \
  -e PYTHONUNBUFFERED=1 \
  -e HOST_UID="$(id -u)" \
  -e HOST_GID="$(id -g)" \
  -v "${SAMPLE_DIR}/input":/inputs:ro \
  -v "${SAMPLE_OUT}":/outputs \
  kristawang/cytobulk:1.0.0 \
  he_mapping \
  --svs_path /inputs/TCGA-37-4132.svs \
  --image_out_dir /outputs/demo_split_test \
  --enable_cropping 1 \
  --crop_size 224 \
  --magnification 1 \
  --center_x 21000 \
  --center_y 11200 \
  --fold_width 10 \
  --fold_height 10 \
  --sc /inputs/HTAN_MSK.h5ad \
  --lr_csv /inputs/lrpairs.csv \
  --annotation_key he_cell_type \
  --out_dir /outputs/demo \
  --project demo \
  --k_neighbor 30 \
  --alpha 0.5 \
  --batch_size 10000 \
  --mapping_sc 1 \
  --return_adata 1 \
  --seed 20230602
```
Outputs will be written under:
- ${SAMPLE_OUT}/demo/ (mapping outputs)
- ${SAMPLE_OUT}/demo_split_test/ (generated tiles)


## 3) Parameter explanation (what the main arguments mean)

This section explains the main arguments used by the Docker command for `he_mapping`.  
They correspond to two steps in your pipeline:

1) **SVS preprocessing (tiling/cropping)** via `ct.pp.process_svs_image(...)`  
2) **H&E ↔ scRNA mapping** via `ct.tl.he_mapping(...)`

---

### 3.1 SVS preprocessing (cropping / tiling)

These parameters control how the `.svs` whole-slide image is converted into tiles.

- `--enable_cropping` (0/1)  
  Whether to crop a specific region (1) or process the entire image (0).  
  
- `--svs_path`  
  Path to the input `.svs` whole-slide image.  

- `--image_out_dir`  
  Output directory where cropped image tiles will be saved.  

- `--crop_size`  
  Tile size in pixels (e.g., 224 means 224×224).  
  Larger tiles cover more tissue per tile; affects tile count and potentially runtime.

- `--magnification`  
  Magnification level used to read/crop the slide.

- `--center_x`, `--center_y`  
  Center coordinates (in slide coordinate system) for defining the crop grid.

- `--fold_width`, `--fold_height`  
  Grid size around the center. Roughly determines how many tiles are generated:
  approximately `fold_width × fold_height` tiles (exact behavior depends on implementation).

---

### 3.2 Inputs for HE mapping (optimal transport alignment)

These parameters control the mapping between image-derived cells and scRNA-seq data.

- `--sc`  
  Path to the scRNA reference AnnData (`.h5ad`).  
  Must contain:
  - expression matrix
  - cell-type labels in `sc.obs[annotation_key]`

- `--lr_csv`  
  Path to ligand–receptor pairs CSV.  
  Typically contains columns: `ligand`, `receptor`.  
  Used in downstream communication-related computations in the mapping workflow.

- `--annotation_key`  
  Column name in `sc_adata.obs` storing cell-type annotations  
  (default in script: `he_cell_type`).

- `--k_neighbor`  
  Number of neighbors used to construct the graph on H&E-derived cells  
  (default: 30). This graph is used by the optimal-transport alignment.

- `--alpha`  
  Trade-off parameter for **Fused Gromov–Wasserstein optimal transport** (range \([0,1]\)).  
  Controls balance between:
  - **graph structure** alignment, and
  - **feature / label matching**.  
  (default: 0.5)

- `--batch_size`  
  Maximum number of cells processed per batch (memory/runtime knob).  
  Larger values may be faster but require more memory.

- `--mapping_sc` (0/1)  
  Whether to perform mapping between H&E image cells and scRNA-seq cells.  
  - `1`: run mapping (default)
  - `0`: only return image-side predictions (no sc alignment)

- `--return_adata` (0/1)  
  Whether to return/save an AnnData object containing mapping outputs  
  for downstream analysis (e.g., CommOT).

---

### 3.3 Output naming / bookkeeping

- `--out_dir`  
  Directory where output files will be written.

- `--project`  
  Project name tag used for naming output files.

---

### 3.4 Reproducibility

- `--seed`  
  Random seed used to control randomness in `random`, `numpy`, and `torch`  
  (as set by `set_seed()` in `he_mapping.py`).
