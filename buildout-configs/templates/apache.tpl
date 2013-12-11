<VirtualHost *:80>
    ServerAdmin ${configuration:server-admin}
    ServerName ${configuration:www-domain}
    ServerAlias ${configuration:www-domain}

    RewriteEngine On

    RewriteRule ^/(.*) http://localhost:${configuration:pound-port}/VirtualHostBase/http/${configuration:www-domain}:80/${configuration:plone-site}/VirtualHostRoot/$1 [P,L]
    Include ${configuration:custom-vh-config}

</VirtualHost>
