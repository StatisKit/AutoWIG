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
    
    //! \brief Compute the probability of a value
    //! \details The probability is given by the flowwing formula \cite{JKK96}
    //!          
    //!          \f{equation*}{
    //!                 P\left(X = x\right) = \begin{cases}
    //!                                            \binon{n}{x} \pi^x \left(1 - \pi\right)^{n-x} & \mbox{if } 0 \leq x \leq n\\
    //!                                             0 & \mbox{otherwise}
    //!                                       \end{cases}.
    //!          \f}
    //! \returns The probability
    double pmf(const unsigned int value) const;
        
    double get_pi() const;
    
    /** 
     * \param pi New probability value
     * \warning The probability value must be in the interval  \f$\left[0,1\right]\f$
     * \throws \ref ::ProbabilityError If the new probability value is not 
     *         in the interval \f$\left[0,1\right]\f$ */
    void set_pi(const double pi);
   
    unsigned int n;
    
  protected:
    double _pi;

  private:
     unsigned int factorial(const unsigned int value) const;
};
