#include "functions.h"

double addition (const double& a, const double& b)
{
  double r;
  r = a + b;
  return r;
}

void duplicate(double& a)
{ a *= 2.; }

double divide(const double& a, const double& b)
{
  double r;
  r = a / b;
  return r;
}

int operate(int a, int b)
{ return a * b; }

double operate(double a, double b)
{ return a / b; }
