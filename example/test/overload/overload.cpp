#include "foo.h"
#include <iostream>

Overload::Overload()
{}

void Overload::staticness()
{ std::cout << "non-static" << std::endl; }

void Overload::staticness(const unsigned int value)
{ std::cout << "non-static" << std::endl; }
    
void Overload::staticness(const Overload& overload, const unsigned int value)
{ std::cout << "static" << std::endl; }

void Overload::constness()
{ std::cout << "non-const" << std::endl; }

void Overload::constness() const
{ std::cout << "const" << std::endl; };

void Overload::nonconstness()
{ std::cout << "non-const" << std::endl; }

void Overload::nonconstness() const
{ std::cout << "const" << std::endl; };
