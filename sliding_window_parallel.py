import os
from multiprocessing import Pool

def run_process(process):
    os.system('python {}'.format(process))

start = datetime.now()
pool = Pool(processes=2)
pool.map(run_process, processes)
print datetime.now() - start