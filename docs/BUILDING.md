# Building SpriteSomething from source

1. Get [python](http://python.org/downloads)
1. Get the [SpriteSomething source code](https://github.com/Artheau/SpriteSomething/archive/master.zip)
1. Install Platform-specific dependencies
1. Install python dependencies
1. Run `python -m unittests` (*optional*)
1. Run `./source/meta/build.py`
1. Run `SpriteSomething` (`.exe` if Windows)

## Platform-specific dependencies

### Windows

* Get [get-pip.py](https://bootstrap.pypa.io/get-pip.py)
* Run `get-pip.py`
* Upgrade pip: `python -m pip install --upgrade pip`

## Python dependencies

* `pip install -r "./resources/app/meta/manifests/pip_requirements.txt"`
  * pillow
  * numpy==1.16.4
  * pyinstaller

* *Note: Windows uses `pip` while Linux and MacOSX use `pip3`. `numpy`, as of version 1.17, has an error that is incompatible.*
