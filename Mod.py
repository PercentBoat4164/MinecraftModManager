import math
import os
import re
import modrinth
import requests


class ModNotFoundError(Exception):
    def __init__(self, what, mapped):
        super().__init__(what)
        self.mapped = mapped


class Mod:
    @staticmethod
    def _generate_word_lists():
        with open("wordsByFrequency.txt", 'r') as words_file:
            _words = words_file.read().split()
            word_num = len(words_file.read().split())
        _word_cost = {k: math.log((i + 1) * math.log(len(_words))) for i, k in enumerate(_words)}
        _max_word = max(len(x) for x in _words)
        return _word_cost, _max_word

    _jar_mod_name_matcher = re.compile("^.+?(?=-mc[\d]|-[\d]|_mc[\d]|_[\d])")
    _jar_mod_name_character_filter = re.compile("-(?:fabric)?|_(?:fabric)?")
    _word_cost, _max_word = _generate_word_lists()

    @classmethod
    def _infer_spaces(cls, s):
        """Uses dynamic programming to infer the location of spaces in a string
        without spaces."""

        # Find the best match for the i first characters, assuming cost has
        # been built for the i-1 first characters.
        # Returns a pair (match_cost, match_length).
        def _best_match(i):
            candidates = enumerate(reversed(cost[max(0, i - cls._max_word):i]))
            return min((c + cls._word_cost.get(s[i - k - 1:i], 9e999), k + 1) for k, c in candidates)

        # Build the cost array.
        cost = [0]
        for i in range(1, len(s) + 1):
            c, k = _best_match(i)
            cost.append(c)

        # Backtrack to recover the minimal-cost string.
        out = []
        i = len(s)
        while i > 0:
            c, k = _best_match(i)
            assert c == cost[i]
            out.append(s[i - k:i])
            i -= k

        return " ".join(reversed(out))

    def __init__(self, jar):
        filename = jar.split('/')[-1]
        # Get the search keyword from the jar's filename
        keywords = self._jar_mod_name_character_filter.sub('', self._jar_mod_name_matcher.match(filename.lower())[0])

        # Get the top search result
        self._project = next(iter(modrinth.Projects.Search(keywords, project_types=['mod'], limit=1).hits or []), None)

        # If no mod was found, try again with inferred spaces
        if self._project is None:
            keywords = self._infer_spaces(keywords)
            self._project = next(iter(modrinth.Projects.Search(keywords, project_types=['mod'], limit=1).hits or []),
                                 None)
            if self._project is None:
                raise ModNotFoundError("The mod '" + jar + "' could not be mapped to any mod available on Modrinth.", False)

        # Verify that the jar file specified actually exists under one of the versions
        versions = self._project.versions
        versions.reverse()
        self._version = None
        for version in versions:
            version = self._project.getVersion(version)
            if version.files[0]["filename"] == filename:
                self._version = version
                break

        # Log the associations
        if not self._version:
            raise ModNotFoundError("The mod '" + jar + "' mapped to '" + str(self) + "' but no matching file exists.", self._project.name)

    def __repr__(self):
        return self._project.name if self._project is not None else ''

    def update(self, instance):
        versions = self._project.versions
        filename = self._version.files[0]["filename"]
        print("Attempting upgrade for '" + str(self) + "'@'" + filename + "'.")
        for version in versions:
            version = self._project.getVersion(version)
            version_file = version.files[0]["filename"]
            print(version_file)
            if filename == version_file:
                print(str(self), "is up-to-date already.")
                return
            elif instance.is_compatible_with(version):
                path = instance.path + "/mods/"
                url = version.getDownload(version.getPrimaryFile())
                with open(path + version_file, "wb") as f:
                    f.write(requests.get(url).content)
                os.rename(path + filename, path + filename + ".disabled")
                print("Updated", str(self) + ".")
                return
        print("Something went very wrong. No newer version was found, but neither was the current version!")