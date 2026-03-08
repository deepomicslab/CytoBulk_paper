import os
import numpy as np
import cytobulk as ct
import scanpy as sc
import random
import torch
import argparse
import warnings

warnings.filterwarnings("ignore")

def set_seed(seed: int = 64):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def read_adata(path: str):
    return sc.read_h5ad(path)


def run_bulk_deconv(
    sc_adata_path: str,
    bulk_adata_path: str,
    out_dir: str,
    n_cell: int = 500,
    seed: int = 64,
):
    # Hard-coded metadata (as requested)
    dataset_name = "human_bulk"
    annotation_key = "Manually_curated_celltype"

    set_seed(seed)

    sc_adata = read_adata(sc_adata_path)

    bulk_adata = read_adata(bulk_adata_path)

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
    )
    print("end")


def parse_args():
    p = argparse.ArgumentParser(
        description="Run Cytobulk bulk_deconv with parameterized input .h5ad files and output directory."
    )
    p.add_argument("--sc_adata", required=True, help="Path to single-cell reference .h5ad")
    p.add_argument("--bulk_adata", required=True, help="Path to bulk/simulated bulk .h5ad")
    p.add_argument("--out_dir", required=True, help="Output directory")

    p.add_argument("--n_cell", type=int, default=500, help="n_cell used for pseudo-bulk simulation (default: 500)")
    p.add_argument("--seed", type=int, default=64, help="Random seed (default: 64)")
    return p.parse_args()


def main():
    args = parse_args()
    run_bulk_deconv(
        sc_adata_path=args.sc_adata,
        bulk_adata_path=args.bulk_adata,
        out_dir=args.out_dir,
        n_cell=args.n_cell,
        seed=args.seed,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()