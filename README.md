# VM Manager

## Asyncronous API prototype for managing virtual machines via libvirt

**WARNING**: It uses SQLite as main DB (in purposes of fast delevepment)! SQLite has a one-threaded blocking engine. So use it carefully.

### Requirements:

- libvirt-python==1.3.3
- marshmallow==2.7.1
- tornado==4.3

### Run:

Note that virtual environment created via pyenv, so it must be installed in your system already.

```shell
$ cd vm-manager-proto
$ pyenv virtualenv 3.5.1 vm-manager-proto
$ pyenv local vm-manager-proto
$ pip install -r requirements.txt
$ PYTHONPATH=. python app.py
```