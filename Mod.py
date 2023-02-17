import hashlib
import os
import re
import time

import requests


class ModNotFoundException(Exception):
    def __init__(self, what):
        super().__init__(what)


class ModrinthRequestException(Exception):
    def __init__(self, what):
        super().__init__(what)


def make_modrinth_request(request, wait_on_ratelimit_error=True):
    try:
        result = requests.get("https://api.modrinth.com/v2/" + request).json()
    except requests.JSONDecodeError:
        raise ModrinthRequestException("Invalid Modrinth request: https://api.modrinth.com/v2/" + str(request))
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
        try:
            self._version = make_modrinth_request("version_file/" + self.hash + "?algorithm=sha512")
        except ModrinthRequestException:
            raise ModNotFoundException(jar + " cannot be found on Modrinth.")
        self._project = make_modrinth_request("project/" + self._version["project_id"])

    def __repr__(self):
        return self._project["title"] if self._project is not None else ''

    def update(self, instance):
        versions = self._project["versions"]
        filename = self._version["files"][0]["filename"]
        for version in versions[-1:versions.index(self._version["id"]):-1]:
            version = make_modrinth_request("version/" + version)
            if instance.is_compatible_with(version):
                path = instance.path + "/mods/"
                url = version["files"][0]["url"]
                with open(path + version["files"][0]["filename"], "wb") as f:
                    f.write(requests.get(url).content)
                os.rename(path + filename, path + filename + ".disabled")
                old_version = self._version
                self._version = version
                return str(self) + " : " + old_version["version_number"] + " -> " + version["version_number"]
        return False
