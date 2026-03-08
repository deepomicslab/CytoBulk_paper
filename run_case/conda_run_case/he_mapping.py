# he_mapping.py
import os
import argparse
import random
import time
import warnings

import numpy as np
import pandas as pd
import scanpy as sc
import torch

import cytobulk as ct

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore")


def set_seed(seed: int = 20230602):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def read_adata(adata_path: str):
    """Read AnnData from .h5ad path."""
    if not os.path.exists(adata_path):
        raise FileNotFoundError(f"File not found: {adata_path}")
    return sc.read_h5ad(adata_path)


def read_csv(csv_path: str):
    """Read CSV from path."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")
    return pd.read_csv(csv_path)


def format_time(seconds: float) -> str:
    """Format seconds into H:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"


def maybe_map_cell_types(adata, annotation_key: str):
    """Optionally normalize a few known cell type strings."""
    # Only map types that exist; missing keys are ignored by pandas.replace
    mapping = {
        "plasma cells": "Plasma Cells",
        "connective tissue": "Connective Tissue",
        "epithelial": "Epithelial Cells",
        "neutrophils": "Neutrophils",
        "lymphocytes": "Lymphocytes",
    }
    adata.obs[annotation_key] = adata.obs[annotation_key].replace(mapping)
    return adata


def parse_alpha(alpha_raw: str):
    """
    Parse alpha argument.

    Allowed:
      - "auto_compute" (string): keep as-is
      - numeric string / float-like: convert to float
    """
    if alpha_raw is None:
        return "auto_compute"

    if isinstance(alpha_raw, (int, float)):
        return float(alpha_raw)

    s = str(alpha_raw).strip()
    if s.lower() in {"auto_compute", "auto", "autocompute"}:
        return "auto_compute"

    try:
        return float(s)
    except ValueError as e:
        raise ValueError(
            f"Invalid --alpha value: {alpha_raw}. Use 'auto_compute' or a float like 0.5."
        ) from e


def parse_bool(x):
    """Parse booleans from common CLI inputs."""
    if isinstance(x, bool):
        return x
    s = str(x).strip().lower()
    if s in {"true", "1", "yes", "y", "t"}:
        return True
    if s in {"false", "0", "no", "n", "f"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {x}")


def run_he_mapping(
    svs_path: str,
    image_dir: str,
    image_out_dir: str,
    enable_cropping: bool,
    crop_size: int,
    magnification: int,
    center_x: int,
    center_y: int,
    fold_width: int,
    fold_height: int,
    sc_adata_path: str,
    lr_csv_path: str,
    annotation_key: str,
    out_dir: str,
    project: str,
    k_neighbor: int,
    alpha,  # can be float or "auto_compute"
    batch_size: int,
    mapping_sc: bool,
    return_adata: bool,
    # Extra parameters (match your direct ct.tl.he_mapping call)
    sc_st: bool = False,                 # NOTE: default is False
    anchor_expression_path: str = "",     # NOTE: empty -> anchor_expression=None
    expression_weight: float = 0.0,       # NOTE: default 0
    skip_filtering: bool = False,         # NOTE: default False
):
    os.makedirs(out_dir, exist_ok=True)
    if image_out_dir:
        os.makedirs(image_out_dir, exist_ok=True)

    # --- SVS preprocessing ---
    # If svs_path is provided, ALWAYS call ct.pp.process_svs_image and write outputs
    # into image_out_dir. The enable_cropping flag controls whether to crop (True)
    # or only run preprocessing steps (False). After preprocessing, we set image_dir
    # to image_out_dir for downstream he_mapping.
    #
    # If svs_path is NOT provided, the user must provide an existing image_dir.
    if svs_path:
        if not os.path.exists(svs_path):
            raise FileNotFoundError(f"svs_path not found: {svs_path}")
        if not image_out_dir:
            raise ValueError(
                "image_out_dir is required when svs_path is provided "
                "(ct.pp.process_svs_image outputs will be written there)."
            )
        os.makedirs(image_out_dir, exist_ok=True)

        ct.pp.process_svs_image(
            svs_path=svs_path,
            output_dir=image_out_dir,
            crop_size=int(crop_size),
            magnification=int(magnification),
            center_x=int(center_x),
            center_y=int(center_y),
            fold_width=int(fold_width),
            fold_height=int(fold_height),
            enable_cropping=bool(enable_cropping),
        )
        image_dir = image_out_dir

    # Validate image_dir
    if not image_dir:
        raise ValueError(
            "image_dir is required. Either:\n"
            "  (1) provide --image_dir pointing to existing tiles, OR\n"
            "  (2) provide --svs_path and --image_out_dir (enable_cropping can be 0/1)."
        )
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"image_dir not found: {image_dir}")

    # Load inputs
    sc_adata = read_adata(sc_adata_path)
    if annotation_key not in sc_adata.obs.columns:
        raise KeyError(
            f"annotation_key='{annotation_key}' not found in sc.obs. "
            f"Available keys include: {list(sc_adata.obs.columns)[:50]}"
        )

    sc_adata = maybe_map_cell_types(sc_adata, annotation_key=annotation_key)
    lr_data = read_csv(lr_csv_path)

    # anchor_expression default is None (only load if a path is provided)
    anchor_expression = None
    if anchor_expression_path:
        anchor_expression = read_adata(anchor_expression_path)

    # Run mapping
    # alpha can be "auto_compute" or float (e.g., 0.5)
    ct.tl.he_mapping(
        image_dir=image_dir,
        out_dir=out_dir,
        project=project,
        lr_data=lr_data,
        sc_adata=sc_adata,
        annotation_key=annotation_key,
        k_neighbor=int(k_neighbor),
        alpha=alpha,
        batch_size=int(batch_size),
        mapping_sc=bool(mapping_sc),
        return_adata=bool(return_adata),
        sc_st=bool(sc_st),
        anchor_expression=anchor_expression,
        expression_weight=float(expression_weight),
        skip_filtering=bool(skip_filtering),
    )


def parse_args():
    p = argparse.ArgumentParser(description="Run Cytobulk H&E mapping")

    # SVS preprocessing options
    p.add_argument(
        "--enable_cropping",
        type=int,
        default=1,
        choices=[0, 1],
        help="Whether to crop tiles from SVS when --svs_path is provided. default: 1 (True)",
    )
    p.add_argument(
        "--svs_path",
        default="",
        help="Path to .svs. If provided, ct.pp.process_svs_image will be run (regardless of enable_cropping).",
    )
    p.add_argument(
        "--image_out_dir",
        default="",
        help="Output dir for ct.pp.process_svs_image (required if --svs_path is set).",
    )

    p.add_argument("--crop_size", type=int, default=224)
    p.add_argument("--magnification", type=int, default=1)
    p.add_argument("--center_x", type=int, default=21000)
    p.add_argument("--center_y", type=int, default=11200)
    p.add_argument("--fold_width", type=int, default=10)
    p.add_argument("--fold_height", type=int, default=10)

    # If you already have tiles, provide image_dir and leave svs_path empty
    p.add_argument("--image_dir", default="", help="Directory containing processed image tiles")

    # Inputs for he_mapping
    p.add_argument("--sc", required=True, help="Path to scRNA AnnData (.h5ad)")
    p.add_argument("--lr_csv", required=True, help="Path to ligand-receptor pairs CSV")
    p.add_argument("--annotation_key", default="he_cell_type", help="Cell type key in sc_adata.obs")

    # Outputs / parameters
    p.add_argument("--out_dir", required=True, help="Output directory")
    p.add_argument("--project", required=True, help="Project name tag")

    p.add_argument("--k_neighbor", type=int, default=30)

    # alpha default should be "auto_compute", but allow passing 0.5 etc.
    p.add_argument(
        "--alpha",
        type=str,
        default="auto_compute",
        help='Alpha for mapping. Use "auto_compute" (default) or a float value like 0.5.',
    )

    p.add_argument("--batch_size", type=int, default=10000)

    # Booleans controlled by 0/1
    p.add_argument("--mapping_sc", type=int, default=1, choices=[0, 1], help="default: 1 (True)")
    p.add_argument("--return_adata", type=int, default=1, choices=[0, 1], help="default: 1 (True)")

    # Extra parameters to match ct.tl.he_mapping signature in your example
    p.add_argument(
        "--sc_st",
        type=parse_bool,
        default=False,  # NOTE: default is False
        help="Whether to enable sc_st mode. default: false",
    )
    p.add_argument(
        "--anchor_expression",
        default="",
        help="Optional: path to anchor expression AnnData (.h5ad). Default: not used (None).",
    )
    p.add_argument("--expression_weight", type=float, default=0.0, help="default: 0")
    p.add_argument("--skip_filtering", type=parse_bool, default=False, help="default: false")

    p.add_argument("--seed", type=int, default=20230602, help="Random seed")
    return p.parse_args()


def main():
    args = parse_args()
    set_seed(args.seed)

    start = time.time()

    alpha = parse_alpha(args.alpha)

    run_he_mapping(
        svs_path=args.svs_path,
        image_dir=args.image_dir,
        image_out_dir=args.image_out_dir,
        enable_cropping=bool(args.enable_cropping),
        crop_size=args.crop_size,
        magnification=args.magnification,
        center_x=args.center_x,
        center_y=args.center_y,
        fold_width=args.fold_width,
        fold_height=args.fold_height,
        sc_adata_path=args.sc,
        lr_csv_path=args.lr_csv,
        annotation_key=args.annotation_key,
        out_dir=args.out_dir,
        project=args.project,
        k_neighbor=args.k_neighbor,
        alpha=alpha,
        batch_size=args.batch_size,
        mapping_sc=bool(args.mapping_sc),
        return_adata=bool(args.return_adata),
        sc_st=bool(args.sc_st),
        anchor_expression_path=args.anchor_expression,
        expression_weight=args.expression_weight,
        skip_filtering=bool(args.skip_filtering),
    )

    elapsed = time.time() - start
    print(f"Total running time: {format_time(elapsed)} ({elapsed:.2f} seconds)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()
        raise