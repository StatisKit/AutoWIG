/**********************************************************************************/
/*                                                                                */
/* AutoWIG: Automatic Wrapper and Interface Generator                             */
/*                                                                                */
/* Homepage: http://autowig.readthedocs.io                                        */
/*                                                                                */
/* Copyright (c) 2016 Pierre Fernique                                             */
/*                                                                                */
/* This software is distributed under the CeCILL license. You should have       */
/* received a copy of the legalcode along with this work. If not, see             */
/* <http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html>.                 */
/*                                                                                */
/* File authors: Pierre Fernique <pfernique@gmail.com> (2)                        */
/*                                                                                */
/**********************************************************************************/

/**
 * \brief This class is used to illustrate problems that can arise with
 *        overloading
 * \details At this stage mainly static (\ref ::Overload::staticness) 
 *          and const (\ref ::Overload::constness or 
 *          \ref ::Overload::nonconstness) overloading are reported as
 *          problematic.
 * \note The documentation is also used for illustrating the Doxygen to
 *       Sphinx conversions
 * \todo Any problem concerning method overloading should be added in this
 *       class
 * */
struct Overload 
{
    Overload();
 
    /// \brief This method print "static" in the standard C output stream
    void staticness();
    
    /// \brief  This method print "static" in the standard C output stream
    void staticness(const unsigned int value); 

    /// \brief This method print "non-static" in the standard C output
    ///        stream
    static void staticness(const Overload& overload,
                           const unsigned int value);

    /// \brief print "non-const" in the standard C output stream
    void constness();

    /// \brief print "const" in the standard C output stream
    void constness() const;

    /// \brief print "const" in the standard C output stream    
    void nonconstness() const;

    /// \brief print "non-const" in the standard C output stream
    void nonconstness();
};