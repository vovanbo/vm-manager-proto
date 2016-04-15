import logging
import time
import uuid

from datetime import datetime

from tornado import template

from utils import get_db_connect


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


def get_free_pool(pools):
    # TODO: Select pool with maximum available storage
    return pools[0]


def get_domain_info(domain):
    info = domain.info()
    return {
        'id': domain.ID(),
        'uuid': domain.UUID().hex(),
        'name': domain.name(),
        'os_type': domain.OSType(),
        'info': {
            'state': info[0],
            'max_memory': info[1],
            'memory': info[2],
            'num_virt_cpu': info[3],
            'cpu_time': info[4],
        }
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
    user_id = kwargs.pop('user_id')
    loader = template.Loader(app.settings.get('template_path'))

    node_id, node = app.balancer.get_node_for(kwargs)
    pool = get_free_pool(node.listAllStoragePools())
    assert pool, 'Pool is required for domain creation on node %s.' % node_id

    kwargs.update({
        'uuid': uuid.uuid4(),
        'node': node_id,
    })

    volume_xml = loader.load('volume.template.xml')
    volume_capacity = kwargs.pop('volume_capacity', 10)
    volume_path = '/tmp/volumes/{}/{}.img'.format(node_id, kwargs['uuid'])
    volume = pool.createXML(volume_xml.generate(
        name='volume-for-{}'.format(kwargs['name']),
        capacity=volume_capacity, path=volume_path
    ).decode('utf-8'))
    assert volume, 'Volume creation is failed!'

    logging.info(kwargs)
    domain_xml = loader.load('domain.template.xml')
    domain = node.createXML(domain_xml.generate(
        disk_source=volume_path, **kwargs
    ).decode('utf-8'))
    assert domain, 'Domain creation is failed!'

    created = datetime.utcnow()
    db = get_db_connect()
    db.execute(
        'INSERT INTO domains (id, name, node, user_id, created) '
        'VALUES (?, ?, ?, ?, ?)',
        (domain.UUID().hex(), domain.name(), node_id, user_id, created)
    )
    db.commit()
    return get_domain_info(domain)
