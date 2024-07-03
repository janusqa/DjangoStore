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

### CORS
- install django-cors-headers
  - pip install django-cors-headers
  - in settings add to INSTALLED_APPS
  - Register middleware "corsheaders.middleware.CorsMiddleware" above "django.middleware.common.CommonMiddleware"
  - add "CORS_ALLOWED_ORIGINS" to  settings.py and specify what should be able to access this apis

  
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
- Add a generic relationship to a form. Example allow tags to be addes while on the add product form. See ProductAdmin. In this example we introduced tight coupling between the store app and the tags app. BAD!!! We fix this by creating a mdeiator app called "core" which knows about both the store and the tags app. This "core" will only be used in this project there by keeping tags and store app dependant of each other using "core"  as the shim to unite them when needed. We orginally had TagInline class in store we now move in to admin.py in "core". Do not forget to register this new app in settings.py. Now if we remove "core"  from settings.py and view add product form page we see the page without the CustomProductAdmin which configures the tag items to be shown as children, and if we add it back then that taggedItem section reappears. Nifty.

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

### Django REST Api
- pip install djangorestframework
- add to apps in settings.py of main project "rest_framework"
- additionaly in settings customize the framework via "REST_FRAMEWORK" variable
  - by default the framework retuns numbers as strings. We can disable this via customizing the framework. See an example in settings.py
- pip install drf-nested-routers # to get nested route funtionality like https://localhost/products/1/reviews/1
- views.py contain our controllers
- urls.py contain our enpoints
- Create serializers (aka DTOs) for any model we want to return from the api.
- Order of creating a api segment
  - Create the model
  - Create the Serializer
  - Create the View/ViewClass/ViewSet
  - Create the router/nested router
- Filtering. To cut down on writing code to filter in api use django-filter
  - pip install django-filter
  - add to list of installed apps in settings.py of main project as "django_filters"
  - eg. see filters.py, ProductViewSet in views.py
- Searching. see ProductViewSet views.py.  need to import SearchFilter from rest_framework.filters
- Sorting. see ProductViewSet views.py. need to import OrderingFilter from rest_framework.filters
- Pagination. see pagination.py, views.py need to import PageNumberPagination from rest_framework.pagination

### Auth
- in our custom core app which is specifi to this app and used for defining specific behaviours for this app we can extend the User model.  See models.py in core app
- Now tell Django we need to use our our extended User model via AUTH_USER_MODEL in main app setting.py.
- DONT FORGET TO RUN MIGRATIONS TO take account of our new extended model
  - This will give us an error about our very first migration being dependant on the defalut User we want to swapout
  - This is because we have done it in the middle of the project (usually you should do this as part of your project set up but here we are). Create the class even if you have to use "pass" to leave it empty.
  - The only fix is to drop the database and recreate it from scratch. SO REMEMBER TO AVOID THIS JUST DO IT AS ONE OF THE FIRST THINGS WHEN CONFIRUING YOUR APPS and save yourself the pain.
  - Now note that Users will not be present in Admin Console since we changed it. We need to go to admin.py in core app and register it like we did our CustomProductAdmin
  - Customize CustomUserAdmin in this case to ask for email during registration in the admin interface. See admin.py in core app
- now go thru entire app where you imported the default user model and make changes that will swap out the default User for our User model. We have to be careful here not to make any app dependant on core where our User model is
  - so... for example in our likes app we are using the default User model which we need to change
  - so... in models.py of apps app import settings and now we can access our user model via "settings.AUTH_USER_MODEL". That is anywhere we have old User we can replace it with importing settings and then accessing our user model via "settings.AUTH_USER_MODEL"
  - Django creates permissons based on our models that we can assing them to groups we make. Sometimes we may need a permission that may not quite fit the ones django created so we can create them on the model ourselves. Eg. we can create a permission to cancel our order. See store.models.py and review the Meta class in the order model. It consist of permissons = ["xxx", 'yyy"] where xxx is the permission code we use in our app and yyy is a friendly description. Remember to run migrations afer creating permissions

### Auth endpoints
- we can certainly roll our own auth from sratch but why do that when they are existing projects that already do this. One such project is dojser which provides ready built rest implementation of all the auth endpoints we could need, and we can customize where neccessary
- djoser.readthedocs.io/en/latest/getting_started.html to view what endpoints are made available to us
- Getting started
  - pip install djoser
  - add djoser as an app in settings.py
  - pip install djangorestframework_simplejwt  # this is a package that supposrts JWT
    - set this up in settings.py in REST_FRAMEWORK variable
    - set up SIMPLE_JWT in settings.py
  - in urls.py in main app register djoser url patterns 
  - check it out. http://localhost:8000/auth/users/ , will get a 401 as we need now to pass tokens to be authorized
  - Note that this enpoint has provision for POST which would allow users to register.  But it only captures username, email, passoword. We can customize this by customizing djosers serailizer that is responsible for the data that this enpoint is expecting which are username, email, password.  We want to customize it to recieve also first_name and last_name. Search the djoser docs for serializers and on that page a little ways down you will see a dict of all the serializers djoser uses.
    - the serailizer we want to replace is the djoser CreateUser Serializer, and we can do this via settings and map it from there to our own custom serializer which we can place in the core app. See serializers.py in the core app
    - Now in settings.py create setting DJOSER dict and give it our CustomCreateUserSerializer class
  - the login enpoint /auth/jwt/create
    - it provies a post endpoint that takes a username and password and returns an access token (5min), and refresh token (1 day). These expiry times can be customized in settings.py via SIMPLE_JWT. Check out https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html
  - custom actions beyond create, update, save, destroy etc.
    - we want to create a custom action called me which can be accessed by current logged in user to fetch his profile / customer info
      - this is possible by creating a custom method on the CustomerViewSet and decorating it as an action. "action" is imported from rest_framework.decorators

### Auth permissions on endpoints
- the default rest_framework permission is AllowAny but we can change this via REST_FRAMEWORK key DEFAULT_PERMISSION_CLASSES in settings.py to for example IsAuthenticated. Now all our enpoints required a logged in user aka a valid jwt token to access them or they will get a 401.
- We can also leave the default permission in place and apply permissions we need to specific views. See CustomerViewSet permission_classes
- lets say we want our products endpoint to be able to be listed by any user including anon users, but only allow admins to update, create, delete. we need a custom permission for this because rest_framework only allows IsAuthenticatedOrReadOnly which means any authenticated user can perform CRUD, but recall we only want admins to perform CRUD, any other user can only retrieve or list. So we need to create a custom permission for example "IsAdminOrReadOnly". in store app see permissions.py. We apply it to a view set as usual using permission_classes = [IsAdminOrReadOnly]. See ProductViewSet.
- We updated CustomerView to allow access to /me action to only authenticated users, but any action (CRUD) on any method required admin user. That way now it is more consistent with other endpoints. See CustomerViewSet
- Currently only admins can CRUD customers, but what if we want our Customer Service group we previously created to also CRUD customers via api endpoints. Enter Model Permissions "DjangoModelPermissions". This allows SAFE_METHODS for authenticated users, and NON SAFE_METHODS for authenticated users who have the model permissions for the resource they are trying to access. We should set the permission_classes=[DjangoModelPermissions] or if we are using get_permissions method to return DjangoModelPermissions(). Now members of the group can manage customs via endpoint not only interface. What this does is allow users to access to apis to manage a resource without giving them access to the admin UI. Note that if user has model permissions assigned via group or direct permission, this DjangoModelPermission gives access to resources if he has is_staff role or not.  Now if these model permisson are taken away from him and the endpoint is still protected by DjangoModelPermissons then he will still be able to LIST and RETREIEVE but not CREATE, UPDATE,DELETE. To stop LIST AND RETRIEVE we must customize DjangoModelPermissions. See permissions.py in store for this customization in action stopping ppl outside a group or having direct permissions frome als viewing or retrieving data.
- There is another class called "DjangoModelPermissions" called "DjangoModelPermissionsOrAnonReadOnly" which allows Unauthenticated users view permissions to list and retieve but not full CRUD.

### Auth custom permission
- in core lets add Permissions to Admin UI so we can delete permissions if something goes wrong.  This is not usally safe, but it will make things easy on us if we need to delete a custom permission. See admin.py in core app
- Recall that earlier we created a custom permission "cancel_order" in the Order model via it's Meta class using the permissions variable. See Order model in models.py. This is about how to apply these to our custom endpoint.
- Since we dont have an Order enpoint as yet lets test this with the Customer endpoint. So we will create a custom permission on the Customer model called "view_history". !!!REMEMBER!!! after creating a custom permission we need to run migrations.
- Now create a new permissions class in permissons.py of store app to implement this custom permsission.
- To recap how to create a custom permisson
  - 1. create the custom permission in ViewSet via permissions variable and run migration
  - 2. create custom permission class that retuns that returns true for any user who has this permission assigned via admin ui
  - 3. assign this permission to users in Admin UI
  - 4. apply this permission to the ViewSet via permission_classes OR get_permissions method

### Signals
- Notifications fired at different times. We can listen for them and do something. See /signals/handlers.py in store app. We will create a signal that listens for the creation of a user, and respond by creating a customer profile for this newly created user.
  - pre_save - fired before a model is saved
  - post_save - fire after a model is saved
  - pre_delete - fired before a model is deleted
  - post_delete - fired after a model is deleted
- To register a handler in signals.py you should override the ready method in apps.py.  See apps.py in the store App. The ready method is called when the store app is initialized or "ready" there we import signals.py
- CUSTOM SIGNALS
  - create a folder called signals in app signals will be for
  - Place your signals.py in there and rename to handlers
  - add an __init__.py module, and that is where your signals are defined.
  - A signal is basically an instance of Signal class see /signals/__init.py and see "order_created"
  - Now fire signal when order is created, which is done usually in serailizers in this case the CreateOrderModelSerializer
  - !!!NOTE!!! handlers are placed in the app that needs them. That is any app can subscribe to a signal. In this case the core app subscibes to the order_created custom signal.  The store app subscribes to the user post_save signal. post_save is a built in django signal.
  - !!!NOTE!!! for custom signals we have to explicitly fire them ourselves for instance in a serializer. see CustomeCreateOrderModelSerializer using "order_created.send_robust" or "order_created.send"
  - Dont forget to load the signal module when app is ready that is in apps.py for the app where the handler is override the ready method.

### custom commands
- django looks for a folder named "management/commands" in which custom commands you create are located. Run with "python manage.py <custom_command>.py". See seed_db.py.

### Image uploads
- set up media directory. "media" dir is usally in root. Must be configured in settings.py and urls.py as usual
- We use ImageField for model field and in that set the uplod dir with is relative to the media folder
- Since we are using ImageField we should install Pillow. "pip install pillow"
- Validation 
  - see validators.py in store app.  This time around we put the validator in a seperate file called validators.py. In this way we will then need to add the validator to a list on the field of the model we wish to validate. See ProductImage model and the ImageField with it's validators field.
  - We have other built in validators if using for example FileField we can validate extensions. See commented out code in ProductImage model
  - Note that ImageFiled already contatins a built in extension validator, BUT FileField does not so we would have needed to import the validator provided by django and use that.
- Add images to the product admin section using inlines that we saw already. Since this is directly related to store we use the admin.py in store to do most of the work and then link it to admin.py in core to handle case where we distriute core with our app. See both admin.py in store and core. We also added some custom css via the Media nested class. See ProductAdmin in the store admin.py. To do that add a css file to static folder, and put it inside the Media nested class.

### Emails
- set up email by configuiring "EMAIL_BACKEND" in settings.py
- set up "EMAIL_HOST", "EMAIL_PORT", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD"  in settings.py
- imports
  - from django.core.mail import send_mail, mail_admins, BadHeaderError
  - see views.py hello8 in playground for example of email sending
- For mail attachments, BCC, CC etc we have to use EmailMessage Class directly. See hello8 in views.py of playground. Methods like send_mail and mail_admins use it internally
- to send properly formatted mail use django-templated-mail
  - pip install django-templated-mail
  - email templates go into the templates folder
  - from templated_mail.mail import BaseEmailMessage

### Background task via distributed queues / message brokers
- Instead of Rabbitmq we will use Redis as our message broker coupled with Celery a distributed task queue
- Install Redis in docker and run it
- Install Redis dependancy in django
  - pip install redis
- Install celery as a dependancy
  - pip install celery
- create a celery.py in maing project(project with settings.py)
- put config info in setting.py prefixed with "CELERY" 
- import celery.py module into __init__.py of main app so it is loaded on startup.
- to start a worker
  - run in terminal "celery -A DjangoStore worker --loglevel=info"
- An example
  - see tasks.py, hello9 in views.py in playground app
  - in views.py we import our tasks from tasks.py
    - from .tasks import notify_customers # for example
- !!!NOTE!!! if you create a new task you must restart your celery worker!!! Tasks like notify_custome if created after celery work has started will not be picked up by it.
  
### Celery BEAT as a task scheduler (can also be cron replacement)
- Beat acts as a scheduler or orchestrator
- in settings.py configure the BEAT via "CELERY_BEAT_SCHEDULE" 
  - for finer grain control over schedules use crontab object
  - from celery.schedules import crontab 
- To start the "worker" is differnt
  - "celery -A DjangoStore beat"

### MONITOR CELERY TASK
- use Flower to monitor celery tasks
  - pip install flower
  - start it up: "celery -A DjangoStore flower"
  - access web ui at localhost:5555

### Automated Testing
- Use pytest
  - "pip install pytest"
  -  "pip install pytest-django" # pytest plugin for django