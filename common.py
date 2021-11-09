"""Commonly used functions."""
import os


def map_input_output(in_dir, out_dir):
    """Map input paths to output paths."""
    in_paths, out_paths = [], []
    for subdir in os.listdir(in_dir):
        in_subdir = os.path.join(in_dir, subdir)
        out_subdir = os.path.join(out_dir, subdir)
        if not os.path.exists(out_subdir):
            os.makedirs(out_subdir)
        for fn in os.listdir(in_subdir):
            in_paths.append(os.path.join(in_subdir, fn))
            out_paths.append(os.path.join(out_subdir, fn))
    return in_paths, out_paths
