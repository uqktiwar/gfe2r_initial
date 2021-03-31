# gfe2r_initial

Pre-req:
In this section, you’ll be installing the prerequisites needed before you can bootstrap your project, such as Python 3.
Installing Python 3

There is a big chance that you already have Python 3 installed on your system. If you don’t, you can simply head to the official website
https://www.python.org/downloads/  and download the binaries for your operating system.
Depending on your system, you may also be able to install Python 3 or upgrade it to the latest version if it’s already installed by using the official package manager.
If you have a problem installing Python 3 or want more information, you can check the Python 3 Installation & Setup Guide https://realpython.com/installing-python/, which provides different ways to install Python 3 on your system.

Finally, you can check if you have Python 3 installed by running the following command:
$ python3 --version

Installing Django
Django is the most popular Python framework for building web apps. It’s free, open source and written in python. Django offers a big collection of modules which you can use in your own projects. It makes it easy for developers to quickly build prototypes by providing a plethora of built-in APIs and sub-frameworks such as GeoDjango. 
The Django package is available from the Python Package Index (PyPI)
https://pypi.org/ so, you can simply use pip to install it by running the following command in your terminal:

$ pip install django
or $ pip install django  --upgrade (if already installed)

To run the website:
Download the project folder

In your terminal, CD into the rootProject folder and run:
	Python manage.py runserver
The application will be hosted at localhost:8000
