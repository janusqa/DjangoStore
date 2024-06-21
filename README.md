### Quickstart
- from vscode install these extensions
  - Python
  - Python Debugger
  - Black Formatter
  - autopep8
  - Django (by baptiste Darthenay)
- Set up black or autopep8 in .vscode/settings.json
- Set up Django (by baptiste Darthenay) in .vscode/settings.json
- python3 -m venv venv
- source venv/bin/activate
- pip install -U pip setuptools wheel
- python3 -m pip install Django

### Projects
- django-admin startproject <[myproject]>
- cd <[myproject]>
- python manage.py runserver 8000 #8000 is the default port

### Scaffold a site
- in the <[myproject]>/<[myproject]>/urls.py folder add your pages to urlpatterns
- now create in same folder a views.py to hold your views (these are controllers)
- back up one folder create a templates folder in same dir as manage.py to hold your html templates
- go down one directory again to settings.py. Find "TEMPLATES" array, and in the "DIRS" array spcify your templates directory as "templates:
- now open the views.py to connect up our templates
  
### CSS
- opening settings and in the top "import os"
- Under STATIC_URL add a "STATICFILES_DIRS" array varible and add to it the location of the static folder you created.
- now in your html templates you can add your style sheets

### Apps
- within a project we can have many apps.  An app is like a classlib in c#. We can reuse them across multiple projects
- python manage.py startapp posts # to create an app within a project
- next as in c# we have to add our "classlib" aka app to the "solution" aka project. open settings.py in main project folder, scroll to "INSTALLED_APPS", and add the foldername for your app to the existing list of apps there.
- Each app can have its own templates/<[app_name]> folder to host templates specific to it
- Now create a urls.py inside the posts app dir that will be used to link up the templates for this app and make them accessible via views.py
- Will need to connect this back up in the urls.py of the main project. It's somewhat like node js router/controller patter

### DB Migrations
- python manage.py makemigrations # scaffold any changes to Models into a migration. Similar to "dotnet ef migrations add" command in c#
- python manage.py migrate # Apply any changes in scaffoled migrations. Simlar to "dotnet ef database update" command in c#

### Python/Django shell
- python manage.py shell # start a python/django shell

### Django Admin
- python manage.py createsuperuser # create credentials to access Django Administration
- Access admin via localhost:8000/admin and login with your freshly minted credentials
- We get Groups and Users for free.  To Add aditional models, need to set them up in admin.py which is in for example the root of an app folder

### IMAGES via Admin
- add MEDIA_URL and MEDIA_ROOT to settings.py in main project folder
- configure urlpatterns in urls.py with these 
- install Pillow ($ pip install Pillow). Remember to do this within your virtual env
- Now for example in the Post model we can add an image field
  
### settings.py
- no longer need to import os, so remove it
- Set DEBUG to False when deploying
- populate ALLOWED_HOSTS with the hosts that can access your django
- run "$ python manage.py collectstatic". This is useful for deployment scenarios. It pull all your static content together and places it in the specified "assets" folder