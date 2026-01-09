#!/usr/bin/env bash

# Script to download hERG cardiotoxicity datasets
# Sources: CardioTox and hERG-QSAR GitHub repositories
# Contains hERG channel blocker/non-blocker classifications with SMILES

set -euo pipefail

localpath=$(pwd)
downloadpath="$localpath/download"

mkdir -p "$downloadpath"

echo "Downloading hERG cardiotoxicity datasets..."

# hERG-QSAR dataset from ChEMBL (curated)
echo "Downloading hERG-QSAR datasets..."
wget -nv -O "$downloadpath/Training_Set.csv" \
    "https://raw.githubusercontent.com/PDelre93/hERG-QSAR/main/Training_Set.csv" || \
    echo "Warning: Could not download Training_Set.csv"

wget -nv -O "$downloadpath/Validation_Set.csv" \
    "https://raw.githubusercontent.com/PDelre93/hERG-QSAR/main/Validation_Set.csv" || \
    echo "Warning: Could not download Validation_Set.csv"

wget -nv -O "$downloadpath/External_set.csv" \
    "https://raw.githubusercontent.com/PDelre93/hERG-QSAR/main/External_set.csv" || \
    echo "Warning: Could not download External_set.csv"

# CardioTox dataset (larger, from BindingDB and ChEMBL)
echo "Downloading CardioTox dataset..."
wget -nv -O "$downloadpath/cardiotox_data.tar.xz" \
    "https://github.com/Abdulk084/CardioTox/raw/master/data/train_validation_cardio_tox_data.tar.xz" || \
    echo "Warning: Could not download CardioTox data"

# Extract CardioTox data
if [[ -f "$downloadpath/cardiotox_data.tar.xz" ]]; then
    echo "Extracting CardioTox data..."
    cd "$downloadpath"
    tar -xf cardiotox_data.tar.xz || echo "Warning: Could not extract CardioTox data"
    cd "$localpath"
fi

echo "Download complete."
ls -lh "$downloadpath"
