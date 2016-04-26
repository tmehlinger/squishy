WORKER_CLASSES = {
    'gevent': 'squishy.workers.gevent.GeventWorker',
    'futures_process': 'squishy.workers.futures.ProcessPoolWorker',
    'futures_thread': 'squishy.workers.futures.ThreadPoolWorker',
    'mp_process': 'squishy.workers.multiprocessing.ProcessPoolWorker',
    'mp_thread': 'squishy.workers.multiprocessing.ThreadPoolWorker',
}

