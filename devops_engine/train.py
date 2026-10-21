"""Convenience script to generate training dataset and train all ML models."""

import os
import sys

_this_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_this_dir) if os.path.basename(_this_dir) == "devops_engine" else _this_dir
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

try:
    from devops_engine.ml.trainer import train_and_evaluate_all
except ImportError:
    from ml.trainer import train_and_evaluate_all

if __name__ == "__main__":
    train_and_evaluate_all()
