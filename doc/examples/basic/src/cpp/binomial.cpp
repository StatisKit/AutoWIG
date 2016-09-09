/**********************************************************************************/
/*                                                                                */
/* AutoWIG: Automatic Wrapper and Interface Generator                             */
/*                                                                                */
/* Homepage: http://autowig.readthedocs.io                                        */
/*                                                                                */
/* Copyright (c) 2016 Pierre Fernique                                             */
/*                                                                                */
/* This software is distributed under the CeCILL-C license. You should have       */
/* received a copy of the legalcode along with this work. If not, see             */
/* <http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html>.                 */
/*                                                                                */
/* File authors: Pierre Fernique <pfernique@gmail.com> (4)                        */
/*                                                                                */
/**********************************************************************************/

#include <basic/binomial.h>
#include <cmath>

const char * ProbabilityError::what() const noexcept
{ return "a probability must be in the interval [0,1]"; }

BinomialDistribution::BinomialDistribution(const unsigned int n, const double pi)
{ 
    this->n = n;
    set_pi(pi);
}

BinomialDistribution::BinomialDistribution(const BinomialDistribution& binomial)
{
    n = binomial.n;
    _pi = binomial._pi;
}

BinomialDistribution::~BinomialDistribution()
{}

double BinomialDistribution::pmf(const unsigned int value) const
{
    double p;
    if(value > n)
    { p = 0; }
    else
    { p = factorial(n)/(factorial(n-value) * factorial(value)) * pow(1-_pi, n-value) * pow(_pi, value); }
    return p;
}

double BinomialDistribution::get_pi() const
{ return _pi; }

void BinomialDistribution::set_pi(const double pi)
{
    if(pi < 0. || pi > 1.)
    { throw ProbabilityError(); }
    _pi = pi;
}

unsigned int BinomialDistribution::factorial(const unsigned int n) const
{ return (n == 1 || n == 0) ? 1 : factorial(n - 1) * n; }