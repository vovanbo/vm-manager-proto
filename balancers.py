class SimpleBalancer(object):
    def __init__(self, nodes):
        self.nodes = nodes

    def get_node_for(self, domain):
        return 0, self.nodes[0]
