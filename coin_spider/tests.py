import os
import sys
import time
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'coin_helper.settings'
django.setup()

print(time.time())
print(time.strftime("%Y-%m-%d %H:%M:%S"))
print(os.environ)