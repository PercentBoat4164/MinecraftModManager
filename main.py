import multiprocessing


def server():
    pass


if __name__ == "__main__":
    multiprocessing.freeze_support()
    multiprocessing.Process(target=server).start()

