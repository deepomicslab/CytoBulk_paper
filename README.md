# CytoBulk: Results Reproduction & Visualization Tutorials

This repository contains comprehensive **installation guides**, **result reproduction tutorials**, and **visualization notebooks** for the CytoBulk bioinformatics tool.

## Overview

CytoBulk is a method for deconvolving bulk transcriptomics data and mapping H&E histology images using single-cell reference data. This repository provides reproducible workflows and tutorials for:

- **Installation** (Conda or Docker)
- **Result Reproduction** (multiple datasets and analysis types)
- **Data Visualization** (Jupyter notebooks)

---

## 📁 Repository Structure

### 1. Installation (`install/`)

Start here to set up CytoBulk in your environment:

- **`conda_install.md`** — Installation guide for **Conda environment**
  - Clone CytoBulk repository
  - Create Conda environment from `environment.yml`
  - Install Giotto in R (required for marker detection)
  - Verify installation

- **`docker_install.md`** — Installation guide for **Docker**
  - Check Docker prerequisites
  - Pull CytoBulk Docker image
  - Verify image availability

### 2. Result Reproduction (`run_case/`)

Contains detailed tutorials for reproducing CytoBulk results on various datasets. Choose between **Conda** or **Docker** environments:

#### A. Conda Tutorials (`conda_run_case/`)
Python scripts with accompanying Markdown documentation:

**Bulk RNA-seq deconvolution:**
- `bulk_deconv_12_simulation.*` — Synthetic bulk data deconvolution
- `bulk_deconv_brca.*` — BRCA dataset deconvolution
- `bulk_deconv_Flu_sdy67.*` — Flu study (SDY67) deconvolution
- `bulk_deconv_human_bulk.*` — Human bulk RNA-seq deconvolution
- `bulk_deconv_TCGA.*` — TCGA dataset deconvolution

**Bulk RNA → cell type mapping:**
- `bulk_brca_mapping.py` — BRCA bulk-to-single-cell mapping
- `bulk_human_bulk_mapping.py` — Human bulk mapping

**H&E image → scRNA mapping:**
- `he_mapping.py` — General H&E mapping script
- `HE_mapping_CID867.md` — CID867 dataset tutorial with visualization

**Spatial transcriptomics (ST) deconvolution:**
- `st_deconv_10x_BRCA.*` — 10x visium BRCA dataset
- `st_deconv_ER2.*` — ER2 dataset
- `st_deconv_merfish.*` — MERFISH data
- `st_deconv_mouse_mob.*` — Mouse MOB (main olfactory bulb) data
- `st_deconv_pdac.*` — PDAC (pancreatic cancer) data
- `st_deconv_seqfishplus.*` — seqFISH+ data
- `st_deconv_TNBC.*` — TNBC (triple-negative breast cancer) data

**ST reconstruction (st_mapping):**
- `st_10x_mapping.py` — ST cell type mapping (maps single cells to spatial locations)

#### B. Docker Tutorials (`docker_run_case/`)
Docker-compatible documentation for running the same analyses:

**Bulk deconvolution:**
- `bulk_deconv_*.md` — Docker versions of bulk deconvolution tutorials

**H&E mapping:**
- `HE_mapping_CID867.md` — Docker tutorial for CID867 dataset
- `HE_mapping_TCGA-37-4132.md` — Docker tutorial for TCGA-37-4132 dataset
- `bulk_deconv_HGSOC.md` — High-grade serous ovarian cancer dataset

**ST deconvolution:**
- `st_deconv_*.md` — Docker versions of ST deconvolution tutorials

### 3. Visualization (`visualization/`)

Interactive Jupyter notebooks for exploring and visualizing CytoBulk results:

- **`bulk_visualization.ipynb`** — Bulk RNA-seq deconvolution results
  - Visualize deconvolved cell-type fractions
  - Compare with ground truth
  - Statistical analysis and plots

- **`he_visualization.ipynb`** — H&E mapping results
  - Compare CytoBulk vs. expression-only methods
  - Gene-wise correlation and MSE metrics
  - Statistical significance testing

- **`st_visualization.ipynb`** — Spatial transcriptomics deconvolution results
  - Spatial distribution of cell types
  - Cell-type colocalization patterns
  - Comparative analysis across methods

---


