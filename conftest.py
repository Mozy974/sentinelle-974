"""Configuration pytest — ajoute api/ au PYTHONPATH pour importer le package `app`."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "api"))
