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


def test_st_deconv(sc_adata, bulk_adata, annotation_key, out_dir, dataset_name, n_cell):
    sc_adata_obj = test_read_adata(sc_adata)
    sc_adata_obj.raw = None

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
        n_cell=int(n_cell),
        use_adversarial=True,
        specificity=True,
        giotto_gene_num=150,
        downsampling=False,
        high_purity=True,
    )
    print("end")


def parse_args():
    p = argparse.ArgumentParser(
        description="Run cytobulk bulk_deconv (parameterized inputs/outputs + dataset_name + annotation_key)."
    )
    p.add_argument("--sc_adata", required=True, help="Path to single-cell reference .h5ad")
    p.add_argument("--bulk_adata", required=True, help="Path to bulk .h5ad")
    p.add_argument("--out_dir", required=True, help="Output directory")
    p.add_argument("--dataset_name", required=True, help="Dataset name used for output naming")
    p.add_argument("--annotation_key", required=True, help="Column in sc_adata.obs for cell type labels")

    # keep everything else hard-coded; allow n_cell optionally (defaults to old 500)
    p.add_argument("--n_cell", type=int, default=500, help="n_cell passed to bulk_deconv (default: 500)")
    p.add_argument("--seed", type=int, default=64, help="Random seed (default: 64)")
    return p.parse_args()


def main():
    args = parse_args()
    set_seed(args.seed)

    test_st_deconv(
        sc_adata=args.sc_adata,
        bulk_adata=args.bulk_adata,
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