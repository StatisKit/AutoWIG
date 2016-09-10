/**********************************************************************************/
/*                                                                                */
/* AutoWIG: Automatic Wrapper and Interface Generator                             */
/*                                                                                */
/* Homepage: http://autowig.readthedocs.io                                        */
/*                                                                                */
/* Copyright (c) 2016 Pierre Fernique                                             */
/*                                                                                */
/* This software is distributed under the CeCILL-C license. You should have       */
/* received a copy of the legalcode along with this work. If not, see             */
/* <http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html>.                 */
/*                                                                                */
/* File authors: Pierre Fernique <pfernique@gmail.com> (2)                        */
/*                                                                                */
/**********************************************************************************/

#include <iostream>
#include <basic/overload.h>

Overload::Overload()
{}
 
void Overload::staticness()
{ std::cout << "static" << std::endl; }

void Overload::staticness(const unsigned int value)
{ std::cout << "static" << std::endl; }

void Overload::staticness(const Overload& overload, const unsigned int value)
{ std::cout << "non-static" << std::endl; }

void Overload::constness()
{ std::cout << "non-const" << std::endl; }

void Overload::constness() const
{ std::cout << "const" << std::endl; }

void Overload::nonconstness() const
{ std::cout << "const" << std::endl; }

void Overload::nonconstness()
{ std::cout << "non-const" << std::endl; }