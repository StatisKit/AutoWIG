#include "overload.h"
#include <iostream>

Staticness::Staticness()
{}

void Staticness::staticness()
{ std::cout << "non-static" << std::endl; }

void Staticness::staticness(const unsigned int value)
{ std::cout << "non-static" << std::endl; }
    
void Staticness::staticness(const Staticness& staticness, const unsigned int value)
{ std::cout << "static" << std::endl; }

Constness::Constness()
{}

void Constness::constness()
{ std::cout << "non-const" << std::endl; }

void Constness::constness() const
{ std::cout << "const" << std::endl; };

NonConstness::NonConstness()
{}

void NonConstness::constness()
{ std::cout << "non-const" << std::endl; }

void NonConstness::constness() const
{ std::cout << "const" << std::endl; };
