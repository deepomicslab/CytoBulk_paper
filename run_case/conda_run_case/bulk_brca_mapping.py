import os
import sys
import numpy as np
import anndata as ad
import pandas as pd
import cytobulk as ct
import scanpy as sc
import random
import torch
import time
from datetime import timedelta
import argparse
import warnings

warnings.filterwarnings("ignore")
# tested


def set_seed(seed=20250905):
    """Set random seed for reproducibility."""
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


def test_read_adata(adata_path):
    """Read AnnData from .h5ad."""
    return sc.read_h5ad(adata_path)


def test_read_df(data_path):
    """Read TSV as DataFrame."""
    return pd.read_csv(data_path, index_col=0, sep="\t")


def test_read_csv(data_path):
    """Read CSV as DataFrame."""
    return pd.read_csv(data_path, index_col=0, sep=",")


def test_bulk_mapping(sc_adata, deconv_adata, annotation_key, out_dir, dataset_name, j):
    """Run cytobulk bulk_mapping."""
    sc_adata_obj = test_read_adata(sc_adata)

    # Subset cells by orig.ident (fixed behavior)
    sc_adata_obj = sc_adata_obj[sc_adata_obj.obs["orig.ident"].isin(
        ["CID4471", "CID44971", "CID4290A", "CID4530N", "CID4515", "CID4535", "CID44041"]
    ), :]

    deconv_adata_obj = test_read_adata(deconv_adata)

    print("start")
    t0 = time.perf_counter()

    reconstructed_cell, reconstructed_adata = ct.tl.bulk_mapping(
        bulk_adata=deconv_adata_obj,
        sc_adata=sc_adata_obj,
        out_dir=out_dir,
        project="brca_bulk",
        n_cell=1000,
        annotation_key=annotation_key,
        multiprocessing=False,
    )

    elapsed = time.perf_counter() - t0
    print(f"end | elapsed: {format_elapsed(elapsed)}")

    return reconstructed_cell, reconstructed_adata


def parse_args():
    """Parse three CLI arguments: two inputs and one output directory."""
    p = argparse.ArgumentParser(
        description="Run cytobulk bulk_mapping (parameterized: sc_adata, deconv_adata, out_dir)."
    )
    p.add_argument("--sc_adata", required=True, help="Path to sc reference .h5ad.")
    p.add_argument("--deconv_adata", required=True, help="Path to deconvolved bulk .h5ad.")
    p.add_argument("--out_dir", required=True, help="Output directory.")
    return p.parse_args()


def main():
    # Fixed parameters (hard-coded)
    set_seed(64)
    annotation_key = "celltype_minor"
    dataset_name = "brca_bulk"  # kept for compatibility; not used by ct.tl.bulk_mapping here
    j = 500  # kept for compatibility; not used by ct.tl.bulk_mapping here

    args = parse_args()

    t0_main = time.perf_counter()
    test_bulk_mapping(
        sc_adata=args.sc_adata,
        deconv_adata=args.deconv_adata,
        annotation_key=annotation_key,
        out_dir=args.out_dir,
        dataset_name=dataset_name,
        j=j,
    )
    elapsed_main = time.perf_counter() - t0_main
    print(f"total elapsed (main): {format_elapsed(elapsed_main)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()