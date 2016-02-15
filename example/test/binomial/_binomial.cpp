#include <boost/python.hpp>

void _std_exception();
void _binomial_distribution();
void _probability_error();

BOOST_PYTHON_MODULE(_binomial)
{
    _std_exception();
    _binomial_distribution();
    _probability_error();
}