class ClassA
{
    public:
        class Nested()
        {};

        ClassA();
        virtual ~ClassA();
        ClassA(const ClassA& ca);
};

class ClassB : public ClassA
{};

class ClassC : private ClassA
{};

class ClassD
{};

class ClassE : public ClassA, classD
{};

template<typename A>
class classF
{};
