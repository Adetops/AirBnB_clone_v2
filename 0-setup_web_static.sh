#!/usr/bin/env bash
# A bash script that sets up my web servers for the deployment
# of web_static

# Ensuring that the programme always exit succesful
trap 'exit 0' ERR


# Installing Nginx
sudo apt-get update -y
sudo apt-get install nginx -y

# Creating necessary directories
sudo mkdir -p /data/web_static/releases/test/
sudo mkdir -p /data/web_static/shared/

# Creating fake HTML file for testing Nginx configuration
content="<html>
  <head>Adetops</head>
  <body>Configuration of Adetops</body>
</html>"

echo "$content"| sudo tee /data/web_static/releases/test/index.html

# Deleting the initial sybolic link
rm -rf /data/web_static/current

# Creating new symbolic link to "/data/web_static/releases/test/"
sudo ln -sf /data/web_static/releases/test/ /data/web_static/current

# Giving ownership to /data/ directory to ubuntu user
sudo chown -Rh ubuntu:ubuntu /data/

# Nginx configuration file
config_file="/etc/nginx/sites-available/default"

# adding a default welcome message
echo 'Hello World!' | sudo tee /var/www/html/index.html > /dev/null

# handling redirections
replacement="48i\\\tif (\$request_filename ~ redirect_me){\n\t\trewrite ^ https://www.youtube.com/watch?v=QH2-TGUlwu4 permanent;\n\t}"
sudo sed -i "$replacement" $config_file

# handling error page
echo "Ceci n'est pas une page" | sudo tee /usr/share/nginx/html/404.html
line="\\\terror_page 404 /404.html;\n\tlocation = /404.html {\n\t\troot /usr/share/nginx/html;\n\t\tinternal;\n\t}"
sudo sed -i "27i $line" $config_file

# adding a custom header
sudo sed -i "32i\\\tadd_header X-Served-By $HOSTNAME;" $config_file

# creating an alias "hbnb_static" to a root
sudo sed -i '38i\\tlocation /hbnb_static/ {\n\t\talias /data/web_static/current/;\n\t}\n' $config_file

# Restarting Nginx
sudo service nginx restart
