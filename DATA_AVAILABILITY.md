# Data availability

This repository does not redistribute raw third party datasets.

The experiments use the following public sources:

1. CICIoT2023 public subsample mirror:
   https://huggingface.co/datasets/lacg030175/CIC-IoT-2023-neto-subsample
2. Original CICIoT2023 project page:
   https://www.unb.ca/cic/datasets/iotdataset-2023.html
3. IoTID20 preprocessed file mirror:
   https://huggingface.co/datasets/KathiS/IoTID20_Preprocessed_File
4. N BaIoT UCI archive:
   https://archive.ics.uci.edu/dataset/442/detection+of+iot+botnet+attacks+n+baiot

Use `scripts/download_datasets.py` to retrieve the public files. Downloaded files are written to `data/raw/`, which is ignored by git.
