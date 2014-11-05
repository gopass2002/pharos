from collections import namedtuple

Metrics = namedtuple('metrics', [
    'cpu_percent', 'cpu_times_user', 'cpu_times_system',
    'memory_percent', 'memory_rss', 'memory_vms',
    'io_counter_read', 'io_counter_write',
    'network_recv_bytes', 'network_send_bytes'
], verbose=False)
