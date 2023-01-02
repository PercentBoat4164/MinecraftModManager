import Mod

import os
import multiprocessing


class Instance:
    _mods = []

    def __init__(self, path, name, game_version, loader):
        self.path = path
        self.name = name
        self._game_version = game_version
        self._loader = loader

    def __repr__(self):
        return self.name + " @ " + self.path + " : " + self._loader + " " + self._game_version

    def is_compatible_with(self, version):
        return self._loader in version.loaders and self._game_version in version.gameVersions

    def infer_mod(self, mod):
        if mod.endswith(".disabled"):
            return None
        try:
            return Mod.Mod(self.path + '/' + mod)
        except Mod.ModNotFoundError as error:
            print(error)
            return mod, error.mapped

    def infer_all_existing_mods(self):
        # Asynchronously infer all existing mods
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        self._mods = pool.map_async(self.infer_mod, os.listdir(self.path + "/mods")).get()
        pool.close()
        pool.join()

        # Sort mods into missed and found
        missed_mods = list(filter(lambda item: type(item) is tuple, self._mods))
        self._mods = list(filter(lambda item: type(item) is Mod.Mod, self._mods))

        # Display results
        print("Found mods:", ', '.join((str(i) for i in self._mods)))
        print("Missed mods (Ignored):", ', '.join(i[0] + " -> " + i[1] + "?" if len(i) == 2 else i[0] for i in missed_mods))

    def update_all_inferred_mods(self):

        for mod in self._mods:
            mod.update(self)
