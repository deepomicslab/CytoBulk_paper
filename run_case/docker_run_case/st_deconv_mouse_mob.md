# Reproducing Results: ST Deconvolution on Mouse MOB (mouse_mob)

This document describes how to reproduce the **mouse MOB spatial transcriptomics (ST) deconvolution** results using our Docker image.

---

## 1) Download the `ST_mouse_mob` package

Download the folder **`ST_mouse_mob/`** from [https://doi.org/10.5281/zenodo.18495002](https://doi.org/10.5281/zenodo.18495002).

It contains three subfolders:

- `input/`  
  Input data for this case:
  - single-cell reference (`sc`, `.h5ad`): `sc_layer_mob.h5ad`
  - spatial transcriptomics data (`st`, `.h5ad`): `st_mob.h5ad`

- `st_model/`  
  **Pretrained model checkpoints** for the mouse MOB case.

- `result_data/`  
  Reference results provided for comparison/validation.

---

## 2) Notes on reproducibility

Even with a fixed seed, strict reproduction may be affected by:

1. **Platform-dependent numerical variation**  
   Some steps depend on low-level linear algebra kernels and GPU/CUDA determinism settings. Small floating-point differences across hosts (BLAS backend, threads, GPU type/driver) can propagate and cause output deviations.

2. **Top-k feature selection (`top_k=50`)**  
   The pipeline uses **Top-50 feature selection**. In rare tie/near-tie cases, selected features may differ across environments/library versions.

### Recommendation for strict reproduction

To reproduce our reported results as closely as possible:

- **Reuse the provided pretrained checkpoints** (copy `st_model/` into your chosen output directory), and
- Run with `--reproduce True`.

---

## 3) Choose your input and output folders (host-side)

Define two host directories:

- `INPUT_DIR`: where you placed `ST_mouse_mob/input`
- `OUTPUT_DIR`: a writable folder where outputs will be saved

Example (replace with your own paths):

```bash
PKG_DIR="/path/to/ST_mouse_mob"
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
  --sc /inputs/sc_layer_mob.h5ad \
  --st /inputs/st_mob.h5ad \
  --annotation_key subtype \
  --out_dir "/outputs/" \
  --dataset_name mouse_mob \
  --n_cell 15 \
  --seed 15 \
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
  - Must contain the input files.

  **Container side (`/inputs`):**
  - The pipeline will read:
    - `/inputs/sc_layer_mob.h5ad`
    - `/inputs/st_mob.h5ad`

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
  - `--sc /inputs/sc_layer_mob.h5ad`

- `--st <path>`  
  Path (inside the container) to the spatial transcriptomics `.h5ad` file.

  Example:
  - `--st /inputs/st_mob.h5ad`

- `--annotation_key <key>`  
  The column name in `sc` `AnnData.obs` that contains cell-type labels used by the method.

  Example:
  - `--annotation_key subtype`

- `--out_dir <path>`  
  Output directory (inside the container). Must be under `/outputs/...` so that results are written to the bind-mounted host output directory.


  **Important for reproduction:**  
  `--out_dir` should contain a pretrained checkpoint folder:
  - `/outputs/st_model/` (copied from `ST_mouse_mob/st_model/`)

- `--dataset_name <name>`  
  Dataset identifier used for internal configuration and naming.

  Example:
  - `--dataset_name mouse_mob`

- `--n_cell <int>`  
  A method hyperparameter used in the benchmark configuration (kept consistent with the reported settings).

  Example:
  - `--n_cell 15`

- `--seed <int>`  
  Random seed for controlled randomness.

  Example:
  - `--seed 15`

- `--reproduce True`  
  Enables reproduction mode (loading pretrained checkpoints as intended for this case).

---

