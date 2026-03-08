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
        reproduce=True,
    )
    print("end")


def format_time(seconds):
    """Format seconds to HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"


def parse_args():
    p = argparse.ArgumentParser(
        description="Run cytobulk st_deconv (MOB) with parameterized inputs."
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

    # Fix random seed to 15 as requested
    random_seed = 15
    set_seed(random_seed)

    program_start_time = time.time()

    # Keep all other parameters exactly as in your version
    annotation_key = "subtype"
    dataset_name = "mouse_mob"
    j = 15

    os.makedirs(args.out_dir, exist_ok=True)

    test_st_deconv(
        sc_adata=args.sc_adata,
        st_adata=args.st_adata,
        annotation_key=annotation_key,
        out_dir=args.out_dir,
        dataset_name=dataset_name,
        j=j,
    )

    program_end_time = time.time()
    total_elapsed_time = program_end_time - program_start_time
    total_formatted_time = format_time(total_elapsed_time)

    print(f"\n{'='*70}")
    print("PROGRAM COMPLETED")
    print(f"Seed: {random_seed}")
    print(f"Total running time: {total_formatted_time} ({total_elapsed_time:.2f} seconds)")
    print(f"{'='*70}\n")


if __name__ == "__main__":  # Entry point
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()