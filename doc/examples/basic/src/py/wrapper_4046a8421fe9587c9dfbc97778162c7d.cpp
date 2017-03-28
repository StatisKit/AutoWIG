#include "_basic.h"



namespace autowig
{

}

#if defined(_MSC_VER)
    #if (_MSC_VER == 1900)
namespace boost
{
    template <> class ::BinomialDistribution const volatile * get_pointer<class ::BinomialDistribution const volatile >(class ::BinomialDistribution const volatile *c) { return c; }
}
    #endif
#endif



void wrapper_4046a8421fe9587c9dfbc97778162c7d()
{

    double  (::BinomialDistribution::*method_pointer_3a3ff64f25e358a6a10b1cd3b3425b82)(unsigned int const) const = &::BinomialDistribution::pmf;
    double  (::BinomialDistribution::*method_pointer_3c97a500c9575c259d5cbdd76120ff4f)() const = &::BinomialDistribution::get_pi;
    void  (::BinomialDistribution::*method_pointer_d364a0529e33516f8ecbb7dcedd60aa0)(double const) = &::BinomialDistribution::set_pi;
    boost::python::class_< class ::BinomialDistribution, autowig::Held< class ::BinomialDistribution >::Type > class_4046a8421fe9587c9dfbc97778162c7d("BinomialDistribution", "", boost::python::no_init);
    class_4046a8421fe9587c9dfbc97778162c7d.def(boost::python::init< unsigned int const, double const >(""));
    class_4046a8421fe9587c9dfbc97778162c7d.def(boost::python::init< class ::BinomialDistribution const & >(""));
    class_4046a8421fe9587c9dfbc97778162c7d.def("pmf", method_pointer_3a3ff64f25e358a6a10b1cd3b3425b82, "Compute the probability of a value\n\nThe probability is given by the flowwing formula\n:cite:`{JKK96}`\n\n:Parameter:\n    `value` (:cpp:any:`unsigned` int) - Undocumented\n\n:Returns:\n    The probability\n\n:Return Type:\n    :cpp:any:`double`\n\n");
    class_4046a8421fe9587c9dfbc97778162c7d.def("get_pi", method_pointer_3c97a500c9575c259d5cbdd76120ff4f, "");
    class_4046a8421fe9587c9dfbc97778162c7d.def("set_pi", method_pointer_d364a0529e33516f8ecbb7dcedd60aa0, ":Parameter:\n    `pi` (:cpp:any:`double`) - New probability value\n\n:Return Type:\n    :cpp:any:`void`\n\n:Raises:\n    :cpp:any:`\\ref` - ::ProbabilityError If the new probability value is not in the interval\n                      :math:`\\left[0,1\\right]`\n\n.. warning::\n\n    The probability value must be in the interval :math:`\\left[0,1\\right]`\n\n");
    class_4046a8421fe9587c9dfbc97778162c7d.def_readwrite("n", &::BinomialDistribution::n, "");

}