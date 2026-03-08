# Reproducing Results: ST Deconvolution on SeqFISH+ (seqfishPLUS)

This document describes how to reproduce the **SeqFISH+ spatial transcriptomics (ST) deconvolution** results using our Docker image.

---

## 1) Download the `ST_seqfishplus` package

Download the folder **`ST_seqfishplus/`** from **`XXXX`**.

It contains three subfolders:

- `input/`  
  Input data for this case:
  - single-cell reference (`sc`, `.h5ad`)
  - spatial transcriptomics data (`st`, `.h5ad`)

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
- Run the pipeline with `--reproduce True`.

---

## 3) Choose your input and output folders (host-side)

You only need to define two host directories:

- `INPUT_DIR`: where you placed `ST_seqfishplus/input`
- `OUTPUT_DIR`: a writable folder where outputs will be saved

Example (replace with your own paths):

```bash
PKG_DIR="/path/to/ST_seqfishplus" 
INPUT_DIR="${PKG_DIR}/input"
OUTPUT_DIR="/path/to/your/output_folder"
```

Create the output directory:
```bash
mkdir -p "${OUTPUT_DIR}"
```

## 4) Copy pretrained checkpoints into OUTPUT_DIR (required)

Before running Docker, copy the pretrained checkpoints into the output directory you will use for --out_dir:
```bash
cp -r "${PKG_DIR}/st_model" "${OUTPUT_DIR}/st_model"
```
This ensures the run loads the same pretrained checkpoints rather than producing environment-dependent parameters.

## 5) Run Docker to reproduce the results
```bash
docker run --rm -it \
  -e PYTHONUNBUFFERED=1 \
  -e HOST_UID="$(id -u)" \
  -e HOST_GID="$(id -g)" \
  -v "${INPUT_DIR}":/inputs:ro \
  -v "${OUTPUT_DIR}":/outputs \
  kristawang/cytobulk:1.0.0 \
  st_deconv \
  --sc /inputs/seqfish_adata.h5ad \
  --st /inputs/simulated_spot_seqfish_adata.h5ad \
  --annotation_key cell_types \
  --out_dir "/outputs/" \
  --dataset_name seqfish_plus \
  --n_cell 4 \
  --seed 64 \
  --reproduce True
```

## 6)Explanation of mounts and parameters

This section explains each Docker option, mount, environment variable, and `st_deconv` argument used in the reproduction command.

---

## 6.1 Docker options

- `--rm`  
  Removes the container after it exits. This keeps the system clean and avoids accumulating stopped containers.

- `-it`  
  Allocates an interactive pseudo-TTY. This is helpful for:
  - better real-time log streaming, and
  - easier debugging if you later switch to an interactive shell.

---

## 6.2 Environment variables

- `-e PYTHONUNBUFFERED=1`  
  Forces Python to flush stdout/stderr immediately (unbuffered output), so logs appear in real time rather than being printed only at the end.

- `-e HOST_UID="$(id -u)"` and `-e HOST_GID="$(id -g)"`  
  Passes your host user’s numeric UID/GID into the container.  
  The container entry script uses these values to `chown` the output directory (specified by `--out_dir`) back to your host user/group at the end of the run. This prevents output files on bind-mounted directories from remaining owned by `root` on the host.

  - `$(id -u)` returns the current user’s UID on the host.
  - `$(id -g)` returns the current user’s primary GID on the host.

---

## 6.3 Volume mounts (host paths you must configure)

Docker binds host directories into the container filesystem. In our portable setup we use fixed container mount points:

### Inputs mount (read-only)
- `-v "${INPUT_DIR}":/inputs:ro`  

  **Host side (`${INPUT_DIR}`):**
  - Must contain the SeqFISH+ input files.

  **Container side (`/inputs`):**
  - The pipeline will read:
    - `/inputs/seqfish_adata.h5ad`
    - `/inputs/simulated_spot_seqfish_adata.h5ad`

  `:ro` means read-only, which is recommended to protect the input data from accidental modification.

### Outputs mount (read-write)
- `-v "${OUTPUT_DIR}":/outputs`

  **Host side (`${OUTPUT_DIR}`):**
  - Must be writable.

  **Container side (`/outputs`):**
  - All results are written under `/outputs/...`
  - Your `--out_dir` must be a path **within** `/outputs/` to ensure outputs persist on the host.

---

## 6.4 Command selection

- `st_deconv`  
  Selects the ST deconvolution pipeline entrypoint inside the image.

---

## 6.5 `st_deconv` arguments

- `--sc <path>`  
  Path (inside the container) to the single-cell reference `.h5ad` file.

  Example:
  - `--sc /inputs/seqfish_adata.h5ad`

- `--st <path>`  
  Path (inside the container) to the spatial transcriptomics `.h5ad` file.

  Example:
  - `--st /inputs/simulated_spot_seqfish_adata.h5ad`

- `--annotation_key <key>`  
  The column name in `sc` `AnnData.obs` that contains cell-type labels used by the method.

  Example:
  - `--annotation_key cell_types`

- `--out_dir <path>`  
  Output directory (inside the container). Must be under `/outputs/...` so that results are written to the bind-mounted host output directory.


  **Important for reproduction:**  
  `--out_dir` should contain a pretrained checkpoint folder:
  - `/outputs/.../st_model/` (copied from `ST_seqfishplus/st_model/`)

- `--dataset_name <name>`  
  Dataset identifier used for internal configuration and naming.

  Example:
  - `--dataset_name seqfish_plus`

- `--n_cell <int>`  
  A method hyperparameter used in the benchmark configuration (kept consistent with the reported settings).

  Example:
  - `--n_cell 4`

- `--seed <int>`  
  Random seed for controlled randomness.

  Example:
  - `--seed 64`

- `--reproduce True`  
  Enables reproduction mode (loading pretrained checkpoints as intended for this case).

---

