import os
import numpy as np
import pandas as pd
import anndata as ad
import cytobulk as ct
import scanpy as sc
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


def read_h5ad(adata_path: str) -> ad.AnnData:
    """Read an AnnData object from an .h5ad file."""
    if not adata_path.endswith(".h5ad"):
        raise ValueError(f"Input must be a .h5ad file: {adata_path}")
    if not os.path.exists(adata_path):
        raise FileNotFoundError(adata_path)
    return sc.read_h5ad(adata_path)


def run_bulk_deconv(
    sc_adata_path: str,
    bulk_adata_path: str,
    annotation_key: str,
    out_dir: str,
    dataset_name: str,
    n_cell: int,
):
    """Run Cytobulk bulk deconvolution with h5ad inputs."""
    sc_adata = read_h5ad(sc_adata_path)
    print(sc_adata)

    bulk_adata = read_h5ad(bulk_adata_path)

    # Create output directory if it does not exist
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
        specificity=True,
        giotto_gene_num=150,
        downsampling=False,
        reproduce = True
    )
    print("end")


def parse_args():
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(
        description="Run cytobulk bulk_deconv with parameterized inputs (h5ad only)."
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
    p.add_argument(
        "--annotation_key",
        required=True,
        help="Column name in sc_adata.obs containing cell type labels.",
    )

    # Optional arguments (defaults keep the original behavior)
    p.add_argument("--seed", type=int, default=64, help="Random seed. Default: 64")
    p.add_argument(
        "--n_cell",
        type=int,
        default=500,
        help="n_cell passed to bulk_deconv. Default: 500",
    )
    return p.parse_args()


def main():
    """Entry point."""
    args = parse_args()
    set_seed(args.seed)

    run_bulk_deconv(
        sc_adata_path=args.sc_adata,
        bulk_adata_path=args.bulk_adata,
        annotation_key=args.annotation_key,
        out_dir=args.out_dir,
        dataset_name=args.dataset_name,
        n_cell=args.n_cell,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()