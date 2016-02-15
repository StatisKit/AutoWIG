struct Staticness
{
    Staticness();
    
    void staticness(); // print "non-static"
    void staticness(const unsigned int value); // print "non-static"    
    static void staticness(const Staticness& staticness, const unsigned int value); // print "static"
};

struct Constness
{
    Constness();
    
    void constness(); // print "non-const"
    void constness() const; // print "const"
};

struct NonConstness
{
    NonConstness();
    
    void constness() const; // print "const"
    void constness(); // print "non-const"
};
