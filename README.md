Nova Python Website
===================

This is the http://novapython.org website source code. It is currently running under Apache using WSGI. To setup the VirtualHost under Apache, you should have a config that resembles:

    <VirtualHost *:80>
        DocumentRoot /var/www/website
        <Directory /var/www/website>
            Order deny,allow
            Allow from all
        </Directory>

        WSGIScriptAlias / /var/www/website/router.py
        Alias /static /var/www/website/static

        <Directory /var/www/webset/static>
            Options +Indexes
        </Directory>
    </VirtualHost>


Or you can run the application locally. Either way you will need the following packages:

    BeautifulSoup==3.2.1
    Jinja2==2.6
    Unidecode==0.04.9
    mimeparse==0.1.3
    mimerender==0.2.2
    pep8==0.6.1
    pytz==2012b
    redis==2.4.11
    requests==0.10.0
    virtualenv==1.5.2.post2
    web.py==0.34
    wsgiref==0.1.2
