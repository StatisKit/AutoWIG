Polygon::Polygon(const double& _width, const double& _height)
{
    set_width(_width);
    set_height(_height);
}

Polygon::Polygon(const Polygon& _polygon)
{ 
    width = _polygon.width;
    height = _polygon.height;
}

double Polygon::get_width() const
{ return width; }

void Polygon::set_width(const double& _width)
{ width = _width; }

double Polygon::get_height() const
{ return height; }

void Polygon::set_height(const double& _height)
{ height = _height; }

Rectangle::Rectangle(const double& _width, const double& _height) : Polygon(_width, _height)
{}

Rectangle::Rectangle(const Rectangle& _rectangle) : Polygon(_rectangle)
{}

Rectangle::~Rectangle()
{}

double Rectangle::compute_area() const
{ return width*height; }

Polygon* Rectangle::copy() const
{ return new Rectangle(widht, height); }

Triangle::Triangle(const double& _width, const double& _height) : Polygon(_width, _height)
{}

Triangle::Triangle(const Triangle& _triangle) : Polygon(_triangle)
{}

Triangle::~Triangle()
{}

double Triangle::compute_area() const
{ return width*height/2.; }

Polygon* Triangle::copy() const
{ return new Triangle(widht, height); }
