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
import argparse
from datetime import timedelta
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


def format_time(seconds):
    """Format seconds to HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"


def test_read_adata(adata_path):
    return sc.read_h5ad(adata_path)


def test_read_df(data_path):
    return pd.read_csv(data_path, index_col=0, sep='\t')


def test_read_csv(data_path):
    return pd.read_csv(data_path, index_col=0, sep=',')


def test_bulk_deconv(sc_adata, bulk_adata, annotation_key, out_dir, dataset_name, n_cell):
    # Start timing
    start_time = time.time()
    print(f"\n{'='*70}")
    print(f"Starting deconvolution for {dataset_name}")
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    sc_adata = test_read_adata(sc_adata)
    bulk = test_read_adata(bulk_adata)

    print("Processing bulk deconvolution...")
    ct.tl.bulk_deconv(bulk_data=bulk, sc_adata=sc_adata,
                      annotation_key=annotation_key,
                      out_dir=out_dir,
                      dataset_name=dataset_name,
                      different_source=True,
                      n_cell=int(n_cell),
                      use_adversarial=True,
                      specificity=True,
                      giotto_gene_num=150,
                      downsampling=False,
                      reproduce = True)
    
    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Format and print time information
    formatted_time = format_time(elapsed_time)
    print(f"\n{'='*70}")
    print(f"Deconvolution completed for {dataset_name}")
    print(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Running time: {formatted_time} ({elapsed_time:.2f} seconds)")
    print(f"{'='*70}\n")
    
    return elapsed_time


def parse_args():
    p = argparse.ArgumentParser(
        description="Run cytobulk bulk_deconv for HGSOC dataset."
    )
    p.add_argument(
        "--sc_adata",
        required=True,
        help="Path to single-cell AnnData .h5ad (sc_adata).",
    )
    p.add_argument(
        "--bulk_adata",
        required=True,
        help="Path to bulk/simulated bulk AnnData .h5ad.",
    )
    p.add_argument(
        "--out_dir",
        required=True,
        help="Output directory.",
    )
    p.add_argument(
        "--dataset_name",
        required=True,
        help="Dataset name tag used by cytobulk (e.g., HGSOC).",
    )
    return p.parse_args()


def main():
    args = parse_args()
    
    # Start timing for entire program
    program_start_time = time.time()
    
    set_seed(64)
    
    # Hardcoded parameters
    annotation_key = "cellType"
    n_cell = 100
    
    # Ensure output directory exists
    os.makedirs(args.out_dir, exist_ok=True)
    
    # Run deconvolution
    test_bulk_deconv(args.sc_adata, args.bulk_adata, annotation_key, args.out_dir, args.dataset_name, n_cell)
    
    # End timing for entire program
    program_end_time = time.time()
    total_elapsed_time = program_end_time - program_start_time
    total_formatted_time = format_time(total_elapsed_time)
    
    print(f"\n{'='*70}")
    print(f"PROGRAM COMPLETED")
    print(f"Total running time: {total_formatted_time} ({total_elapsed_time:.2f} seconds)")
    print(f"{'='*70}\n")

        
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
