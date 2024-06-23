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
- pip freeze > requirements.txt # save project dependancies
- pip install -r requirements.txt # restore project dependancies

### Django debug toolbar
- https://django-debug-toolbar.readthedocs.io/en/latest/installation.html 
- $ pip install django-debug-toolbar Now
-  add it to INSTALLED_APPS in settings.py in primary folder 
-  add a url pattern to urls.py in primary folder path('debug/', include(debug_toolbar.urls))

### Projects
- django-admin startproject <[myproject]> 
- cd <[myproject]>
- OR 
- django-admin startproject <[myproject]> .  # to create the project right in your current folder instead of a project sub-folder
- python manage.py runserver 8000 #8000 is the default port

### Scaffold a site
- in the <[myproject]>/<[myproject]>/urls.py folder add your pages to urlpatterns
- now create in same folder a views.py to hold your views (these are controllers)
- back up one folder create a templates folder in same dir as manage.py to hold your html templates
- go down one directory again to settings.py. Find "TEMPLATES" array, and in the "DIRS" array spcify your templates directory as "templates:
- now open the views.py to connect up our templates

### STATIC FILES
- configure static and media in settings.py
    ```
    MEDIA_URL = "media/"
    MEDIA_ROOT = BASE_DIR / "media"
    STATIC_URL = "static/"
    STATICFILES_DIRS = [BASE_DIR / "static"]
    STATIC_ROOT = BASE_DIR / "assets"
    ```
- make sure you create a static folder and media folder in project root
- staic folder holds items like css/js etc
- configure the urls for these also in urls.py
    ```
    from django.urls import path, include, re_path
    from django.conf.urls.static import static
    from django.conf import settings
    from django.views.static import serve
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    ```
- now run the command "$ python manage.py collectstatic"

  
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
- !!!IMPORTANT!!!! when seting your routs in the path params in urls.py ALWAYS USE A TRAILING SLASH!!!! eg. path("new-post/", views.new_post, name="new-post") AND NOT path("new-post", views.say_hello, name="hello"),
- Will need to connect this back up in the urls.py of the main project. It's somewhat like node js router/controller patter

### DB Migrations
- python manage.py makemigrations # scaffold any changes to Models into a migration. Similar to "dotnet ef migrations add" command in c#
- python manage.py migrate # Apply any changes in scaffoled migrations. Simlar to "dotnet ef database update" command in c#
- revert a migration by migrating to a previous migration eg. "python manage.py migrate store 0003"

### custom migrations
- create empty migration $ python manage.py makemigrations store --empty
- in the newly created migrations file in the operations array eg. 
- operations = [ 
    migrations.RunSQL( """ INSERT INTO store_collection (title) VALUES ("collection1") """, """ DELETE FROM store_collection WHERE title="collection1" """ ) 
  ] 
  NOTE: the second arg to RunSQL is a sql statment that reverts the first statement. We need it so we can use migrations to revert. The first arg migrates forwards to the new state of the db, the second arg migrates backward to the past state of the db

### Python/Django shell
- python manage.py shell # start a python/django shell

### Django Admin
- python manage.py createsuperuser # create credentials to access Django Administration
- python manage.py changepassword <[username]> # reset a password for existing user 
- Access admin via localhost:8000/admin and login with your freshly minted credentials
- We get Groups and Users for free.  To Add aditional models, need to set them up in admin.py which is in for example the root of an app folder
- Customize Admin Site title by setting "admin.site.site_header" in main project "urls.py"
- Customize Admin index page title by setting "admin.site.index_title" in main project "urls.py"
- Remember to overrid the __str__ method of models so when they are displayed in the Admin UI they look friendly and human readable
- You can also customize how objects are displayed by providing a nested Meta class to for example sort objects when they appear in the admin UI
- You can also display how the list is displayed, for example add additional columns. See "admin.py" in store for an example with ProductAdmin class used to  customize Product listing. Basically create a class and pass this class while registering model in admin
- Computed columns are supported. See Inventory Status example with ProductAdmin
- Can add related fields to the listing. See ProductAdmin example. We can also show a particular field of the related object. It's in the example implemented by using a method called collection_title
- Can override base query using "get_queryset". See CollectionAdmin
- Add links to related objects/fields in a list. See CollectionAdmin
- Can specify what columns to search by in a list. See CustomerAdmin
- Can configure filter for columns. Custome filters included for custom columns you added. See ProductAdmin.
- Add custom actions. Every list comes with a free DELETE action. See ProductAdmin.
- Can customize the forms objects in the admin. As an example we will auto-fill the slug field of the product object when we enter a title
- Enable data valadation. See Product Mode -> unit_prices where we validate that unit price must be in a certain range of values, that is -1 or 0 is not allowed as a price
- Enable parent page to display its related child items. Example on the order form page, display an editable list of order items. This is powerfull.  See "OrderItemInline" and "OrderAdmin" -> "inlines" in admin.py
- Add a generic relationship to a form. Example allow tags to be addes while on the add product form. See ProductAdmin. In this example we introduced tight coupling between the store app and the tags app. BAD!!! We fix this by creating a mdeiator app called store_custom which knows about both the store and the tags app. This store_custom will only be used in this project there by keeping tags and store app dependant of each other using store_custom as the shim to unite them when needed. We orginally had TagInline class in store we now move in to admin.py in store_custom. Do not forget to register this new app in settings.py. Now if we remove store_custom from settings.py and view add product form page we see the page without the CustomProductAdmin which configures the tag items to be shown as children, and if we add it back then that taggedItem section reappears. Nifty.

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