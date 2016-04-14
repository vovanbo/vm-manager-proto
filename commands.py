import logging
import time
import uuid


# WARNING: All of commands results must be JSON-serializable values or structs!


def start(**kwargs):
    logging.info('BEGIN commands.start')
    time.sleep(5)
    logging.info('END commands.start, %s', kwargs)
    return [{
        'domain_id': kwargs.get('domain_id')
    }, ]


def get_nodes_info(**kwargs):
    app = kwargs.pop('app')
    node_id = kwargs.get('node_id')
    nodes = app.nodes
    if node_id:
        node_id = int(node_id)
        nodes = {k: v for k, v in nodes.items() if k == id}
    result = []
    for node_id, node in nodes.items():
        info = node.getInfo()
        result.append({
            'id': node_id,
            'hostname': node.getHostname(),
            'max_vcpus': node.getMaxVcpus(None),
            'type': node.getType(),
            'uri': node.getURI(),
            'cpu_model': info[0],
            'memory_size': info[1],
            'active_cpus': info[2],
            'cpu_frequency': info[3],
            'numa_nodes': info[4],
            'cpu_sockets': info[5],
            'cores_per_socket': info[6],
            'threads_per_core': info[7],
        })
    return result[0] if node_id is not None else result


def create_domain(**kwargs):
    app = kwargs.pop('app')
    node_id, node = app.balancer.get_node_for(kwargs)
    result = {
        'id': str(uuid.uuid4()),
        'node': node_id,
    }
    result.update(**kwargs)
    return result
