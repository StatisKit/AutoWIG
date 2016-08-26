set -v
rm environment.yml
conda create -n sphinx-autowig python
source activate sphinx-autowig
bash ../conda/install.sh
conda install python-clanglite -c statiskit
conda install jupyter>=1.0.0
conda install sphinx>=1.4.6
pip install phinxcontrib-bibtex
pip install nbsphinx
conda env export > environment.yml
source deactivate sphinx-autowig
conda env remove -n sphinx-autowig