import pycurl
import os
import time
import cStringIO
import datetime
import re


interrupt_check_url = "http://169.254.169.254/latest/meta-data/spot/termination-time"

def check_if_migration_needed():
  buffer = cStringIO.StringIO()
  c = pycurl.Curl()
  az=get_az()
  c.setopt(c.URL, 'xxxx/fetch/migration?az=%22'+az+'%22')
  c.setopt(c.WRITEDATA, buffer)
  c.perform()
  c.close()
  body = buffer.getvalue()
  return body
def check_if_interrupted() :
  buffer = cStringIO.StringIO()
  c = pycurl.Curl()
  c.setopt(c.URL, interrupt_check_url)
  c.setopt(c.WRITEDATA, buffer)
  c.perform()
  c.close()
  body = buffer.getvalue()
  return bool(re.search('.*T.*Z', body))

def get_az() :
  buffer = cStringIO.StringIO()
  c = pycurl.Curl()
  c.setopt(c.URL, 'http://169.254.169.254/2016-09-02/meta-data/placement/availability-zone')
  c.setopt(c.WRITEDATA, buffer)
  c.perform()
  c.close()
  body = buffer.getvalue()
  return body

def make_migration_notice():
  path="/tmp/migration"
  os.mkdir(path,0755);

instance_time = None
buf = cStringIO.StringIO()
c=pycurl.Curl()
c.setopt(c.URL, 'https://xxxxx/fetch/')
c.setopt(c.WRITEFUNCTION, buf.write)
c.perform()
instance_running_time=buf.getvalue()
instance_running_time=instance_running_time[:-1]
instance_running_time=instance_running_time[1:]
c.close()

print "instance_running_time is"
print instance_running_time
print "instance's running time in seconds"
instance_running_time_seconds=time.mktime(datetime.datetime.strptime(instance_running_time, "%Y-%m-%d %H:%M:%S").timetuple())
print instance_running_time_seconds
flag=0
while True:
  time.sleep(5)
  elapsed=(int(time.time()-instance_running_time_seconds))
  print "elapsed time in seconds"
  print (elapsed)
  print "elapsed time in minutes"
  print (elapsed/60)
  elapsed_minutes=int(elapsed/60)
  if (elapsed_minutes-55) % 60 == 0 and flag==0:
    result=check_if_migration_needed()
    if(result=="true"):
      make_migration_notice()
      break
    flag=1
  elif (elapsed_minutes-55) % 60 != 0 and flag==1:
    flag=0
  elif (check_if_interrupted()):
    make_migration_notice()
    break