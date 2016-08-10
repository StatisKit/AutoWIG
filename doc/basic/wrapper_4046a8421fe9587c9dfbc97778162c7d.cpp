#include <type_traits>
#include <boost/python.hpp>
#include <binomial.h>

namespace autowig { template<class T> using HeldType = std::shared_ptr< T >; }

namespace autowig
{
}


void wrapper_4046a8421fe9587c9dfbc97778162c7d()
{

    double  (::BinomialDistribution::*method_pointer_3a3ff64f25e358a6a10b1cd3b3425b82)(unsigned int  const) const = &::BinomialDistribution::pmf;
    double  (::BinomialDistribution::*method_pointer_3c97a500c9575c259d5cbdd76120ff4f)() const = &::BinomialDistribution::get_pi;
    void  (::BinomialDistribution::*method_pointer_d364a0529e33516f8ecbb7dcedd60aa0)(double  const) = &::BinomialDistribution::set_pi;
    boost::python::class_< class ::BinomialDistribution, autowig::HeldType< class ::BinomialDistribution > > class_4046a8421fe9587c9dfbc97778162c7d("BinomialDistribution", "", boost::python::no_init);
    class_4046a8421fe9587c9dfbc97778162c7d.def("pmf", method_pointer_3a3ff64f25e358a6a10b1cd3b3425b82, "");
    class_4046a8421fe9587c9dfbc97778162c7d.def("get_pi", method_pointer_3c97a500c9575c259d5cbdd76120ff4f, "");
    class_4046a8421fe9587c9dfbc97778162c7d.def("set_pi", method_pointer_d364a0529e33516f8ecbb7dcedd60aa0, ":Parameter:\n    `pi` (:cpp:any:`double`) - New probability value\n\n:Return Type:\n    :cpp:any:`void`\n\n:Raises:\n    :cpp:any:`\\ref` - ::ProbabilityError If the new probability value is not in the interval\n                      :math:`\\left[0,1\\right]`\n\n");
    class_4046a8421fe9587c9dfbc97778162c7d.def_readwrite("n", &::BinomialDistribution::n, "");

}