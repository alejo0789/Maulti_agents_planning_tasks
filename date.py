import datetime

d=datetime.datetime.strptime("2011-01-21 02:37:21", "%Y-%m-%d %H:%M:%S") #Get your naive datetime object
d=d.replace(tzinfo=datetime.timezone.utc) #Convert it to an aware datetime object in UTC time.
d=d.astimezone() #Convert it to your local timezone (still aware)
print(d.strftime("%d %b %Y %I:%M:%S %p")) #Print it with a directive of choice