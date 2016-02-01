#include <boost/python.hpp>
#include <vector>
#include <set>
#include <map>
% for i in includefiles:
#include <${i.replace('./src/cpp', library)}>
% endfor

% for template in vectortemplates:
struct vector_${template.replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_to_python
{
    static PyObject* convert(const std::vector< ${template} >& v)
    {
        boost::python::list result = boost::python::list();
        std::vector< ${template} >::const_iterator it;
        for(it = v.begin(); it != v.end(); ++it)
        { result.append(boost::python::object(*it)); }
        return boost::python::incref(boost::python::tuple(result).ptr());
    }
};



% endfor
% for template in settemplates:
struct set_${template.replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_to_python
{
    static PyObject* convert(const std::set< ${template} >& v)
    {
        boost::python::list result = boost::python::list();
        std::set< ${template} >::const_iterator it;
        for(it = v.begin(); it != v.end(); ++it)
        { result.append(boost::python::object(*it)); }
        return boost::python::incref(boost::python::tuple(result).ptr());
    }
};

struct set_${template.replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_from_python
{
    set_${template.replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_from_python()
    {
        boost::python::converter::registry::push_back(
            &convertible,
            &construct,
            boost::python::type_id< std::set< ${template} > >());
    }

    static void* convertible(PyObject* obj_ptr)
    { return obj_ptr; }

    static void construct(PyObject* obj_ptr, boost::python::converter::rvalue_from_python_stage1_data* data)
    {
        boost::python::handle<> obj_iter(PyObject_GetIter(obj_ptr));
        void* storage = ((boost::python::converter::rvalue_from_python_storage< std::set< ${template} > >*)data)->storage.bytes;
        new (storage) std::set< ${template} >();
        data->convertible = storage;
        std::set< ${template} >& result = *((std::set< ${template} >*)storage);
        unsigned int i = 0;
        for(;; i++)
        {
            boost::python::handle<> py_elem_hdl(boost::python::allow_null(PyIter_Next(obj_iter.get())));
            if(PyErr_Occurred())
            { boost::python::throw_error_already_set(); }
            if(!py_elem_hdl.get()) 
            { break; }
            boost::python::object py_elem_obj(py_elem_hdl);
            result.insert(boost::python::extract< ${template} >(py_elem_obj));
        }
    }
      
};

% endfor
% for template in maptemplates:
struct map_${template[0].replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_${template[1].replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_to_python
{
    static PyObject* convert(const std::map< ${template[0]}, ${template[1]} >& m)
    {
        boost::python::dict result = boost::python::dict();
        std::map< ${template[0]}, ${template[1]} >::const_iterator it;
        for(it = m.begin(); it != m.end(); ++it)
        { result[boost::python::object((*it).first)] = boost::python::object((*it).second); }
        return boost::python::incref(result.ptr());
    }
};

struct map_${template[0].replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_${template[1].replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_from_python
{
    map_${template[0].replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_${template[1].replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_from_python()
    {
        boost::python::converter::registry::push_back(
            &convertible,
            &construct,
            boost::python::type_id< std::map< ${template[0]}, ${template[1]} > >());
    }

    static void* convertible(PyObject* obj_ptr)
    { return obj_ptr; }

    static void construct(PyObject* obj_ptr, boost::python::converter::rvalue_from_python_stage1_data* data)
    {
        boost::python::handle<> obj_iter(PyObject_GetIter(obj_ptr));
        void* storage = ((boost::python::converter::rvalue_from_python_storage< std::map< ${template[0]}, ${template[1]} > >*)data)->storage.bytes;
        new (storage) std::map< ${template[0]}, ${template[1]} >();
        data->convertible = storage;
        std::map< ${template[0]}, ${template[1]} >& result = *((std::map< ${template[0]}, ${template[1]} >*)storage);
        unsigned int i = 0;
        for(;; i++)
        {
            boost::python::handle<> py_elem_hdl(boost::python::allow_null(PyIter_Next(obj_iter.get())));
            if(PyErr_Occurred())
            { boost::python::throw_error_already_set(); }
            if(!py_elem_hdl.get()) 
            { break; }
            boost::python::object py_elem_obj(py_elem_hdl);
            result[boost::python::extract< ${template[0]} >(py_elem_obj[0])] = boost::python::extract< ${template[1]} >(py_elem_obj[1]);
        }
    }
      
};

% endfor
BOOST_PYTHON_MODULE(_stl_containers)
{
% for template in vectortemplates:
    boost::python::to_python_converter< std::vector< ${template} >, vector_${template.replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_to_python >();
    vector_${template.replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_from_python();
% endfor
% for template in settemplates:
    boost::python::to_python_converter< std::set< ${template} >, set_${template.replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_to_python >();
    set_${template.replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_from_python();
% endfor
% for template in maptemplates:
    boost::python::to_python_converter< std::map< ${template[0]}, ${template[1]} >, map_${template[0].replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_${template[1].replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_to_python >();
    map_${template[0].replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_${template[1].replace(' ', '').replace('::', '_').replace('<', '').replace('>', '')}_from_python();
% endfor
}

void init_bindings()
{
    Py_Initialize();
    init_stl_containers();
}
