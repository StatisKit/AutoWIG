#ifndef CLASSES_H
#define CLASSES_H

namespace libtest
{
    class Polygon
    {
        public:
            Polygon(const double& _width, const double& _height);
            Polygon(const Polygon& _polygon);
            virtual ~Polygon();

            double get_width() const;
            void set_width(const double& _width);

            double get_height() const;
            void set_height(const double& _height);

            virtual double compute_area() const = 0;

            virtual Polygon* copy() const = 0;

        protected:
            double width;
            double height;
    };

    class Rectangle: public Polygon
    {
      public:
          Rectangle(double _width, double _height);
          Rectangle(const Rectangle& _rectangle);
          virtual ~Rectangle();

          virtual double compute_area() const;

          virtual Polygon* copy() const;
    };


    class Triangle: public Polygon
    {
      public:
          Triangle(double _width, double _height);
          Triangle(const Triangle& _triangle);
          virtual ~Triangle();

          virtual double compute_area() const;

          virtual Polygon* copy() const;
    };

    template<typename T=Polygon, int I=10> class Container
    {
        //template<class U> U foo();
        T bar(const T& bar);
    };

    template<typename A, int B> class OtherContainer : public Container<A, B>
    {
    };

    /*template<class T> class Container<T*>
    {
    };*/

    //template<typename A> class Container< A*, 10 >;
    //template<> class Container< Polygon &, 10 >;
    //{
    //    double a;
    //};
    /*template<> SPECIALIZATION DO NOT WORK
    class Container< Polygon >
    {
    };*/

    //Container< Polygon, 10 > copy_container(const Container< Polygon, 10 >& container);

    /*
    class PolygonContainer : public Container< Polygon >
    {};*/

    class PolygonContainer : public Container< Polygon >
    {};
}

#endif
