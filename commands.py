import logging
import time
import uuid
from datetime import datetime

from tornado import template

from utils import get_db_connect, detailed_pool_info, get_free_pool, detailed_domain_info


# WARNING: All the results of commands must be JSON-serializable!


def debug(**kwargs):
    logging.info('BEGIN commands.start')
    time.sleep(5)
    logging.info('END commands.start, %s', kwargs)
    return True


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
        pools = [detailed_pool_info(p) for p in node.listAllStoragePools()]
        domains = [d.UUID().hex() for d in node.listAllDomains()]
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
            'domains': domains,
            'pools': pools,
        })
    return result if node_id is None else result[0]


def get_domains_info(**kwargs):
    app = kwargs.pop('app')
    user_id = kwargs.pop('user_id')
    domain_id = kwargs.get('domain_id')
    nodes = app.nodes
    db = get_db_connect()
    if domain_id:
        domain_id = str(uuid.UUID(domain_id))
        domains = db.execute(
            'SELECT * FROM domains WHERE uuid = ? AND user_id = ?',
            (domain_id, user_id, )
        ).fetchall()
    else:
        domains = db.execute(
            'SELECT * FROM domains WHERE user_id = ?',
            (user_id, )
        ).fetchall()
    result = [nodes[d['node']].lookupByUUIDString(d['uuid']) for d in domains]
    result = [detailed_domain_info(d) for d in result]
    return result if domain_id is None else result[0]


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
    volume_capacity = kwargs.pop('volume_capacity', 10)  # Default: 10 Gb
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
        'INSERT INTO domains (uuid, name, node, user_id, created) '
        'VALUES (?, ?, ?, ?, ?)',
        (domain.UUIDString(), domain.name(), node_id, user_id, created)
    )
    db.commit()
    return detailed_domain_info(domain)
