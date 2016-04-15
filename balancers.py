import logging

from settings import DomainState


class SimpleBalancer(object):
    def __init__(self, nodes):
        self.nodes = nodes

    def get_node_for(self, domain):
        stats = {}
        for node_id, node in self.nodes.items():
            node_stats = {
                'memory': 0,
                'num_virt_cpu': 0
            }
            for domain in node.listAllDomains():
                info = domain.info()
                if DomainState(info[0]) == DomainState.RUNNING:
                    node_stats['memory'] += info[2]
                    node_stats['num_virt_cpu'] += info[3]
            stats_key = (node_stats['num_virt_cpu'], node_stats['memory'])
            stats.update({stats_key: node_id})
            logging.info('Stats for %s: %s', node_id, stats_key)
        free_node_id = stats[min(stats.keys())]
        return free_node_id, self.nodes[free_node_id]
