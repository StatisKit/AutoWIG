__all__ = []

try:
    from matplotlib import pyplot
    import networkx

    def plot(self, layout='graphviz', size=16, aspect=.5, invert=False, pattern='(.*)', type=False, base=False, directories=True, files=True, fundamentals=False, variables=False, **kwargs):
        graph = self.to_networkx(pattern,
                specialization=specialization,
                type=type,
                base=base,
                directories=directories,
                files=files,
                fundamentals=fundamentals,
                variables=variables)
        mapping = {j : i for i, j in enumerate(graph.nodes())}
        graph = networkx.relabel_nodes(graph, mapping)
        layout = getattr(networkx, layout+'_layout')
        nodes = layout(graph)
        if invert:
            fig = pyplot.figure(figsize=(size*aspect, size))
        else:
            fig = pyplot.figure(figsize=(size, size*aspect))
        axes = fig.add_subplot(1,1,1)
        axes.set_axis_off()
        mapping = {j : i for i, j in mapping.iteritems()}
        xmin = float("Inf")
        xmax = -float("Inf")
        ymin = float("Inf")
        ymax = -float("Inf")
        for node in graph.nodes():
            xmin = min(xmin, nodes[node][0])
            xmax = max(xmax, nodes[node][0])
            ymin = min(ymin, nodes[node][1])
            ymax = max(ymax, nodes[node][1])
            asgnode = self[mapping[node]]
            nodes[node] = axes.annotate(asgnode.localname, nodes[node],
                    xycoords = "data",
                    color = 'k',
                    bbox = dict(
                        boxstyle = 'round',
                        fc = 'w',
                        lw = 2.,
                        alpha = 1.,
                        ec = 'k'))
            nodes[node].draggable()
        for source, target in graph.edges():
            axes.annotate(" ",
                    xy=(.5, .5),
                    xytext=(.5, .5),
                    ha="center",
                    va="center",
                    xycoords=nodes[target],
                    textcoords=nodes[source],
                    color="k",
                    arrowprops=dict(
                        patchA = nodes[source].get_bbox_patch(),
                        patchB = nodes[target].get_bbox_patch(),
                        arrowstyle = '->',
                        linestyle = graph.edge[source][target]['linestyle'],
                        connectionstyle = 'arc3,rad=0.',
                        lw=2.,
                        fc=graph.edge[source][target]['color'],
                        ec=graph.edge[source][target]['color'],
                        alpha=1.))
        axes.set_xlim(xmin, xmax)
        axes.set_ylim(ymin, ymax)
        return axes

    from .asg import AbstractSemanticGraph
    AbstractSemanticGraph.plot = plot
    del plot

except:
    pass
