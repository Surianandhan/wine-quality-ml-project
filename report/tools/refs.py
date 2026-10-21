"""
refs.py -- the bibliography shared by the report and the paper (APA 7 style).

Every DOI below was checked against Crossref / DataCite. Entries are kept in
alphabetical order; a document numbers only the entries it cites, in this order.
Each entry is a list of (text, italic) pieces followed by an optional link.
"""

REFS = {
    "bhardwaj2022": ([("Bhardwaj, P., Tiwari, P., Olejar, K., Parr, W., & Kulasiri, D. (2022). A machine learning application in wine quality prediction. ", False),
                      ("Machine Learning with Applications, 8", True), (", 100261.", False)],
                     "https://doi.org/10.1016/j.mlwa.2022.100261"),
    "breiman2001": ([("Breiman, L. (2001). Random forests. ", False), ("Machine Learning, 45", True), ("(1), 5–32.", False)],
                    "https://doi.org/10.1023/A:1010933404324"),
    "chawla2002": ([("Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. ", False),
                    ("Journal of Artificial Intelligence Research, 16", True), (", 321–357.", False)],
                   "https://doi.org/10.1613/jair.953"),
    "cortes1995": ([("Cortes, C., & Vapnik, V. (1995). Support-vector networks. ", False), ("Machine Learning, 20", True), ("(3), 273–297.", False)],
                   "https://doi.org/10.1007/BF00994018"),
    "cortez2009": ([("Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). Modeling wine preferences by data mining from physicochemical properties. ", False),
                    ("Decision Support Systems, 47", True), ("(4), 547–553.", False)],
                   "https://doi.org/10.1016/j.dss.2009.05.016"),
    "cortez2009data": ([("Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). ", False), ("Wine Quality", True),
                        (" [Dataset]. UCI Machine Learning Repository.", False)],
                       "https://doi.org/10.24432/C56S3T"),
    "dahal2021": ([("Dahal, K. R., Dahal, J. N., Banjade, H., & Gaire, S. (2021). Prediction of wine quality using machine learning algorithms. ", False),
                   ("Open Journal of Statistics, 11", True), ("(2), 278–289.", False)],
                  "https://doi.org/10.4236/ojs.2021.112015"),
    "demsar2006": ([("Demšar, J. (2006). Statistical comparisons of classifiers over multiple data sets. ", False),
                    ("Journal of Machine Learning Research, 7", True), (", 1–30.", False)],
                   "https://jmlr.org/papers/v7/demsar06a.html"),
    "dietterich2000": ([("Dietterich, T. G. (2000). Ensemble methods in machine learning. In ", False),
                        ("Multiple Classifier Systems (MCS 2000), Lecture Notes in Computer Science, Vol. 1857", True),
                        (" (pp. 1–15). Springer.", False)],
                       "https://doi.org/10.1007/3-540-45014-9_1"),
    "fisher2019": ([("Fisher, A., Rudin, C., & Dominici, F. (2019). All models are wrong, but many are useful: Learning a variable's importance by studying an entire class of prediction models simultaneously. ", False),
                    ("Journal of Machine Learning Research, 20", True), ("(177), 1–81.", False)],
                   "https://jmlr.org/papers/v20/18-760.html"),
    "friedman2001": ([("Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. ", False),
                      ("The Annals of Statistics, 29", True), ("(5), 1189–1232.", False)],
                     "https://doi.org/10.1214/aos/1013203451"),
    "geurts2006": ([("Geurts, P., Ernst, D., & Wehenkel, L. (2006). Extremely randomized trees. ", False), ("Machine Learning, 63", True), ("(1), 3–42.", False)],
                   "https://doi.org/10.1007/s10994-006-6226-1"),
    "gupta2018": ([("Gupta, Y. (2018). Selection of important features and predicting wine quality using machine learning techniques. ", False),
                   ("Procedia Computer Science, 125", True), (", 305–312.", False)],
                  "https://doi.org/10.1016/j.procs.2017.12.041"),
    "harris2020": ([("Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., Cournapeau, D., ... Oliphant, T. E. (2020). Array programming with NumPy. ", False),
                    ("Nature, 585", True), ("(7825), 357–362.", False)],
                   "https://doi.org/10.1038/s41586-020-2649-2"),
    "he2009": ([("He, H., & Garcia, E. A. (2009). Learning from imbalanced data. ", False),
                ("IEEE Transactions on Knowledge and Data Engineering, 21", True), ("(9), 1263–1284.", False)],
               "https://doi.org/10.1109/TKDE.2008.239"),
    "huang2006": ([("Huang, G.-B., Zhu, Q.-Y., & Siew, C.-K. (2006). Extreme learning machine: Theory and applications. ", False),
                   ("Neurocomputing, 70", True), ("(1–3), 489–501.", False)],
                  "https://doi.org/10.1016/j.neucom.2005.12.126"),
    "hunter2007": ([("Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. ", False),
                    ("Computing in Science & Engineering, 9", True), ("(3), 90–95.", False)],
                   "https://doi.org/10.1109/MCSE.2007.55"),
    "ke2017": ([("Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T.-Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. In ", False),
                ("Advances in Neural Information Processing Systems 30", True), (" (pp. 3146–3154). Curran Associates.", False)],
               None),
    "kuncheva2003": ([("Kuncheva, L. I., & Whitaker, C. J. (2003). Measures of diversity in classifier ensembles and their relationship with the ensemble accuracy. ", False),
                      ("Machine Learning, 51", True), ("(2), 181–207.", False)],
                     "https://doi.org/10.1023/A:1022859003006"),
    "lemaitre2017": ([("Lemaître, G., Nogueira, F., & Aridas, C. K. (2017). Imbalanced-learn: A Python toolbox to tackle the curse of imbalanced datasets in machine learning. ", False),
                      ("Journal of Machine Learning Research, 18", True), ("(17), 1–5.", False)],
                     "https://jmlr.org/papers/v18/16-365.html"),
    "ma2024": ([("Ma, R., Mao, D., Cao, D., Luo, S., Gupta, S., & Wang, Y. (2024). From vineyard to table: Uncovering wine quality for sales management through machine learning. ", False),
                ("Journal of Business Research, 176", True), (", 114576.", False)],
               "https://doi.org/10.1016/j.jbusres.2024.114576"),
    "mckinney2010": ([("McKinney, W. (2010). Data structures for statistical computing in Python. In ", False),
                      ("Proceedings of the 9th Python in Science Conference", True), (" (pp. 56–61).", False)],
                     "https://doi.org/10.25080/Majora-92bf1922-00a"),
    "nadeau2003": ([("Nadeau, C., & Bengio, Y. (2003). Inference for the generalization error. ", False), ("Machine Learning, 52", True), ("(3), 239–281.", False)],
                   "https://doi.org/10.1023/A:1024068626366"),
    "pedregosa2011": ([("Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., ... Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. ", False),
                       ("Journal of Machine Learning Research, 12", True), (", 2825–2830.", False)],
                      "https://jmlr.org/papers/v12/pedregosa11a.html"),
    "rumelhart1986": ([("Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). Learning representations by back-propagating errors. ", False),
                       ("Nature, 323", True), ("(6088), 533–536.", False)],
                      "https://doi.org/10.1038/323533a0"),
    "sokolova2009": ([("Sokolova, M., & Lapalme, G. (2009). A systematic analysis of performance measures for classification tasks. ", False),
                      ("Information Processing & Management, 45", True), ("(4), 427–437.", False)],
                     "https://doi.org/10.1016/j.ipm.2009.03.002"),
    "streamlit2026": ([("Streamlit Inc. (2026). ", False), ("Streamlit", True), (" (Version 1.66.0) [Computer software].", False)],
                      "https://streamlit.io"),
    "strobl2007": ([("Strobl, C., Boulesteix, A.-L., Zeileis, A., & Hothorn, T. (2007). Bias in random forest variable importance measures: Illustrations, sources and a solution. ", False),
                    ("BMC Bioinformatics, 8", True), (", 25.", False)],
                   "https://doi.org/10.1186/1471-2105-8-25"),
    "vanderplas2018": ([("VanderPlas, J., Granger, B., Heer, J., Moritz, D., Wongsuphasawat, K., Satyanarayan, A., Lees, E., Timofeev, I., Welsh, B., & Sievert, S. (2018). Altair: Interactive statistical visualizations for Python. ", False),
                        ("Journal of Open Source Software, 3", True), ("(32), 1057.", False)],
                       "https://doi.org/10.21105/joss.01057"),
    "virtanen2020": ([("Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., ... van Mulbregt, P. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. ", False),
                      ("Nature Methods, 17", True), ("(3), 261–272.", False)],
                     "https://doi.org/10.1038/s41592-019-0686-2"),
    "wilcoxon1945": ([("Wilcoxon, F. (1945). Individual comparisons by ranking methods. ", False), ("Biometrics Bulletin, 1", True), ("(6), 80–83.", False)],
                     "https://doi.org/10.2307/3001968"),
    "wolpert1992": ([("Wolpert, D. H. (1992). Stacked generalization. ", False), ("Neural Networks, 5", True), ("(2), 241–259.", False)],
                    "https://doi.org/10.1016/S0893-6080(05)80023-1"),
    "zhou2012": ([("Zhou, Z.-H. (2012). ", False), ("Ensemble methods: Foundations and algorithms", True), (". Chapman & Hall/CRC.", False)],
                 "https://doi.org/10.1201/b12207"),
}
ORDER = list(REFS)


class Citations:
    """Numbers references in alphabetical order over the keys a document uses."""

    def __init__(self, used):
        self.keys = [k for k in ORDER if k in used]
        self.num = {k: i + 1 for i, k in enumerate(self.keys)}

    def __call__(self, *keys):
        return ", ".join(f"[{n}]" for n in sorted(self.num.get(k, 0) for k in keys))
