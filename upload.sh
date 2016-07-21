set -e

anaconda login

conda build conda/python-autowig -c StatisKit -c salford_systems -c conda-forge;
CONDA_FILE=`conda build conda/python-autowig -c StatisKit --output`;
anaconda upload --force --user StatisKit ${CONDA_FILE%%};