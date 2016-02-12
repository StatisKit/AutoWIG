#include <boost/python.hpp>

void _binomial_distribution();
void _probability_error();

BOOST_PYTHON_MODULE(__binomial)
{
    _binomial_distribution();
    _probability_error();
}