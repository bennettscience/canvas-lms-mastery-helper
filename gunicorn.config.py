import multiprocessing
import os
from dotenv import load_dotenv

for env_file in ('.env', '.flaskenv'):
    env = os.path.join(os.getcwd(), env_file)
    if os.path.exists(env):
        load_dotenv(env)

# Run multiple processes
workers = 2
bind = '127.0.0.1:8080'
umask = 0o007

# Logging settings
capture_output = True # Capture print statements
accesslog = '-' # Set access log location. Needs an absolute path
errorlog = '-' # Set error log location. Needs an absolute path
loglevel = 'debug' # Decrease log level in prod. Defaults to 'error'