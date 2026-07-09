# Reference and Venue Audit

Checked on 2026-06-30.

## Venue Requirements

| Venue | Verified source | Manuscript consequence |
|---|---|---|
| Scientific Reports | https://www.nature.com/srep/author-instructions/submission-guidelines | Keep the title within 20 words, abstract within 200 words, and main text within about 4,500 words excluding Methods, references, and figure legends. Use the order Introduction, Results, Discussion, Methods. |
| PLOS ONE | https://journals.plos.org/plosone/s/submission-guidelines and https://journals.plos.org/plosone/s/getting-started | Initial submission is format-flexible, with no fixed length limit, but data availability and reproducibility statements must be explicit. |
| Nature Portfolio data policy | https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards | Data availability must specify how the minimum dataset supporting the findings can be accessed. |

## Dataset and Method References

| Ref. | Use in manuscript | Verified bibliographic form | DOI or stable URL | Source used for audit |
|---|---|---|---|---|
| CICIoT2023 | Main dataset provenance | Neto, E. C. P., Dadkhah, S., Ferreira, R., Zohourian, A., Lu, R. & Ghorbani, A. A. CICIoT2023: A real-time dataset and benchmark for large-scale attacks in IoT environment. Sensors 23, 5941 (2023). | https://doi.org/10.3390/s23135941 | https://www.mdpi.com/1424-8220/23/13/5941; https://www.unb.ca/cic/datasets/iotdataset-2023.html |
| CICIoT2023 public mirror | Exact local data asset | Hugging Face mirror: lacg030175/CIC-IoT-2023-neto-subsample. | https://huggingface.co/datasets/lacg030175/CIC-IoT-2023-neto-subsample | Local download ledger and dataset URL |
| IoTID20 | Independent dataset provenance | Ullah, I. & Mahmoud, Q. H. A scheme for generating a dataset for anomalous activity detection in IoT networks. In Advances in Artificial Intelligence, Canadian AI 2020, Lecture Notes in Computer Science 12109, 508-520 (Springer, 2020). | https://doi.org/10.1007/978-3-030-47358-7_52 | https://sites.google.com/view/iot-network-intrusion-dataset/home; https://link.springer.com/chapter/10.1007/978-3-030-47358-7_52 |
| IoTID20 public mirror | Exact local data asset | Hugging Face mirror: KathiS/IoTID20_Preprocessed_File. | https://huggingface.co/datasets/KathiS/IoTID20_Preprocessed_File | Local download ledger and dataset URL |
| N-BaIoT | Unseen-device validation dataset | Meidan, Y. et al. N-BaIoT: Network-based detection of IoT botnet attacks using deep autoencoders. IEEE Pervasive Computing 17, 12-22 (2018). | https://doi.org/10.1109/MPRV.2018.03367731 | https://archive.ics.uci.edu/dataset/442/detection+of+iot+botnet+attacks+n+baiot |
| LightGBM | Gradient boosting baseline | Ke, G. et al. LightGBM: A highly efficient gradient boosting decision tree. Advances in Neural Information Processing Systems 30 (2017). | https://papers.nips.cc/paper/6907-lightgbm-a-highly-efficient-gradient-boosting-decision-tree | NeurIPS proceedings and Microsoft Research publication page |
| XGBoost | Complementary weighted model | Chen, T. & Guestrin, C. XGBoost: A scalable tree boosting system. Proceedings of KDD 2016, 785-794 (2016). | https://doi.org/10.1145/2939672.2939785 | https://dl.acm.org/doi/10.1145/2939672.2939785 |
| SMOTE | Oversampling baseline | Chawla, N. V., Bowyer, K. W., Hall, L. O. & Kegelmeyer, W. P. SMOTE: Synthetic minority over-sampling technique. Journal of Artificial Intelligence Research 16, 321-357 (2002). | https://doi.org/10.1613/jair.953 | https://www.jair.org/index.php/jair/article/view/10302 |
| Borderline-SMOTE | Main LightGBM component | Han, H., Wang, W.-Y. & Mao, B.-H. Borderline-SMOTE: A new over-sampling method in imbalanced data sets learning. In Advances in Intelligent Computing, ICIC 2005, Lecture Notes in Computer Science 3644, 878-887 (Springer, 2005). | https://doi.org/10.1007/11538059_91 | https://link.springer.com/chapter/10.1007/11538059_91 |
| SHAP | Explainability method | Lundberg, S. M. & Lee, S.-I. A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems 30 (2017). | https://papers.nips.cc/paper/7062-a-unified-approach-to-interpreting-model-predictions | NeurIPS proceedings |
| scikit-learn | Core machine-learning implementation | Pedregosa, F. et al. Scikit-learn: Machine learning in Python. Journal of Machine Learning Research 12, 2825-2830 (2011). | https://jmlr.org/papers/v12/pedregosa11a.html | JMLR |
| imbalanced-learn | Oversampling and imbalance utilities | Lemaitre, G., Nogueira, F. & Aridas, C. K. Imbalanced-learn: A Python toolbox to tackle the curse of imbalanced datasets in machine learning. Journal of Machine Learning Research 18, 1-5 (2017). | https://jmlr.org/papers/v18/16-365.html | JMLR |

## Citation Controls

- Cite the original CICIoT2023 paper for dataset provenance and separately disclose that experiments used the public Hugging Face subsample mirror.
- Cite IoTID20 through the Springer LNCS chapter and disclose that the local mirror lacked an official split, so a stratified holdout was used.
- Cite N-BaIoT through the IEEE Pervasive Computing paper and the UCI dataset page; state the 20,000-row per-file cap in Methods and limitations.
- Use method citations only for implemented components: LightGBM, XGBoost, SMOTE, Borderline-SMOTE, SHAP, scikit-learn, and imbalanced-learn.
