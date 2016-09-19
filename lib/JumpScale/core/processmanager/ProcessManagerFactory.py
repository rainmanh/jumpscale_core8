from JumpScale import j


from multiprocessing import Pool
import time


def f(x):
    counter = 0
    while True:
        counter += 1
        print(counter)
        time.sleep(1)


class ProcessManagerFactory:

    def __init__(self):
        self.__jslocation__ = "j.core.processmanager"

    def test(self):

        p = Pool(50)
        from IPython import embed
        print("DEBUG NOW 87878")
        embed()
        raise RuntimeError("stop debug here")
