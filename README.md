# Hello world

Ene mene muh und draus bist du. Draus bist du noch lange nicht, musst erst sagen wie alt du bist.

Wer, wie, was, wieso, weshalb, warum? – Wer nicht fragt bleibt dumm!


# Basic structure

The app.py is the main file acting as the redicrector for the URLs . Inside page2.py one can find an app and inside page3.py one can find another app.

The home.py is just an page that is placed as root to guide the user to both of the apps.

Maybe on the home page also Barrierefreiheitserklärung, Datenschutzerklärung and Impressum need to be added.


Project/ \
|-- app.py \
|  \
|-- pages/  \
|-----|page2.py   \
|-----|page3.py  \
|-----|assets/   \
|---------|-- stuff   \
|   |    \
|-- README   \


# How to run it ?

Check out  https://dash.plotly.com/tutorial . To launch the app, type into your terminal the command python app.py