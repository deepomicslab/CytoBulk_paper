import os
import numpy as np
import cytobulk as ct
import scanpy as sc
import random
import torch
import time
import argparse
from datetime import timedelta
import warnings

warnings.filterwarnings("ignore")

def set_seed(seed: int = 64):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def format_elapsed(seconds: float) -> str:
    """Format elapsed time like 0:24:50 (1490 seconds)."""
    total_seconds = int(round(seconds))
    return f"{timedelta(seconds=total_seconds)} ({total_seconds} seconds)"


def read_adata(path: str):
    return sc.read_h5ad(path)


def run_bulk_mapping(
    sc_adata_path: str,
    deconv_adata_path: str,
    out_dir: str,
    n_cell: int = 500,
    seed: int = 64,
):
    # Hard-coded metadata (as requested)
    project = "human_bulk"
    annotation_key = "Manually_curated_celltype"

    set_seed(seed)

    sc_adata_obj = read_adata(sc_adata_path)
    deconv_adata_obj = read_adata(deconv_adata_path)

    os.makedirs(out_dir, exist_ok=True)

    print("start")
    t0 = time.perf_counter()

    reconstructed_cell, reconstructed_adata = ct.tl.bulk_mapping(
        bulk_adata=deconv_adata_obj,
        sc_adata=sc_adata_obj,
        out_dir=out_dir,
        project=project,
        n_cell=int(n_cell),
        annotation_key=annotation_key,
        multiprocessing=False,
    )

    elapsed = time.perf_counter() - t0
    print(f"end | elapsed: {format_elapsed(elapsed)}")

    return reconstructed_cell, reconstructed_adata


def parse_args():
    p = argparse.ArgumentParser(
        description="Run Cytobulk bulk_mapping with parameterized input .h5ad files and output directory."
    )
    p.add_argument("--sc_adata", required=True, help="Path to single-cell reference .h5ad")
    p.add_argument("--deconv_adata", required=True, help="Path to deconvolved bulk .h5ad (e.g., *_bulk_adata.h5ad)")
    p.add_argument("--out_dir", required=True, help="Output directory")

    p.add_argument("--n_cell", type=int, default=500, help="n_cell used for mapping (default: 500)")
    p.add_argument("--seed", type=int, default=64, help="Random seed (default: 64)")
    return p.parse_args()


def main():
    args = parse_args()

    t0_main = time.perf_counter()
    run_bulk_mapping(
        sc_adata_path=args.sc_adata,
        deconv_adata_path=args.deconv_adata,
        out_dir=args.out_dir,
        n_cell=args.n_cell,
        seed=args.seed,
    )
    elapsed_main = time.perf_counter() - t0_main
    print(f"total elapsed: {format_elapsed(elapsed_main)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()