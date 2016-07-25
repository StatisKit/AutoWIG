#include "binomial.h"
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

double BinomialDistribution::pmf(const unsigned int value) const
{
    double p;
    if(value > n)
    { p = 0; }
    else
    { p = exp(std::lgamma(n + 1) - std::lgamma(n - value + 1) - std::lgamma(value + 1) + (n - value) * log(1 - _pi) + value * log(_pi)); }
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
