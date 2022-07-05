# homeassistant
# credits to https://github.com/wpeterw/stromer_slack_status
please take a look at this project for a nice new integration: https://github.com/CoMPaTech/stromer

stromer.py can be innitiated with appdeamon. see https://www.home-assistant.io/docs/ecosystem/appdaemon/
Don't forget to add your login details and api secrets in the python script.
password = "PASSWORD-Here"
username = "username@email.com"
client_id = "Clientid-here"
client_secret = "Secret-here" (absolute since api version 4)

The client_id and client_secret can be 'sniffed' with tools like MitM proxy.

sensor.yaml, add this to your sensor.yaml. see how to create a sensor.yaml as split config instead of your configuration.yaml. https://www.home-assistant.io/docs/configuration/splitting_configuration/

Add the sensors to your dashboard:

![Stromer Sensor](https://repository-images.githubusercontent.com/236567711/8775ce80-41cc-11ea-9b03-74208e961f84)
