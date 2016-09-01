from __module import BinomialDistribution, Overload, ProbabilityError

def _repr_latex_(self):
    return r"$\mathcal{B}\left(" + str(self.n) + ", " str(round(self.get_pi(), 2)) + r"\right)$"

BinomialDistribution._repr_latex_ = _repr_latex_
del _repr_latex_