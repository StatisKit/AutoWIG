#include <exception>

struct ProbabilityError : std::exception
{ 
    ProbabilityError();
    virtual const char* what() const noexcept; 
};

class BinomialDistribution
{
  public:
    BinomialDistribution(const unsigned int n, const double pi);
    BinomialDistribution(const BinomialDistribution& binomial);
	
    double pmf(const unsigned int& event) const;
     
    double get_pi() const;

    /// \param pi New probability value
    /// \throws ::ProbabilityError If the new probability value is not in the interval \f$\left[0,1\right]\f$
    void set_pi(const double pi);
   
    unsigned int n;
    
  protected:
    double _pi;
};
