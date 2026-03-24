import os
import sys
import numpy as np
import anndata as ad
import pandas as pd
import cytobulk as ct
import scanpy as sc
import random
import torch
import warnings
import argparse

warnings.filterwarnings("ignore")
# tested


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
    return pd.read_csv(data_path, index_col=0, sep="\t")


def test_read_csv(data_path):
    return pd.read_csv(data_path, index_col=0, sep=",")


def test_st_deconv(sc_adata, st_adata, annotation_key, out_dir, dataset_name, j):
    sc_ = test_read_adata(sc_adata)

    st_ = test_read_adata(st_adata)

    print("start")
    ct.tl.st_deconv(
        st_adata=st_,
        sc_adata=sc_,
        annotation_key=annotation_key,
        out_dir=out_dir,
        dataset_name=dataset_name,
        different_source=True,
        n_cell=int(j),
        use_adversarial=True,
        top_k=50,
        giotto_gene_num=150,
        downsampling=False,
        reproduce = True,
    )
    print("end")


def parse_args():
    p = argparse.ArgumentParser(
        description="Run cytobulk st_deconv (PDAC settings) with parameterized inputs."
    )
    p.add_argument(
        "--sc_adata",
        required=True,
        help="Path to single-cell AnnData .h5ad (sc_adata).",
    )
    p.add_argument(
        "--st_adata",
        required=True,
        help="Path to spatial/spot AnnData .h5ad (st_adata).",
    )
    p.add_argument(
        "--out_dir",
        required=True,
        help="Output directory.",
    )
    return p.parse_args()


def main():
    args = parse_args()

    # keep original fixed settings from your PDAC script
    set_seed(64)
    annotation_key = "cell_type"
    dataset_name = "pdac"
    j = 10

    os.makedirs(args.out_dir, exist_ok=True)

    test_st_deconv(
        sc_adata=args.sc_adata,
        st_adata=args.st_adata,
        annotation_key=annotation_key,
        out_dir=args.out_dir,
        dataset_name=dataset_name,
        j=j,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()