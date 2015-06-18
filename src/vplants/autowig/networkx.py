__all__ = []

try:
    import networkx
    from abc import ABCMeta

    def to_networkx(self, pattern='(.*)', type=True, base=True, directories=True, files=True, fundamentals=True, variables=True):
        graph = networkx.DiGraph()

        class Filter(object):

            __metaclass__ = ABCMeta

        if not directories:
            Filter.register(DirectoryProxy)
        if not files:
            Filter.register(FileProxy)
        if not fundamentals:
            Filter.register(FundamentalTypeProxy)
        if not variables:
            Filter.register(VariableProxy)
        for node in self.nodes():
            if not isinstance(node, Filter):
                graph.add_node(node.id)
        for source, targets in self._syntax_edges.iteritems():
            if not isinstance(self[source], Filter):
                for target in targets:
                    if not isinstance(self[target], Filter):
                        graph.add_edge(source, target, color='k', linestyle='solid')
        if type:
            for source, target in self._type_edges.iteritems():
                if not isinstance(self[source], Filter) and not isinstance(self[target['target']], Filter):
                    graph.add_edge(source, target['target'], color='r', linestyle='solid')
        if base:
            for source, targets in self._base_edges.iteritems():
                if not isinstance(self[source], Filter):
                    for target in targets:
                        if not isinstance(self[target], Filter):
                            graph.add_edge(source, target['base'], color='m', linestyle='solid')

        return graph.subgraph([node for node in graph.nodes() if re.match(pattern, node)])


    from .asg import AbstractSemanticGraph
    AbstractSemanticGraph.to_networkx = to_networkx
    del to_networkx

except:
    pass
