#include "_basi.h"


namespace autowig
{
}


void wrapper_0f744e8d056f5d469a887c7c78eaf8fe()
{

    void  (::Overload::*method_pointer_59d40e318ef55ff886ecbb0040842054)() = &::Overload::staticness;
    void  (::Overload::*method_pointer_464561c46f6f55b9bb8db94776addf78)(unsigned int const) = &::Overload::staticness;
    void  (*method_pointer_fc940302e91057e9b8076d1736fe3442)(struct ::Overload const &, unsigned int const) = ::Overload::staticness;
    void  (::Overload::*method_pointer_e0ea15995a26563fa398def271a7ad20)() = &::Overload::constness;
    void  (::Overload::*method_pointer_fe8b5871f7875476ba7ae9ff39e06a34)() const = &::Overload::constness;
    void  (::Overload::*method_pointer_6e7b492ef965566b9c74f97f969fc435)() const = &::Overload::nonconstness;
    void  (::Overload::*method_pointer_d39edea9dfc1510e9f8e3a470a588785)() = &::Overload::nonconstness;
    boost::python::class_< struct ::Overload, autowig::Held< struct ::Overload >::Type > class_0f744e8d056f5d469a887c7c78eaf8fe("Overload", "This class is used to illustrate problems that can arise with\noverloading\n\nAt this stage mainly static\n(:cpp:func:`::Overload::staticness`) and const\n(:cpp:func:`::Overload::constness` or\n:cpp:func:`::Overload::nonconstness`) overloading are\nreported as problematic.\n\n.. note::\n\n    The documentation is also used for illustrating the Doxygen to Sphinx\n    conversions\n\n.. todo::\n\n    Any problem concerning method overloading should be added in this class\n\n", boost::python::no_init);
    class_0f744e8d056f5d469a887c7c78eaf8fe.def("staticness", method_pointer_59d40e318ef55ff886ecbb0040842054, "This method print 'static' in the standard C output stream\n\n:Return Type:\n    :cpp:any:`void`\n\n");
    class_0f744e8d056f5d469a887c7c78eaf8fe.def("staticness", method_pointer_464561c46f6f55b9bb8db94776addf78, "This method print 'static' in the standard C output stream\n\n:Parameter:\n    `value` (:cpp:any:`unsigned` int) - Undocumented\n\n:Return Type:\n    :cpp:any:`void`\n\n");
    class_0f744e8d056f5d469a887c7c78eaf8fe.def("staticness", method_pointer_fc940302e91057e9b8076d1736fe3442, "This method print 'non-static' in the standard C output stream\n\n:Parameters:\n  - `overload` (:py:class:`basic.Overload`) - Undocumented\n  - `value` (:cpp:any:`unsigned` int) - Undocumented\n\n:Return Type:\n    :cpp:any:`void`\n\n");
    class_0f744e8d056f5d469a887c7c78eaf8fe.def("constness", method_pointer_e0ea15995a26563fa398def271a7ad20, "print 'non-const' in the standard C output stream\n\n:Return Type:\n    :cpp:any:`void`\n\n");
    class_0f744e8d056f5d469a887c7c78eaf8fe.def("constness", method_pointer_fe8b5871f7875476ba7ae9ff39e06a34, "print 'const' in the standard C output stream\n\n:Return Type:\n    :cpp:any:`void`\n\n");
    class_0f744e8d056f5d469a887c7c78eaf8fe.def("nonconstness", method_pointer_6e7b492ef965566b9c74f97f969fc435, "print 'const' in the standard C output stream\n\n:Return Type:\n    :cpp:any:`void`\n\n");
    class_0f744e8d056f5d469a887c7c78eaf8fe.def("nonconstness", method_pointer_d39edea9dfc1510e9f8e3a470a588785, "print 'non-const' in the standard C output stream\n\n:Return Type:\n    :cpp:any:`void`\n\n");
    class_0f744e8d056f5d469a887c7c78eaf8fe.staticmethod("staticness");

}