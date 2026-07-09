# N-BaIoT Unseen Device Validation Design

## Role

N-BaIoT is used for the independent unseen-device validation route. The validation simulates deployment on an IoT device absent from training.

## Data

- Rows used in this run: 3,967,570
- Per-file row cap: 50000
- Devices: 9
- Attack labels: 9
- Numeric features: 115

## Split

Leave-one-device-out. For each fold, one device is held out entirely for testing and all other devices form the training set.

## Claim Control

This is stronger than a random split because device identity is held out. If per-file caps are used, results are quick-stage evidence and should be confirmed with a larger cap before final manuscript claims.
