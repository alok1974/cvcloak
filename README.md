# cvcloak

Invisible cloak (a la Harry Potter) implemented in opencv.

![cvcloak.png](https://github.com/alok1974/cvcloak/blob/master/cvcloak.png)

## Installing
```
$ git clone git@github.com:/alok1974/cvcloak.git
$ cd cvcloak
$ pip install .
```


## Run
1. Start the app on a desktop / laptop with a web cam. Stay away from the camera.
```
$ cvcloak
```
2. The app will take a few seconds to capture the background. Camera feed will be displayed after that. A static background will yield good results.
3. Any bright red colored object that enter the screen now will appear transparent.
4. To change the detection color, open calibration and change the master hue.


Enjoy!