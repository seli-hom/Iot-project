<!-- TODO: write read me documentation -->
# IoT Project - Smart Store
<!-- TODO: write project description -->


| Team Members  | Github Handle |
| ------------- | ------------- |
| Selihom Efrem Ogbe  | seli-hom  |
| Talia Muro  | taliamuro  |
| Luke Ryan Nwantoly | Asumakn  |
| Sabrina Robinson  | SR-Delightfully  |


<!-- TODO: add instructions on how to run the project -->
<!--* install flask -->
<!--* install python -->
<!--* set Wampoon (explain what is wampoon exactly)' -->
<!--* make sure wampoon is running before next step ⬇ -->
<!--* run cmd 'pip install Flask-Mail' -->
<!--* run cmd 'python main.py' -->
<!--* go to "http://localhost:5000/" to view project -->

<!-- ! if you run into an error, write the issue here and explain how you fixed it ⬇ -->

<!-- TODO: add physical system requirements -->
<!--* I.E. breadboards, rasberry pis, media, etc. -->

<br>

# Project Structure

<pre>
IOT-PROJECT
├── models/                   -> <a href="#models-layer"><small><b>Database layer</b></small></a>
│   ├── customers.py             <small>customer data & queries</small>
│   ├── database.py              <small>database connection & initialization</small>
│   ├── notifications.py         <small>system alerts & logs</small>
│   └── users.py                 <small>authentication & roles</small>
│
├── public/                   -> <a href="#frontend-layer"><small><b>Frontend layer</b></small></a>
│   ├── js/                      <small>frontend javascript</small>
│   └── python/                  <small>frontend python scripts</small>
│
├── routes/                   -> <a href="#controllers-layer"><small><b>controllers / request handling</b></small></a>
│   └── store_routes.py          <small>main store dashboard routing</small>
│
├── scripts/                  -> <a href="#scripts-layer"><small><b>backend utility scripts</b></small></a>
│
├── services/                 -> <a href="#services-layer"><small><b>business logic</b></small></a>
│   ├── email_service.py         <small>emails, alerts, notifications</small>
│   └── TODO: alert_service.py   <small>convert alert handling into a service</small>
│
├── static/                      <small>css, images, assets</small>
├── templates/                   <small>html templates</small>
│
├── main.py                   -> <a href="#application-entry"><small><b>application entry point</b></small></a>
└── README.md                 -> <a href="#documentation"><small><b>project documentation</b></small></a>
</pre>

<br>

*TODO: add more detailed descript of each part, its purpose and how it works.

## Application Entry
<a id="application-entry"></a>

## Documentation
<a id="documentation"></a>

Project documentation includes

## Frontend Layer
<a id="frontend-layer"></a>

## Models Layer
<a id="models-layer"></a>

## Controllers Layer
<a id="controllers-layer"></a>

Handles:

## Services Layer
<a id="services-layer"></a>

Business logic including:

## Scripts Layer
<a id="scripts-layer"></a>

Background workers:

