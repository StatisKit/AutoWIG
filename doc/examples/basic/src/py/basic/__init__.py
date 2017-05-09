##################################################################################
#                                                                                #
# AutoWIG: Automatic Wrapper and Interface Generator                             #
#                                                                                #
# Homepage: http://autowig.readthedocs.io                                        #
#                                                                                #
# Copyright (c) 2016 Pierre Fernique                                             #
#                                                                                #
# This software is distributed under the CeCILL license. You should have       #
# received a copy of the legalcode along with this work. If not, see             #
# <http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html>.                 #
#                                                                                #
# File authors: Pierre Fernique <pfernique@gmail.com> (6)                        #
#                                                                                #
##################################################################################

from __basic import BinomialDistribution, Overload

def _repr_latex_(self):
    return r"$\mathcal{B}\left(" + str(self.n) + ", " + str(round(self.get_pi(), 2)) + r"\right)$"

BinomialDistribution._repr_latex_ = _repr_latex_
del _repr_latex_
