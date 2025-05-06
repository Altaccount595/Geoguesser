# tophertime-studios__tawabb_alexl175_jacobl153_jonathanm764

# Roster:
**PM:** Tawabb Berri

**FRONT END:** Alex Luo

**Middleware/API:** Jacob Lukose 

**Database Lead:** Jonathan Metzler

# Project Description:

Our project will be focused on creating a replica of GeoGuessr by using GoogleMaps StreetView panoramas. During each round the server picks a random StreetView coordinate and shows the panorama next to an interactive world map (depending on the region the user has selected). The player drops a marker on where they think the street is located and submits. The game then reveals the location, draws a distance line, and awards points based on the distance between the true location and the user's location. Our game will have multiple regions and a timed mode. A stretch of our project is to include a TimeGuessr where users will have to guess a place and time based on historical/famous images.

# Install Guide

**Prerequisites**

Ensure that **Git** and **Python** are installed on your machine. It is recommended that you use a virtual machine when running this project to avoid any possible conflicts. For help, refer to the following documentation:
   1. Installing Git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git 
   2. Installing Python: https://www.python.org/downloads/ 

   3. (Optional) Setting up Git with SSH (Ms. Novillo's APCSA Guide): https://novillo-cs.github.io/apcsa/tools/ 
         

**Cloning the Project**
1. Create Python virtual environment:

```
$ python3 -m PATH/TO/venv_name
```

2. Activate virtual environment 

   - Linux: `$ . PATH/TO/venv_name/bin/activate`
   - Windows (PowerShell): `> . .\PATH\TO\venv_name\Scripts\activate`
   - Windows (Command Prompt): `>PATH\TO\venv_name\Scripts\activate`
   - macOS: `$ source PATH/TO/venv_name/bin/activate`

   *Notes*

   - If successful, command line will display name of virtual environment: `(venv_name) $ `

   - To close a virtual environment, simply type `$ deactivate` in the terminal


3. In terminal, clone the repository to your local machine: 

HTTPS METHOD (Recommended)

```
$ git clone https://github.com/1Teee/tophertime-studios__tawabb_alexl175_jacobl153_jonathanm764.git     
```

SSH METHOD (Requires SSH Key to be set up):

```
$ git clone git@github.com:1Teee/tophertime-studios__tawabb_alexl175_jacobl153_jonathanm764.git
```

4. Navigate to project directory

```
$ cd PATH/TO/tophertime-studios__tawabb_alexl175_jacobl153_jonathanm764/
```

5. Install dependencies

```
$ pip install -r requirements.txt
```
        
# Launch Codes

## Best Way

1. Visit (placeholder for domain) on any modern browser
2. Enjoy!

## The DEVO Way

1. Navigate to project directory:

```
$ cd PATH/TO/studios__tawabb_alexl175_jacobl153_jonathanm764.git/
```
 
2. Navigate to 'app' directory

```
 $ cd app/
```

3. Run App

```
 $ python3 __init__.py
```
4. Open the link that appears in the terminal to be brought to the website
    - You can visit the link via several methods:
        - Control + Clicking on the link
        - Typing/Pasting http://127.0.0.1:5000 in any browser
    - To close the app, press control + C when in the terminal

```    
* Running on http://127.0.0.1:5000
``` 
