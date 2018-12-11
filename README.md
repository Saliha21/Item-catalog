# Udacity Item Catalog App
* This application provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.


## Getting Started
### How to use it
You will need to install these application.
* Flask 
```sh
$ pip install flask
```
* sqlalchemy
```sh
$ pip install flask sqlalchemy
```
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/downloads.html)

### Running

* install Vagrant and VirtualBox
* Clone the fullstack-nanodegree-vm
* Run vagrant up to run the virtual machine, then vagrant ssh to login to the VM
* use the following line to get into the vagrant VM folder
```sh
$ cd /vagrant
```
* Use the command line to get in to the folder you just downloaded
* Then you can run this command
```sh
$ python db.py
```
* After it added items succesfully, you can run the following command
```sh
$ python project.py
```
* go to [this link](http://localhost:5000/catalogs) to access the application.
 

## JSON Endpoints:
* Returns JSON of all items in catalog
<img src="https://github.com/Saliha21/image/blob/master/endpo1.png" width="500" height="130">
* Returns JSON of selected item in catalog
<img src="https://github.com/Saliha21/image/blob/master/endpo2.png" width="500" height="130">
* Returns JSON of all categories in catalog
<img src="https://github.com/Saliha21/image/blob/master/endpo3.png" width="500" height="130">
