import hashlib
import os
import re
import time
import requests


class ModNotFoundError(Exception):
    def __init__(self, what, mapped):
        super().__init__(what)
        self.mapped = mapped


def make_modrinth_request(request, wait_on_ratelimit_error=True):
    try:
        result = requests.get("https://api.modrinth.com/v2/" + request).json()
    except requests.JSONDecodeError:
        raise Exception("Invalid Modrinth request: " + str(request))
    if "error" in result.keys():
        if result["error"] == "ratelimit_error":
            print(result["description"])
            time.sleep(int(re.search("(\d\d) second", result["description"]).group(1)) + 1)
            return make_modrinth_request(request, wait_on_ratelimit_error)
    return result


class Mod:
    def __init__(self, jar):
        with open(jar, 'rb') as f:
            hasher = hashlib.sha512(f.read())
        self.hash = hasher.hexdigest()
        self._version = make_modrinth_request("version_file/" + self.hash + "?algorithm=sha512")
        self._project = make_modrinth_request("project/" + self._version["project_id"])

    def __repr__(self):
        return self._project["title"] if self._project is not None else ''

    def update(self, instance):
        versions = self._project["versions"]
        filename = self._version["files"][0]["filename"]
        print("Attempting upgrade for '" + str(self) + "'@'" + filename + "'.")
        for version in versions[-1:versions.index(self._version["id"]):-1]:
            version = make_modrinth_request("version/" + version)
            if instance.is_compatible_with(version):
                path = instance.path + "/mods/"
                url = version["files"][0]["url"]
                with open(path + version["files"][0]["filename"], "wb") as f:
                    f.write(requests.get(url).content)
                os.rename(path + filename, path + filename + ".disabled")
                print("Updated", str(self) + " to " + version["version_number"] + ".")
                return
        print(str(self) + " is already up-to-date.")