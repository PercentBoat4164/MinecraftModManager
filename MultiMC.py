import Instance

import json
import os.path


class MultiMC:
    _LINUX_MULTIMC_INSTANCE_LOCATION = os.path.expanduser("~/.local/share/multimc/instances")
    instances = {}

    def __init__(self):
        # Search for all instances controlled my MultiMC
        if os.path.isdir(self._LINUX_MULTIMC_INSTANCE_LOCATION):
            for i in os.scandir(self._LINUX_MULTIMC_INSTANCE_LOCATION):
                # Does this directory contains a valid instance?
                if os.path.isfile(i.path + "/instance.cfg"):
                    # Find the instance name from the cfg file
                    name = ''
                    with open(i.path + "/instance.cfg") as f:
                        cfgs = f.read().splitlines()
                        for cfg in cfgs:
                            if cfg.find("name=") > -1:
                                name = cfg.split('=')[-1]

                    # Find the game version and mod loader used for this instance
                    game_version = ''
                    loader = ''
                    with open(i.path + "/mmc-pack.json") as f:
                        mmc_pack = json.loads(f.read())
                        for component in mmc_pack["components"]:
                            match component["cachedName"]:
                                case "Minecraft": game_version = component["version"]
                                case "Fabric Loader": loader = "fabric"
                                case "Forge": loader = "forge"
                                case "Quilt Loader": loader = "quilt"

                    # Export data to a new Instance
                    self.instances.update({name: Instance.Instance(i.path + "/.minecraft", name, game_version, loader)})

    def __repr__(self):
        return str(self.instances)


if __name__ == "__main__":
    multimc_manager = MultiMC()
    print(multimc_manager)
