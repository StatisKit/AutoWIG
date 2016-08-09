import os
import unittest
import tempfile
import shutil
import hashlib

from autowig import autowig

class TestSimple(unittest.TestCase):
    """Test the wrapping of a simple library"""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp(dir='.')
        with open(os.path.join(cls.directory, 'binomial.h'), 'w') as filehandler:
            filehandler.write(r"""#include <exception>

class ProbabilityError : public std::exception
{
    /// \brief Compute the exception content
    /// \returns The message "a probability must be in the interval [0,1]"
    virtual const char* what() const noexcept; 
};

class BinomialDistribution
{
  public:
    BinomialDistribution(const unsigned int n, const double pi);
    BinomialDistribution(const BinomialDistribution& binomial);
    
    double pmf(const unsigned int value) const;
        
    double get_pi() const;
    
    /** 
     * \param pi New probability value
     * \throws \ref ::ProbabilityError If the new probability value is not 
     *         in the interval \f$\left[0,1\right]\f$ */
    void set_pi(const double pi);
   
    unsigned int n;
    
  protected:
    double _pi;

  private:
     unsigned int factorial(const unsigned int value) const;
};""")
        
        with open(os.path.join(cls.directory, 'binomial.cpp'), 'w') as filehandler:
            filehandler.write(r"""#include "binomial.h"
#include <cmath>

const char * ProbabilityError::what() const noexcept
{ return "a probability must be in the interval [0,1]"; }

BinomialDistribution::BinomialDistribution(const unsigned int n, const double pi)
{ 
    this->n = n;
    set_pi(pi);
}

BinomialDistribution::BinomialDistribution(const BinomialDistribution& binomial)
{
    n = binomial.n;
    _pi = binomial._pi;
}

double BinomialDistribution::pmf(const unsigned int value) const
{
    double p;
    if(value > n)
    { p = 0; }
    else
    { p = factorial(n)/(factorial(n-value) * factorial(value)) * pow(1-p, n-value) * pow(p, value); }
    return p;
}

double BinomialDistribution::get_pi() const
{ return _pi; }

void BinomialDistribution::set_pi(const double pi)
{
    if(pi < 0. || pi > 1.)
    { throw ProbabilityError(); }
    _pi = pi;
}

unsigned int BinomialDistribution::factorial(const unsigned int n) const
{ return (n == 1 || n == 0) ? 1 : factorial(n - 1) * n; }""")

        #subprocess.call(['gcc', '-o', os.path.join(cls.directory, 'binomial.os'), '-c', '-x', 'c++',
        #     '-std=c++0x', '-Wwrite-strings', '-fPIC', os.path.join(cls.directory, 'binomial.cpp')])

        cls.md5sum = 'f3282d4f035092d5b9c546905c6f2525'
        #cls.md5sum = '4233d6bbd7f38ac7a17141f219388468'

    def test_wrappers(self):
        asg = autowig.AbstractSemanticGraph()
        autowig.parser.plugin = 'pyclanglite'
        autowig.parser(asg, [os.path.join(self.directory, 'binomial.h')], ['-x', 'c++', '-std=c++11', '-I' + os.path.abspath(self.directory)])

        autowig.controller.plugin = 'default'
        autowig.controller(asg)

        autowig.generator.plugin = 'boost_python_internal'
        wrappers = autowig.generator(asg, module=os.path.join(self.directory, 'module.cpp'),
                        decorator=None,
                        prefix='wrapper_')

        wrappers = sorted(wrappers, key=lambda wrapper: wrapper.globalname)
        md5sum = hashlib.md5()
        for wrapper in wrappers:
            md5sum.update(wrapper.content)
        md5sum = md5sum.hexdigest()
        self.assertEqual(md5sum, self.md5sum)

    @classmethod
    def tearDownClass(cls):
        pass
        #shutil.rmtree(cls.directory)
