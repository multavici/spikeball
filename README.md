# Spikeball Gent Website

## After cloning
The first thing to do is to set all the relevant environment variables.
Luckily, flask has an easy way of setting those: the `.flaskenv` file. Copy the
`.flaskenv-example` file to `.flaskenv` and change the parameters accordingly.
Be sure to set
```
    FLASK_ENV=production
```
in a production environment.

## Running the app

After the environment is set, the app can be run.

### Flask shell
In stead of just typing `python` when one needs to spawn a python shell to test
things out, it is recommended to type
```
    flask shell
```
this way, all useful variables are already imported.

### In development
Make a flask environment file `.flaskenv` with all the environment variables of
your project. Set `FLASK_ENV=development` and run the app with
```
    flask run
```

### In production
Run flask with *Gunicorn* and *Nginx*.  An example Gunicorn service file can be
found [here](spikeball.service). This file should be saved as
```
    /etc/systemd/system/spikeball.service
```
and can be enabled and started as follows:
```
    sudo systemctl enable spikeball
    sudo systemctl start spikeball
```
An example Nginx proxy file can be found [here](spikeball.nginx) and should
be saved as
```
    /etc/nginx/sites-available/spikeball
```
to enable the website, this file should be statically linked to `/etc/nginx/sites-enabled`.
do not forget to test and restart the Nginx service:
```
    sudo nginx -t
    sudo systemctl restart nginx
```
The example nginx file already assumes you installed and enabled **certbot**.
