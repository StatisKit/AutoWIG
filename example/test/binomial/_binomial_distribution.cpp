#include <boost/python.hpp>
#include <//home/pfernique/Desktop/AutoWIG/example/test/binomial/binomial.h>

void _binomial_distribution()
{

        boost::python::class_< class ::BinomialDistribution, class ::BinomialDistribution* >("BinomialDistribution", boost::python::no_init)
            .def(boost::python::init< unsigned int  const, double  const >())
            .def(boost::python::init< class ::BinomialDistribution  const & >())
            .def("pmf", &::BinomialDistribution::pmf)
            .def("get_pi", &::BinomialDistribution::get_pi)
            .def("set_pi", &::BinomialDistribution::set_pi)
            .def_readwrite("n", &::BinomialDistribution::n);    
}