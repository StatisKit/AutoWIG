#ifndef TYPE_H
#define TYPE_H

#include <string>

/** First text
 * 
 * Second text
 */

namespace namespace_a
{
    int variable;

    namespace namespace_b
    {
        class Class;

        namespace namespace_c 
        {
            enum enum_type {
                ENUM_A,
                ENUM_B
            };
        }

    }

    typedef namespace_b::namespace_c::enum_type enum_type; 

    int& function(const int& a);

    struct Struct
    {
        Struct();
        virtual ~Struct();
        Struct(const Struct& s);

        virtual double virtual_function(const enum_type& enum_value) const = 0;
    };

    class BaseClass : public Struct
    {
        public:
            BaseClass();
    };
}

namespace namespace_b
{
    class DerivedClass : public namespace_a::BaseClass
    {
        int field;

        public:
            virtual double virtual_function(const namespace_a::enum_type& enum_value) const;
    };
}

#include <vector>
#include <eigen2/Eigen/Dense>
#endif
