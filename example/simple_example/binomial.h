#include <exception>

class ProbabilityError : public std::exception
{ virtual const char* what() const noexcept; };

class BinomialDistribution
{
  public:
    BinomialDistribution(const unsigned int n, const double pi);
    BinomialDistribution(const BinomialDistribution& binomial);
	
    double pmf(const unsigned int& event) const;
     
    double get_pi() const;
    void set_pi(const double pi);
   
    unsigned int n;
    
  protected:
    double _pi;
};
