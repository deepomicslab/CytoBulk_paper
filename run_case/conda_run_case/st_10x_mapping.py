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
# tested
warnings.filterwarnings("ignore")


def set_seed(seed=20250905):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def test_read_adata(adata_path):
    return sc.read_h5ad(adata_path)


def test_read_df(data_path):
    return pd.read_csv(data_path, index_col=0, sep='\t')


def test_read_csv(data_path):
    return pd.read_csv(data_path, index_col=0, sep=',')


def test_st_mapping(sc_adata_path, st_adata_path, annotation_key, out_dir, dataset_name):
    sc_adata = test_read_adata(sc_adata_path)
    st_adata = test_read_adata(st_adata_path)

    print("Starting ST reconstruction (st_mapping)...")

    reconstructed_cell, reconstructed_adata = ct.tl.st_mapping(
        st_adata=st_adata,
        sc_adata=sc_adata,
        out_dir=out_dir,
        project=dataset_name,
        annotation_key=annotation_key
    )
    
    print("ST reconstruction completed.")


def parse_args():
    p = argparse.ArgumentParser(
        description="Run cytobulk st_mapping (ST reconstruction) with parameterized inputs."
    )
    p.add_argument(
        "--sc_adata",
        required=True,
        help="Path to single-cell AnnData .h5ad (sc_adata).",
    )
    p.add_argument(
        "--st_adata",
        required=True,
        help="Path to ST AnnData .h5ad from deconvolution step (e.g., 10x_sub3_st_adata.h5ad).",
    )
    p.add_argument(
        "--out_dir",
        required=True,
        help="Output directory.",
    )
    p.add_argument(
        "--dataset_name",
        required=True,
        help="Dataset name tag used by cytobulk (e.g., 10x_sub3).",
    )
    return p.parse_args()


def main():
    args = parse_args()
    
    # Set random seed for reproducibility
    set_seed(64)
    
    # Hardcoded parameters
    annotation_key = "cell_type"
    
    # Ensure output directory exists
    os.makedirs(args.out_dir, exist_ok=True)
    
    # Run ST reconstruction
    test_st_mapping(
        sc_adata_path=args.sc_adata,
        st_adata_path=args.st_adata,
        annotation_key=annotation_key,
        out_dir=args.out_dir,
        dataset_name=args.dataset_name
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
