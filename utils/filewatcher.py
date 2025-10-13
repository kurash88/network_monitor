from watchfiles import awatch


class FileWatcher:
    def __init__(self, path):
        self.path = path
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    async def watch(self):
        async for _ in awatch(self.path):
            for observer in self.observers:
                await observer.add_task_queues_to_runners()
