import json
import os.path

import Instance


class MultiMC:
    _LINUX_MULTIMC_INSTANCE_LOCATION = os.path.expanduser("~/.local/share/multimc/instances")
    _WINDOWS_MULTIMC_INSTANCE_LOCATION = os.path.expanduser("/instances")
    instances = {}

    def __init__(self):
        self.INSTANCE_LOCATION = ""
        if os.name == 'nt':
            while not os.path.exists(self.INSTANCE_LOCATION):
                self.INSTANCE_LOCATION = str(input(
                    "Enter the path to the MultiMC directory. (The directory containing the executable)\n")) + self._WINDOWS_MULTIMC_INSTANCE_LOCATION
        else:
            self.INSTANCE_LOCATION = self._LINUX_MULTIMC_INSTANCE_LOCATION
        # Search for all instances controlled my MultiMC
        if os.path.isdir(self.INSTANCE_LOCATION):
            for i in os.scandir(self.INSTANCE_LOCATION):
                # Does this directory contains a valid instance?
                if os.path.isfile(os.path.join(i, "instance.cfg")):
                    # Find the instance name from the cfg file
                    name = ''
                    with open(os.path.join(i, "instance.cfg")) as f:
                        cfgs = f.read().splitlines()
                        for cfg in cfgs:
                            if cfg.find("name=") > -1:
                                name = cfg.split('=')[-1]

                    # Find the game version and mod loader used for this instance
                    game_version = ''
                    loader = ''
                    with open(os.path.join(i, "mmc-pack.json")) as f:
                        mmc_pack = json.loads(f.read())
                        for component in mmc_pack["components"]:
                            match component["cachedName"]:
                                case "Minecraft":
                                    game_version = component["version"]
                                case "Fabric Loader":
                                    loader = "fabric"
                                case "Forge":
                                    loader = "forge"
                                case "Quilt Loader":
                                    loader = "quilt"

                    # Export data to a new Instance
                    self.instances.update({name: Instance.Instance(os.path.join(i, ".minecraft"), name, game_version, loader)})

    def __repr__(self):
        return str(self.instances)

    def ask_for_instance(self):
        print(self)
        while True:
            try:
                return self.instances[str(input("Enter an instance name to update.\n"))]
            except KeyError:
                pass



if __name__ == "__main__":
    multimc_manager = MultiMC()
    print(multimc_manager)
