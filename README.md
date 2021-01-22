# ILIAD

A simple and easy ilias downloader written with python. It helps you to download files on ilias to your computer.


![Title](https://github.com/cold-soda-jay/iliaD/blob/master/pic/title.png?raw=true)

> **Important:** The project is now only support Ilias platform of ***Karlsruhe Institut für Technologie***.


## Install 

```
$ pip install iliaDownloader

$ iliaD
```


</br>

**&diams; Requirement if using source code**

```python
beautifulsoup4==4.9.0
bs4==0.0.1
requests==2.23.0
urllib3==1.25.9
soupsieve==2.0
texttable==1.6.2
```
## Usage

</br>

**&diams; Initiate**

``iliaD init`` 

or

``iliaD init -name uxxxx -target path/of/target``

For the first time to use you should use command ``init`` to initiate the user information. Follow the constructions you can set your user name in form "**uxxxx**", the **password** and the path of **target directory**.

``iliaD course``


After user data initiated, you can use command ``course`` to choose courses to be downloaded. Or you can use command ``sync`` to choose courses and download the directly.

</br>

**&diams; Synchronize**

``iliaD sync``

Use command ``sync`` you can synchronize new files. The exist file will not be changed. Only new file in ilias will be downloaded to the folder.

</br>

**&diams; Check user data and edit**

``iliaD user``

or

``iliaD course``

Use command ``user`` to check and edit the user name, target directory and password. Use command ``course`` to check and edit marked courses.


## Commands

|Command | Usage |
|:-:|:-:|
| ``init`` |Init user config with name and target folder |
|``sync`` |Synchronize all marked Ilias files |
|``user`` | Print or change user data|
|``course`` |Print or change marked courses |


## Automatic daliy synchronize

If you have a raspberry pi or any Unix computer, you can do the following instructions to synchronize the ilias folder with your cloud storage.

1. Download the [iliaD](https://github.com/cold-soda-jay/iliaD) .
2. Download [rclone](https://rclone.org/) .
3. Bind rclone with your cloud storage.
4. Initiate the iliaD, set the target directory (e.g. ``/home/pi/Onedrive/SS20/``)
5. Open crontab: with ``crontab -e`` in terminal
6. Add following instructions:
    1. ``00 05 * * * iliaD sync >> /path/of/iliaD.log 2>&1``
    2. ``30 05 * * * rclone -v copy path/of/target/directory/ path_of_cloud >> path/of/rclone.log 2>&1``

With the seetings, your raspberry pi will synchronize the ilias folder, download new files at 5:00 am. and upload them in your cloud storage at 5:30 am.

