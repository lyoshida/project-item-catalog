# Item Catalog Project

This is a course Project of the Full Stack Nanodegree (by Udacity).

## Running the app locally

Make sure you have python 2.6+ installed.

### Installing dependecies

Use the command `pip install [package]` to install required packages:

 * flask
 * sqlalchemy
 * httplib2
 * requests
 * oauth2client

 ### Setup Google+ login

 Access https://console.developers.google.com/, and follow the steps shown in this page:
 https://developers.google.com/+/web/signin/ to setup a Google+ login.

 Remember to add http://localhost:5000 to the "Authorized JavaScript Origins"

 Download the client secret file and place it in the root folder of the project.
 Rename the file to `client_secrets.json`

 ### Loading the webserver

 Run the following command:

 `python webserver.py`

 The default server is http://0.0.0.0:5000. Open it in your browser.


## Adding Items

You must be logged in to create, edit and delete categories and items.

Before adding items, create categories by clicking on "+ category".