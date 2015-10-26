def add_sconscript(self, **kwargs):
    pydir = kwargs.pop('pydir', '../' + self.localname.replace(self.suffix, ''))
    env = kwargs.pop('env', 'env')
    sconscript = self.asg.add_file(self.parent + 'SConscript')
    content = 'Import("' + env + ')\nwrapper_' + env + ' = ' + env + '.Clone()\n'
    content += 'sources = ["' + '",\n           '.join(export.globalname.replace(directory.globalname, '') for export in self.exports if not export.is_empty) + '"]\n'
    content += 'target = str(wrapper_env.Dir(' + pydir + ')) + "/_' + self.localname.replace(self.suffix, '') + '"'
    dirnode = self.add_directory(pydir)
    content += 'if os.name == "nt":\n    SHLIBSUFFIX = ".pyd"\nelse:\n    SHLIBSUFFIX = ".so"\n\n'
    content += 'if wrapper_' + env + '["compiler"] == "msvc" and "8.0" in wrapper_' + env +'["MSVS_VERSION"]:'

    real_target = "%s/%s" % (str(env.Dir(python_dir).srcnode()), target)

    if os.name == 'nt':
        kwds['SHLIBSUFFIX'] = '.pyd'
    else:
        kwds['SHLIBSUFFIX'] = '.so'

    if (env['compiler'] == 'msvc') and ('8.0' in env['MSVS_VERSION']):
        kwds['SHLINKCOM'] = [env['SHLINKCOM'],
        'mt.exe -nologo -manifest ${TARGET}.manifest -outputresource:$TARGET;2']

    if os.name == 'nt':
    # Fix bug with Scons 0.97, Solved in newer versions.
        wrap = env.SharedLibrary(real_target, source,
                           SHLIBPREFIX='',
                           *args, **kwds)
    elif sys.platform == 'darwin':
        wrap = env.LoadableModule(real_target, source,
                           SHLIBPREFIX='',
                           LDMODULESUFFIX='.so',
                           FRAMEWORKSFLAGS = \
                            '-flat_namespace -undefined suppress',
                           *args, **kwds)
    else:
        wrap = env.LoadableModule(real_target, source,
                           SHLIBPREFIX='',
                           *args, **kwds)

    Alias("build", wrap)
    return wrap

class BoostPythonExportStlContainerFileProxy(BoostPythonExportFileProxy):

    language = 'c++'

    VECTOR = Template(text=r"""\
% if not call:
#include <boost/python.hpp>\
    %for header in headers:

${include(header)}
    %endfor

struct vector_${stdvector.hash}_to_python
{
    static PyObject* convert(const ${stdvector.globalname}& v)
    {
        boost::python::list result = boost::python::list();
        for(auto it = v.cbegin(), ite = c.cend(); it != ite; ++it)
        { result.append(boost::python::object(*it)); }
        return boost::python::incref(boost::python::typle(result).ptr());
    }
};

struct vector_${stdvector.hash}_from_python
{
    vector_${stdvector.hash}_from_python()
    {
        boost::python::converter::registry::push_back(
            &convertible,
            &construct,
            boost::python::type_id< ${stdvector.globalname} > >());
    }

    static void* convertible(PyObject* obj_ptr)
    { return obj_ptr; }

    static void construct(PyObject* obj_ptr, boost::python::converter::rvalue_from_python_stage1_data* data)
    {
        boost::python::handle<> obj_iter(PyObject_GetIter(obj_ptr));
        void* storage = ((boost::python::converter::rvalue_from_python_storage< ${stdvector.globalname} >*)data)->storage.bytes;
        new (storage) ${stdvector.globalname}();
        data->convertible = storage;
        ${stdvector.globalname}& result = *((${stdvector.globalname}*)storage);
        unsigned int i = 0;
        for(;; i++)
        {
            boost::python::handle<> py_elem_hdl(boost::python::allow_null(PyIter_Next(obj_iter.get())));
            if(PyErr_Occurred())
            { boost::python::throw_error_already_set(); }
            if(!py_elem_hdl.get())
            { break; }
            boost::python::object py_elem_obj(py_elem_hdl);
            result.push_back(${template}(boost::python::extract< ${stdvector.templates[0].globalname} >(py_elem_obj)));
        }
    }
};
% else:
    boost::python::to_python_converter< ${stdvector.globalname}, vector_${stdvector.hash}_to_python >();
    vector_${stdvector.hash}_from_python();
% endif""")

    SET = Template(text="""\
% if not call:
#include <boost/python.hpp>\
    %for header in headers:

${include(header)}
    %endfor

struct set_${stdset.hash}_to_python
{
    static PyObject* convert(const ${stdset.globalname}& v)
    {
        boost::python::list result = boost::python::list();
        ${stdset.globalname}::const_iterator it;
        for(it = v.begin(); it != v.end(); ++it)
        { result.append(boost::python::object(*it)); }
        return boost::python::incref(boost::python::tuple(result).ptr());
    }
};

struct set_${stdset.hash}_from_python
{
    set_${stdset.hash}_from_python()
    {
        boost::python::converter::registry::push_back(
            &convertible,
            &construct,
            boost::python::type_id< ${stdset.globalname} > >());
    }

    static void* convertible(PyObject* obj_ptr)
    { return obj_ptr; }

    static void construct(PyObject* obj_ptr, boost::python::converter::rvalue_from_python_stage1_data* data)
    {
        boost::python::handle<> obj_iter(PyObject_GetIter(obj_ptr));
        void* storage = ((boost::python::converter::rvalue_from_python_storage< ${stdset.globalname} >*)data)->storage.bytes;
        new (storage) ${stdset.globalname}();
        data->convertible = storage;
        ${stdset.globalname}& result = *((${stdset.globalname}*)storage);
        unsigned int i = 0;
        for(;; i++)
        {
            boost::python::handle<> py_elem_hdl(boost::python::allow_null(PyIter_Next(obj_iter.get())));
            if(PyErr_Occurred())
            { boost::python::throw_error_already_set(); }
            if(!py_elem_hdl.get())
            { break; }
            boost::python::object py_elem_obj(py_elem_hdl);
            result.insert(boost::python::extract< ${stdset.templates[0].globalname} >(py_elem_obj));
        }
    }
};
% else:
    boost::python::to_python_converter< ${stdset.globalname} >, set_${stdset.hash}_to_python >();
    set_{stdset.hash}_from_python();
%endif""")

    MAP = Template(text="""\
% if not call:
#include <boost/python.hpp>\
    %for header in headers:

${include(header)}
    %endfor

struct map_${stdmap.hash}_to_python
{
    static PyObject* convert(const ${stdmap.globalname}& m)
    {
        boost::python::dict result = boost::python::dict();
        ${stdmap.globalname}::const_iterator it;
        for(it = m.begin(); it != m.end(); ++it)
        { result[boost::python::object((*it).first)] = boost::python::object((*it).second); }
        return boost::python::incref(result.ptr());
    }
};

struct map_${stdmap.hash}_from_python
{
    map_${stdmap.hash}_from_python()
    {
        boost::python::converter::registry::push_back(
            &convertible,
            &construct,
            boost::python::type_id< ${stdmap.globalname} > >());
    }

    static void* convertible(PyObject* obj_ptr)
    { return obj_ptr; }

    static void construct(PyObject* obj_ptr, boost::python::converter::rvalue_from_python_stage1_data* data)
    {
        boost::python::handle<> obj_iter(PyObject_GetIter(obj_ptr));
        void* storage = ((boost::python::converter::rvalue_from_python_storage< ${stdmap.globalname} >*)data)->storage.bytes;
        new (storage) ${stdmap.globalname}();
        data->convertible = storage;
        ${stdmap.globalname}& result = *((${stdmap.globalname}*)storage);
        unsigned int i = 0;
        for(;; i++)
        {
            boost::python::handle<> py_elem_hdl(boost::python::allow_null(PyIter_Next(obj_iter.get())));
            if(PyErr_Occurred())
            { boost::python::throw_error_already_set(); }
            if(!py_elem_hdl.get())
            { break; }
            boost::python::object py_elem_obj(py_elem_hdl);
            result[boost::python::extract< ${stdmap.templates[0].globalname} >(py_elem_obj[0])] = boost::python::extract< ${stdmap.templates[1].globalname} >(py_elem_obj[1]);
        }
    }

};
% else:
    boost::python::to_python_converter< ${stdmap.globalname} >, map_${stdmap.hash}_to_python >();
    map_${stdmap.hash}_from_python();
% endif
""")

    def add_wrap(self, wrap):
        if not isinstance(wrap, ClassTemplateSpecializationProxy) or not wrap.specialize.globalname in ['class ::std::vector', 'class ::std::set', 'class ::std::map']:
            raise ValueError()
        self.asg._nodes[self.node]['_wraps'].append(wrap.node)
        wrap.boost_python_export = self.node

    @property
    def is_empty(self):
        return len(self._wraps) == 0

    @property
    def headers(self):
        if self._held_type is None:
            return self.asg.headers(*self.wraps)
        else:
            return self.asg.headers(self.asg[self._held_type], *self.wraps)

    def include(self, header):
        if header.language == 'c':
            return 'extern "C" { #include <' + self.asg.include_path(header) + '> }'
        else:
            return '#include <' + self.asg.include_path(header) + '>'

def get_content(self):
    if not hasattr(self, '_content') or self._content == "":
        if self.is_empty:
            filepath = path(self.globalname)
            if filepath.exists():
                return "".join(filepath.lines())
            else:
                return ""
        else:
            content = ""
            for wrap in self.wraps:
                if isinstance(wrap, ClassTemplateSpecializationProxy):
                    specialize = wrap.specialize
                    if specialize == 'class ::std::vector':
                        content += self.VECTOR.render(include = self.include, headers=self.headers, stdvector=wrap, call=False)
                    elif specialize == 'class ::std::set':
                        content += self.SET.render(include = self.include, headers=self.headers, stdset=wrap, call=False)
                    elif specialize == 'class ::set::map':
                        content += self.MAP.render(include = self.include, headers=self.headers, stdmap=wrap, call=False)
            content += 'void ' + self.prefix + '()\n{'
            for wrap in self.wraps:
                if isinstance(wrap, ClassTemplateSpecializationProxy):
                    specialize = wrap.specialize
                    if specialize == 'class ::std::vector':
                        content += self.VECTOR.render(include = self.include, headers=self.headers, stdvector=wrap, call=True)
                    elif specialize == 'class ::std::set':
                        content += self.SET.render(include = self.include, headers=self.headers, stdset=wrap, call=True)
                    elif specialize == 'class ::set::map':
                        content += self.MAP.render(include = self.include, headers=self.headers, stdmap=wrap, call=True)
            content += '\n;}'
            return content
    else:
        return self._content

def set_content(self, content):
    self.asg._nodes[self.node]['_content'] = content

def del_content(self):
    self.asg._nodes[self.node].pop('_content', False)

BoostPythonExportStlContainerFileProxy.content = property(get_content, set_content, del_content)
del get_content, set_content, del_content

def stl_back_end(asg, filename, **kwargs):
    from vplants.autowig.back_end import BackEndDiagnostic
    prev = time.time()
    if filename in asg:
        modulenode = asg[filename]
    else:
        modulenode = asg.add_file(filename, proxy=kwargs.pop('module', BoostPythonModuleFileProxy))
        if 'target' in kwargs:
            target = asg.add_directory(kwargs.pop('target'))
            modulenode.target = target.globalname
    export = kwargs.pop('export', BoostPythonExportStlContainerFileProxy)
    nodes = asg.nodes('^class ::std::(vector|set|map)<(.*)>$')
    suffix = modulenode.suffix
    directory = modulenode.parent.globalname
    with_closure = kwargs.pop('with_closure', True)
    while len(nodes) > 0:
        node = nodes.pop()
        if node.boost_python_export is True:
            if isinstance(node.templates[0], FundamentalTypeProxy):
                exportnode = modulenode.add_boost_python_export(directory + node_path(node, prefix='converter_', suffix=suffix), proxy=export)
                exportnode.add_wrap(node)
                if with_closure:
                    temps = [dcl for dcl in node.declarations() if dcl.boost_python_export is True]
                    while len(temps) > 0:
                        temp = temps.pop()
                        if temp.boost_python_export is True:
                            temp.boost_python_export = False
                        if isinstance(temp, (TypedefProxy, VariableProxy)):
                            target = temp.type.target
                            if target.boost_python_export is True:
                                temps.append(target)
                        elif isinstance(temp, FunctionProxy):
                            result_type = temp.result_type.target
                            if not result_type.boost_python_export:
                                temps.append(result_type)
                            for parameter in temp.parameters:
                                target = parameter.type.target
                                if not target.boost_python_export:
                                    temps.append(target)
                        elif isinstance(node, ConstructorProxy):
                            for parameter in temp.parameters:
                                target = parameter.type.target
                                if not target.boost_python_export:
                                    temps.append(target)
                        elif isinstance(temp, ClassProxy):
                            for base in temp.bases():
                                if not base.boost_python_export and base.access == 'public':
                                    temps.append(base)
                            for dcl in temp.declarations():
                                if dcl.boost_python_export is True and dcl.access == 'public':
                                    temps.append(dcl)
            else:
                bpe = node.templates[0].boost_python_export
                if bpe:
                    if not bpe is True:
                        bpm = bpe.boost_python_module
                        if not bpm is None:
                            bpm.add_boost_python_export(bpm.parent.globalname + node_path(node, prefix='converter_',
                                suffix=suffix), proxy=export)
                    else:
                        if re.math('^class ::std::map<(.*)>$', node.globalname):
                        if re.match('^class ::std::(vector|set|map)<(.*)>$', node.templates[0].target.globalname):
                            nodes.append(node.templates[0].target)
                            if re.math('^class ::std::map<(.*)>$', node.globalname):
                                if re.match('^class ::std::(vector|set|map)<(.*)>$', node.templates[1].target.globalname):
                                    nodes.append(node.templates[1].target)
                            nodes.append(node)
    diagnostic = BackEndDiagnostic()
    curr = time.time()
    diagnostic.elapsed = curr - prev
    diagnostic.on_disk = False
    return diagnostic
