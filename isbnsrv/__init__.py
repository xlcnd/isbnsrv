import concurrent.futures

__api__ = "1"
__version__ = "1.1.1"

SERVER = {"Server": f"isbnsrv/{__version__}"}
executor = concurrent.futures.ThreadPoolExecutor()  # max_workers=(5 x #cores)
