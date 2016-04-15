import logging
import time
import uuid


# WARNING: All the results of commands must be JSON-serializable!


def start(**kwargs):
    logging.info('BEGIN commands.start')
    time.sleep(5)
    logging.info('END commands.start, %s', kwargs)
    return [{
        'domain_id': kwargs.get('domain_id')
    }, ]


def get_pool_info(pool):
    info = pool.info()
    return {
        'name': pool.name(),
        'uuid': pool.UUIDString(),
        'autostart': pool.autostart(),
        'is_active': pool.isActive(),
        'is_persistent': pool.isPersistent(),
        'num_volumes': pool.numOfVolumes(),
        'state': info[0],
        'capacity': info[1],
        'allocation': info[2],
        'available': info[3]
    }


def get_nodes_info(**kwargs):
    app = kwargs.pop('app')
    node_id = kwargs.get('node_id')
    nodes = app.nodes
    if node_id:
        node_id = int(node_id)
        nodes = {k: v for k, v in nodes.items() if k == node_id}
    result = []
    logging.info(nodes)
    for id, node in nodes.items():
        info = node.getInfo()
        result.append({
            'id': id,
            'hostname': node.getHostname(),
            'max_vcpus': node.getMaxVcpus(None),
            'type': node.getType(),
            'uri': node.getURI(),
            'info': {
                'cpu_model': info[0],
                'memory_size': info[1],
                'active_cpus': info[2],
                'cpu_frequency': info[3],
                'numa_nodes': info[4],
                'cpu_sockets': info[5],
                'cores_per_socket': info[6],
                'threads_per_core': info[7],
            },
            'domains': node.listDomainsID(),
            'pools': [get_pool_info(p) for p in node.listAllStoragePools()],
        })
    return result if node_id is None else result[0]


def create_domain(**kwargs):
    app = kwargs.pop('app')
    node_id, node = app.balancer.get_node_for(kwargs)
    result = {
        'id': str(uuid.uuid4()),
        'node': node_id,
    }
    result.update(**kwargs)
    return result
