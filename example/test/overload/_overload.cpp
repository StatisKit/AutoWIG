#include <boost/python.hpp>

void _non_constness();
void _staticness();
void _constness();

BOOST_PYTHON_MODULE(_overload)
{
    _non_constness();
    _staticness();
    _constness();
}