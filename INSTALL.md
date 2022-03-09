# Installation

This is a web application, meaning you'll need a web server (local or
cloud-based) in order to run your own installation. The steps below will help
you get your own copy configured on most Linux-based servers.

## Requirements

-   Web server (Apache/Nginx)
-   Python 3.8+
-   MySQL or MariaDB
-   git

## A note on security

You should take standard steps to secure your web server. That process is
outside the scope of this section, but
[Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-install-the-apache-web-server-on-ubuntu-18-04)
has a good starter guide for setting up Apache on a Ubuntu server.

### SQL

You'll need a SQL database to store data from Canvas. This is preconfigured for
MySQL (MariaDB) but any SQL schema should work. Set up your database and note
your username and password.

## Source

-   Log into your host and navigate to your web root directory
-   Clone this repository
    -   `git clone https://github.com/bennettsience/canvas-lms-mastery-helper masteryhelper && cd masteryhelper`

It is recommended that you use a virtual environment to manage your
dependencies. After creating your environment, you can install dependencies
using `poetry install` or `pip install -f requirements.txt`.

## Config

The repo comes with a sample config file. Make a copy with
`cp config.sample.py config.py`. You'll need to set up your database using the
credentials you created earlier.

By default, the application will run with a SQLite database, which works fine
for single users. But, if you want to make it available to more than one person,
you'll need to change your database engine.

Set your database credntials in the `SQLALCHEMY_DATABASE_URI` key and save the
file. SQLAlchemy
[has comprehensive docs](https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/)
on configuration options.

Once your dependencies are installed and your config is updated, you can set up
your database:

```bash
flask db upgrade
flask seed
```

## Canvas Keys

### Developer Key

Users will authenticate via Canvas' OAuth endpoints, which provisions
authorization tokens for the session. You will need to create a Developer Key in
your Canvas Admin settings to allow access.

1. Log into your instance of Canvas and open the Admin tools.
2. In Developer Keys, create a new key with the following settings:
    - Name (displays on the login page)
    - Owner email
    - Redirect URI
        - Use _https://your-domain.com/auth/callback_
    - Client Credentials Audience
        - _Canvas_

### Scoping

Enforcing scopes is always a good idea. Enable the following:

-   Assignments
    -   url:GET/api/v1/courses/:course_id/assignments
    -   url:GET/api/v1/courses/:course_id/assignments/:id
-   Courses
    -   url:GET|/api/v1/courses
    -   url:GET|/api/v1/courses/:id
    -   url:GET|/api/v1/users/:user_id/courses
-   Enrollments
    -   url:GET|/api/v1/courses/:course_id/enrollments
-   Outcome Groups
    -   url:GET|/api/v1/courses/:course_id/outcome_group_links
-   Outcome Results
    -   url:GET|/api/v1/courses/:course_id/outcome_results
-   Outcomes
    -   url:GET|/api/v1/outcomes/:id
-   Submissions
    -   url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/submissions
    -   url:GET|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id
    -   url:PUT|/api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id

When you create they key, copy the **Client ID** and **Client Secret**.

### Optional: Standalone Access Token

If you want to set up a cron job to pull in Outcome Results nightly from Canvas,
you'll need to set up an Access Token for a user with admin permissions. Create
the token with the same authorization scopes. Save the key that is generated.

## .env Configuration

In your server, run `cp .flaskenv.sample .flaskenv` to generate your environment
file. Then, edit the following fields:

```text
CANVAS_URI='https://your-domain.instructure.com/'
CANVAS_KEY='your-standalone-access-token'
CANVAS_OAUTH_APP_ID='your-developer-key-client-ID'
CANVAS_OAUTH_APP_SECRET='your-developer-key-secret'
CANVAS_OAUTH_CALLBACK_URI='https://your-domain.com/auth/callback'
```

### Notes

-   Your `CANVAS_OAUTH_CALLBACK_URI` must match the callback URI you used in the
    Developer Key settings.
-   The `CANVAS_OAUTH_CALLBACK_URI` must use SSL.

## gunicorn configuration

Gunicorn is a [WSGI server](https://wsgi.readthedocs.io/en/latest/what.html)
which handles communication from your HTTP server to Python. It has it's own
configuration file which helps you control application logging and performance.

On your server, run `cp gunicorn.sample.py gunicorn.config.py` and edit the
following fields:

```python
import multiprocessing
import os
from dotenv import load_dotenv

for env_file in ('.env', '.flaskenv'):
    env = os.path.join(os.getcwd(), env_file)
    if os.path.exists(env):
        load_dotenv(env)

# Run multiple processes
workers = 2
# Edit if you want to run on a different port
bind = '127.0.0.1:8080'
umask = 0o007

# Logging settings
accesslog = '-' # Set access log location. Needs an absolute path
errorlog = '-' # Set error log location. Needs an absolute path
loglevel = 'debug' # Decrease log level in prod. Defaults to 'error'
```

## Apache configuration

Apache can be used as a reverse proxy to route traffic from the Internet to your
gunicorn application server. There are a number of detailed examples on the
Internet, including the
[official Apache documentation](https://httpd.apache.org/docs/2.4/howto/reverse_proxy.html).
Here is a sample `VirtualHost` entry showing the basics.

_Note that this needs to be modified slightly to allow HTTPS access._

```text
<VirtualHost *:80>
    ServerName www.mydomain.com
    DocumentRoot /your/install/directory

    Alias /static "/your/install/directory/app/static"
    <Directory /your/install/directoryt>
        Allow from all
        Require all granted
    </Directory>

    # Do not proxy requests to /static
    ProxyPass /static !

    # Route everything else to gunicorn.
    # Make sure to update your URL to match your gunicorn bound address
    ProxyPass / http://127.0.0.1:8080
    ProxyPassReverse / http://127.0.0.1:8080
</VirtualHost>
```
