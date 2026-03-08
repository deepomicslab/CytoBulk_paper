import os
import sys
import numpy as np
import anndata as ad
import pandas as pd
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


def test_read_adata(adata_path):
    """Read AnnData from .h5ad."""
    return sc.read_h5ad(adata_path)


def test_read_df(data_path):
    """Read TSV as DataFrame."""
    return pd.read_csv(data_path, index_col=0, sep="\t")


def test_read_csv(data_path):
    """Read CSV as DataFrame."""
    return pd.read_csv(data_path, index_col=0, sep=",")


def test_st_deconv(sc_adata, bulk_adata, annotation_key, out_dir, dataset_name, j):
    """Run cytobulk deconvolution."""
    sc_adata_obj = test_read_adata(sc_adata)
    bulk_adata_obj = test_read_adata(bulk_adata)

    os.makedirs(out_dir, exist_ok=True)

    print("start")
    ct.tl.bulk_deconv(
        bulk_data=bulk_adata_obj,
        sc_adata=sc_adata_obj,
        annotation_key=annotation_key,
        out_dir=out_dir,
        dataset_name=dataset_name,
        different_source=True,
        n_cell=int(j),
        use_adversarial=True,
        specificity=True,
        giotto_gene_num=150,
        downsampling=True,
        reproduce = True,
    )
    print("end")


def parse_args():
    """Parse three CLI arguments: two inputs and one output directory."""
    p = argparse.ArgumentParser(
        description="Run cytobulk bulk_deconv (parameterized: sc_adata, bulk_adata, out_dir)."
    )
    p.add_argument("--sc_adata", required=True, help="Path to sc reference .h5ad.")
    p.add_argument("--bulk_adata", required=True, help="Path to bulk .h5ad.")
    p.add_argument("--out_dir", required=True, help="Output directory.")
    return p.parse_args()


def main():
    # Fixed parameters (hard-coded)
    set_seed(64)
    annotation_key = "celltype_minor"
    dataset_name = "CID_4535"
    n_cell = 500

    args = parse_args()

    test_st_deconv(
        sc_adata=args.sc_adata,
        bulk_adata=args.bulk_adata,
        annotation_key=annotation_key,
        out_dir=args.out_dir,
        dataset_name=dataset_name,
        j=n_cell,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()