from source.meta.common import common


class PluginsParent():
    # plugins object
    def __init__(self):
        # self.plugins is a list
        self.plugins = []

    # getter
    def get_plugins(self):
        return self.plugins

    # setter
    def set_plugins(self, plugins):
        self.plugins = plugins


def main():
    print(f"Called main() on utility library {__file__}")

if __name__ == "__main__":
    main()
