import os
import numpy as np
import pandas as pd
import anndata as ad
import scanpy as sc
import cytobulk as ct
import random
import torch
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


def read_h5ad(path: str) -> ad.AnnData:
    """Read AnnData from .h5ad."""
    if not path.endswith(".h5ad"):
        raise ValueError(f"Input must be .h5ad: {path}")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return sc.read_h5ad(path)


def bulk_deconv(sc_adata_path, bulk_adata_path, annotation_key, out_dir, dataset_name, n_cell):
    """
    Run cytobulk bulk_deconv using h5ad inputs only.
    """
    sc_adata = read_h5ad(sc_adata_path)
    bulk_adata = read_h5ad(bulk_adata_path)
    # keep behavior consistent with your original script
    sc_adata.raw = None


    os.makedirs(out_dir, exist_ok=True)

    print("start")
    ct.tl.bulk_deconv(
        bulk_data=bulk_adata,
        sc_adata=sc_adata,
        annotation_key=annotation_key,
        out_dir=out_dir,
        dataset_name=dataset_name,
        different_source=True,
        n_cell=int(n_cell),
        use_adversarial=True,
        specificity=False,
        giotto_gene_num=150,
        downsampling=False,
        reproduce = True,
    )
    print("end")


def parse_args():
    p = argparse.ArgumentParser(
        description="Run cytobulk bulk_deconv with parameterized h5ad inputs."
    )
    p.add_argument(
        "--sc_adata",
        required=True,
        help="Path to single-cell reference AnnData (.h5ad).",
    )
    p.add_argument(
        "--bulk_adata",
        required=True,
        help="Path to bulk AnnData (.h5ad).",
    )
    p.add_argument(
        "--out_dir",
        required=True,
        help="Output directory (will be created if not exists).",
    )
    p.add_argument(
        "--dataset_name",
        required=True,
        help="Dataset name used in output naming.",
    )
    return p.parse_args()


def main():
    args = parse_args()

    # keep your original fixed settings
    set_seed(64)
    annotation_key = "Celltype_minor"
    n_cell = 100

    bulk_deconv(
        sc_adata_path=args.sc_adata,
        bulk_adata_path=args.bulk_adata,
        annotation_key=annotation_key,
        out_dir=args.out_dir,
        dataset_name=args.dataset_name,
        n_cell=n_cell,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()