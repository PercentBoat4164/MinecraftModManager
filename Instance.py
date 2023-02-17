import multiprocessing
import os
import threading
import time

import Mod


class LoadingScreenAnimator:
    def __init__(self, frames: tuple[str] | list[str] | str = r"\|/-", framerate: float | int = 4):
        self._frames = frames
        self._frame = 0
        self._animate = True
        self._frametime = 1 / framerate
        if len(frames) < 0:
            raise ValueError("There must be at least one frame!")

    def start(self):
        self._animate = True
        threading.Thread(target=self.animate_loading_screen).start()

    def stop(self):
        self._animate = False

    def animate_loading_screen(self):
        previous_frame_len = len(self._frames[0])
        print(self._frames[0], end="")
        i = 1
        while self._animate:
            time.sleep(self._frametime)
            string = "\b" * previous_frame_len + self._frames[i]
            if self._animate:
                print(string, end="")
            previous_frame_len = len(self._frames[i])
            i = (i + 1) % len(self._frames)


class Instance:
    def __init__(self, path, name, game_version, loader):
        self._mods = []
        self.path = path
        self.name = name
        self._game_version = game_version
        self._loader = loader

    def __repr__(self):
        return self.name + " @ " + self.path + " - " + self._loader + " " + self._game_version

    def is_compatible_with(self, version):
        return (self._loader in version["loaders"] or (
                    self._loader == "quilt" and "fabric" in version["loaders"])) and self._game_version in version[
            "game_versions"]

    def _get_mod(self, mod):
        if mod.endswith(".disabled"):
            return None
        try:
            return Mod.Mod(os.path.join(self.path, "mods", mod))
        except Mod.ModNotFoundException:
            return mod

    def _update_mod(self, mod):
        return mod.update(self)

    def get_all_mods(self):
        animator = LoadingScreenAnimator()
        print("Cataloguing all mods ", end="")
        animator.start()

        # Asynchronously catalogue all existing mods
        mod_path = os.path.join(self.path, "mods")
        if not os.path.exists(mod_path):
            animator.stop()
            print("\b" * 22, end="")
            print("This instance must be started at least once before updating. The 'mods' folder does not exists.")
            return

        mods_to_try = os.listdir(mod_path)
        pool = multiprocessing.Pool(len(mods_to_try))
        self._mods = pool.map_async(self._get_mod, mods_to_try).get()
        pool.close()
        pool.join()

        animator.stop()

        # Sort mods into missed and found
        missed_mods = list(filter(lambda item: type(item) is str, self._mods))
        self._mods = list(filter(lambda item: type(item) is Mod.Mod, self._mods))

        # Display results
        print("\b" * 22, end="")
        if len(self._mods) > 0:
            print("======================= CATALOGUE =======================")
            print("Found mods:\n\t" + "\n\t".join((str(i) for i in self._mods)))
        if len(missed_mods) > 0:
            print("Missed mods:\n\t" + "\n\t".join(missed_mods))

    def update_all_mods(self):
        if len(self._mods) > 0:
            animator = LoadingScreenAnimator()
            print("Updating all mods ", end="")
            animator.start()

            # Asynchronously update all existing mods
            pool = multiprocessing.Pool(len(self._mods))
            updated_mods = pool.map_async(self._update_mod, self._mods).get()
            pool.close()
            pool.join()

            animator.stop()

            # Filter updated mods
            updated_mods = list(filter(lambda item: type(item) is str, updated_mods))

            # Display results
            print("\b" * 19 + "======================== UPDATES ========================")
            if len(updated_mods) > 0:
                print("Updated mods:\n\t" + "\n\t".join(updated_mods))
            else:
                print("All mods are already up-to-date!")

    def get_game_version(self):
        return self._game_version

    def get_loader(self):
        return self._loader
