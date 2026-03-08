import os
import argparse
import random
import time
import warnings
import shutil

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
    if not os.path.exists(adata_path):
        raise FileNotFoundError(f"File not found: {adata_path}")
    return sc.read_h5ad(adata_path)


def read_csv(csv_path: str):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")
    return pd.read_csv(csv_path)


def format_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"


def maybe_map_cell_types(adata, annotation_key: str):
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
    if isinstance(x, bool):
        return x
    s = str(x).strip().lower()
    if s in {"true", "1", "yes", "y", "t"}:
        return True
    if s in {"false", "0", "no", "n", "f"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {x}")


def resolve_combinded_cent_path(
    combinded_cent_path: str,
    sc_adata_path: str,
    anchor_expression_path: str,
):
    candidates = []

    if combinded_cent_path:
        candidates.append(combinded_cent_path)

    if sc_adata_path:
        candidates.append(os.path.join(os.path.dirname(sc_adata_path), "combinded_cent.txt"))

    if anchor_expression_path:
        anchor_dir = os.path.dirname(anchor_expression_path)
        input_dir = os.path.dirname(anchor_dir)
        candidates.append(os.path.join(input_dir, "combinded_cent.txt"))

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate

    return ""


def prepare_combinded_cent(out_dir: str, combinded_cent_path: str):
    os.makedirs(out_dir, exist_ok=True)
    dst_path = os.path.join(out_dir, "combinded_cent.txt")

    if os.path.exists(dst_path):
        print("[INFO] combinded_cent.txt already exists in out_dir, skip copy.")
        return

    if not combinded_cent_path:
        raise FileNotFoundError(
            "`combinded_cent.txt` is missing in out_dir and no valid source path was found. "
            "Please copy it manually as documented in md, or pass --combinded_cent explicitly."
        )

    if not os.path.exists(combinded_cent_path):
        raise FileNotFoundError(f"combinded_cent file not found: {combinded_cent_path}")

    if os.path.abspath(combinded_cent_path) != os.path.abspath(dst_path):
        shutil.copy2(combinded_cent_path, dst_path)
        print(f"[INFO] Copied combinded_cent.txt -> {dst_path}")
    else:
        print("[INFO] combinded_cent.txt is already in out_dir, skip copy.")


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
    alpha,
    batch_size: int,
    mapping_sc: bool,
    return_adata: bool,
    sc_st: bool,
    anchor_expression_path: str,
    expression_weight: float,
    skip_filtering: bool,
    combinded_cent_path: str,
):
    os.makedirs(out_dir, exist_ok=True)
    if image_out_dir:
        os.makedirs(image_out_dir, exist_ok=True)

    resolved_combinded_cent = resolve_combinded_cent_path(
        combinded_cent_path=combinded_cent_path,
        sc_adata_path=sc_adata_path,
        anchor_expression_path=anchor_expression_path,
    )
    prepare_combinded_cent(out_dir=out_dir, combinded_cent_path=resolved_combinded_cent)

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

    if not image_dir:
        raise ValueError(
            "image_dir is required. Either:\n"
            "  (1) provide --image_dir pointing to existing tiles, OR\n"
            "  (2) provide --svs_path and --image_out_dir."
        )
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"image_dir not found: {image_dir}")

    sc_adata = read_adata(sc_adata_path)
    if annotation_key not in sc_adata.obs.columns:
        raise KeyError(
            f"annotation_key='{annotation_key}' not found in sc.obs. "
            f"Available keys include: {list(sc_adata.obs.columns)[:50]}"
        )

    sc_adata = maybe_map_cell_types(sc_adata, annotation_key=annotation_key)
    lr_data = read_csv(lr_csv_path)

    anchor_expression = None
    if anchor_expression_path:
        anchor_expression = read_adata(anchor_expression_path)

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
    p = argparse.ArgumentParser(description="Run Cytobulk H&E mapping for HE_mapping_CID867")

    p.add_argument(
        "--enable_cropping",
        type=int,
        default=0,
        choices=[0, 1],
        help="Whether to crop tiles from SVS when --svs_path is provided. default: 0 (False)",
    )
    p.add_argument(
        "--svs_path",
        default="",
        help="Path to .svs. If provided, ct.pp.process_svs_image will be run.",
    )
    p.add_argument(
        "--image_out_dir",
        default="",
        help="Output dir for ct.pp.process_svs_image (required if --svs_path is set).",
    )

    p.add_argument("--crop_size", type=int, default=224)
    p.add_argument("--magnification", type=int, default=1)
    p.add_argument("--center_x", type=int, default=4000)
    p.add_argument("--center_y", type=int, default=9000)
    p.add_argument("--fold_width", type=int, default=10)
    p.add_argument("--fold_height", type=int, default=10)

    p.add_argument("--image_dir", default="", help="Directory containing processed image tiles")

    p.add_argument("--sc", required=True, help="Path to scRNA AnnData (.h5ad)")
    p.add_argument("--lr_csv", required=True, help="Path to ligand-receptor pairs CSV")
    p.add_argument("--annotation_key", default="cell_type", help="Cell type key in sc_adata.obs")

    p.add_argument("--out_dir", required=True, help="Output directory")
    p.add_argument("--project", default="demo", help="Project name tag")

    p.add_argument("--k_neighbor", type=int, default=30)

    p.add_argument(
        "--alpha",
        type=str,
        default="auto_compute",
        help='Alpha for mapping. Use "auto_compute" (default) or a float value like 0.5.',
    )
    p.add_argument("--batch_size", type=int, default=15000)

    p.add_argument("--mapping_sc", type=int, default=1, choices=[0, 1], help="default: 1 (True)")
    p.add_argument("--return_adata", type=int, default=1, choices=[0, 1], help="default: 1 (True)")

    p.add_argument(
        "--sc_st",
        type=parse_bool,
        default=True,
        help="Whether to enable sc_st mode. default: true",
    )
    p.add_argument(
        "--anchor_expression",
        required=True,
        help="Path to anchor expression AnnData (.h5ad), e.g. input/5/*.h5ad",
    )
    p.add_argument("--expression_weight", type=float, default=0.5, help="default: 0.5")
    p.add_argument("--skip_filtering", type=parse_bool, default=True, help="default: true")

    p.add_argument(
        "--combinded_cent",
        default="",
        help=(
            "Optional explicit path to combinded_cent.txt. "
            "If not provided, script will try to auto-find it under the input directory."
        ),
    )

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
        combinded_cent_path=args.combinded_cent,
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
