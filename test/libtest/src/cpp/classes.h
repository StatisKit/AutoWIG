#ifndef CLASSES_H
#define CLASSES_H

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

#endif
