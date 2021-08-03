# Project overview

This is intended to be a small code repository to supplement the paper "An Algorithm for the Separation-Preserving Transition of Clusterings."

This project includes a collection of small examples that will demonstrate the algorithms described in the paper. The provided jupyter notebooks
contain the algorithms described in the paper.

All Linear programs are contained in the relevant jupyter notebook, but most linear programming output is suppressed by default.
## Included files

Full Run.ipynb - This Jupyter notebook will do all the steps described in the paper on a given data set.

LSA2Radial.ipynb - This script focuses solely on Algorithm 2 described in the paper.

Radial2Radial.ipynb - This Jupyter notebook performs Algorithm 3 described in the paper.

TTHelperFuncts.py - this python script contains all the helper functions that the algorithms rely on. It is shared across all the scripts to reduce how big all the Jupyter Notebooks are and allow the focus to be more on the paper's contents.


## Technical requirements
This project relies on the gurobi LP solver, and prototyping is done using Jupyter notebooks.

gurobi installation instructions can be found here:

https://www.gurobi.com/resource/starting-with-gurobi/

anaconda installation comes with jupyter notebooks and installation instructions can be found here:

https://www.anaconda.com/distribution


