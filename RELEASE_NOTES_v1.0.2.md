# Release notes v1.0.2

Reproducibility smoke-test maintenance release.

Changes:

- Fixes a reduced-size CICIoT summary-writing edge case where `pr_auc_macro` may be absent from the validation alpha grid when the validation sample has incomplete class coverage.
- Reports the actual feature count in the CICIoT validation alpha grid.
- Adds a clean-extraction reproducibility smoke-test note.

The manuscript result CSV files and reported metrics are unchanged.
