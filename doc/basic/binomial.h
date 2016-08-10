#include <exception>

struct ProbabilityError : std::exception
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
};