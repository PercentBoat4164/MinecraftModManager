import multiprocessing
import os

import Mod


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
        return self._loader in version["loaders"] or (self._loader == "quilt" and "fabric" in version["loaders"]) and self._game_version in version["game_versions"]

    def _get_mod(self, mod):
        if mod.endswith(".disabled"):
            return None
        try:
            return Mod.Mod(self.path + '/mods/' + mod)
        except Mod.ModNotFoundException as error:
            print(error)
            return mod

    def _update_mod(self, mod):
        mod.update(self)

    def get_all_mods(self):
        print("====================== MOD  MISSES ======================")
        # Asynchronously catalogue all existing mods
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        self._mods = pool.map_async(self._get_mod, os.listdir(self.path + "/mods/")).get()
        pool.close()
        pool.join()

        # Sort mods into missed and found
        missed_mods = list(filter(lambda item: type(item) is str, self._mods))
        self._mods = list(filter(lambda item: type(item) is Mod.Mod, self._mods))

        # Display results
        print("\n\n===================== MOD CATALOGUE =====================")
        print("Found mods:", ', '.join((str(i) for i in self._mods)))
        print("Missed mods (Ignored):",
              ', '.join(missed_mods))

    def update_all_mods(self):
        # Asynchronously update all existing mods
        print("\n\n====================== UPDATE  LOG ======================")
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        pool.map_async(self._update_mod, self._mods).get()
