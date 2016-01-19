#include <string>

class World
{
    public:
        World();
        
        const std::string& great() const;
        
        void set(const std::string& msg);
        
    protected:
        std::string msg;
};
