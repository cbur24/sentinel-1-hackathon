The Python standard library provides a lightweight solution for creating virtual environments via the `venv` module.

Create a virtual Environment: Use Python's built-in `venv` module to create a virtual environment. Name it after the python version, e.g. "py311":

    $ python3 -m venv py311

Activate the virtual environment: Use the source command to activate the virtual environment:

    $ source py311/bin/activate

Install Required Packages:
We have a list of required packages in the `requirement.txt` file. You can install these packages into your virtual environment using pip:

    $ python3 -m pip install -r /requirements.txt

