import os
import pprint

import source.snes.zelda3.link.sprite as link_sprite_library
import source.snes.metroid3.samus.sprite as samus_sprite_library

data = {
    "metroid3": {"samus": {}},
    "zelda3": {"link": {}}
}

for gameID in ["metroid3", "zelda3"]:
    for spriteID in ["samus", "link"]:
        spritePath = os.path.join("snes", gameID, spriteID)
        if os.path.exists(
            os.path.join("resources", "app", spritePath)
        ):
            data[gameID][spriteID] = {
                "input": {
                    "filepath": spritePath
                },
                "output": {}
            }
            # ZSPR, PNG, RDC
            filexts = ["zspr", "png", "rdc"]
            for filext in filexts:
                sheetsPath = os.path.join(
                    "resources", "app", spritePath, "sheets")
                if os.path.exists(
                    os.path.join(
                        sheetsPath,
                        f"{spriteID}.{filext}"
                    )
                ):
                    outputPath = sheetsPath.replace(
                        "app", "user").replace("sheets", "output")
                    if not os.path.exists(outputPath):
                        os.makedirs(outputPath)
                    data[gameID][spriteID]["input"][filext] = os.path.join(
                        sheetsPath,
                        f"{spriteID}.{filext}"
                    )
                    data[gameID][spriteID]["output"][filext] = os.path.join(
                        outputPath,
                        f"{spriteID}.{filext}"
                    )


class Audit():
    def same(self, file1, file2):
        return file1.read() == file2.read()

    def test_export(self, gameID, spriteID, filext):
        spriteLibrary = None
        if gameID == "zelda3" and spriteID == "link":
            spriteLibrary = link_sprite_library
        elif gameID == "metroid3" and spriteID == "samus":
            spriteLibrary = samus_sprite_library

        if filext in data[gameID][spriteID]["input"]:

            sprite = {
                "import": {
                    filext: spriteLibrary.Sprite(
                        data[gameID][spriteID]["input"][filext],
                        {"name": "Link"},
                        data[gameID][spriteID]["input"]["filepath"]
                    )
                },
                "export": {}
            }
            sprite["import"][filext].metadata = {
                "sprite.name": spriteID.capitalize(),
                "author.name": "Nintendo",
                "author.name-short": "Nintendo"
            }
            if filext == "zspr":
                sprite["export"][filext] = sprite["import"][filext].save_as_ZSPR(
                    data[gameID][spriteID]["output"][filext])
            elif filext == "png":
                sprite["export"][filext] = sprite["import"][filext].save_as_PNG(
                    data[gameID][spriteID]["output"][filext])
            elif filext == "rdc":
                sprite["export"][filext] = sprite["import"][filext].save_as_RDC(
                    data[gameID][spriteID]["output"][filext])

            file = {
                "import": {
                    filext: open(data[gameID][spriteID]["input"][filext], "rb")
                },
                "export": {
                    filext: open(data[gameID][spriteID]
                                 ["output"][filext], "rb")
                }
            }
            print(
                f"{filext.upper()}s",
                self.same(
                    file["import"][filext],
                    file["export"][filext]
                )
                and "do"
                or "don't",
                "match"
            )


class LinkAudit(Audit):
    def test_link_export(self, filext):
        self.test_export("zelda3", "link", filext)

    def test_link_exports(self):
        print("Zelda3/Link")
        for filext in [
            "zspr",
            # "rdc",
            "png"
        ]:
            self.test_link_export(filext)
        print("")


class SamusAudit(Audit):
    def test_samus_export(self, filext):
        self.test_export("metroid3", "samus", filext)

    def test_samus_exports(self):
        print("Metroid3/Samus")
        for filext in [
            "zspr",
            # "rdc",
            "png"
        ]:
            self.test_samus_export(filext)
        print("")


if __name__ == "__main__":
    la = LinkAudit()
    la.test_link_exports()

    sa = SamusAudit()
    sa.test_samus_exports()
