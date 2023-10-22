# Forecasting Deforestation in the Pantanal Biome, Brazil, using a machine-learning model

Abstract
--------

Halting deforestation is crucial to protect life on the planet and mitigate climate change. Regrettably, the Pantanal biome, a vital tropical wetland of notable relevance for Brazil and the world, is currently experiencing mounting deforestation rates. This trend may result in losing up to 86\% of the region’s natural vegetation. The Pantanal region has remained largely understudied despite successfully implementing contemporary statistical techniques to model and forecast deforestation in other regions. As a result, this study employs simulation modeling to explore a range of hypothetical land-use and burn-area scenarios, aiming to understand deforestation dynamics and to predict the loss of natural ecosystems in the Pantanal region by 2030. To predict deforestation in the Pantanal, the Machine Learning model XGBoost was employed. This model integrated a range of key features such as agricultural production, cattle head production, burned area, and deforestation in previous years.

Setup
-----

This project uses Python (>=3.7).

Development environment
-----------------------

To create and install python environment:

```bash
make create-env
```

Then, activate it: 

```bash
. ./activate
```

This will activate the conda environmnet, install the dependencies required and set some key paths. 

Dependencies
------------

To install dependencies:

.. code:: bash

   make install-deps


To compile dependencies:

.. code:: bash

  pip install pip-tools
  make compile-deps


Development configuration
--------------------------

Create a file in the project's root dir called ``config.local.env``,
with the following structure:

::


   DATA_FOLDER="path to you local data folder"


Basic directory structure
------------------------------

:: 

   ├── config                 # Configuration directory, contains all configuration yamls
   ├── data                   # Local data directory for development
   ├── notebooks              # Jupyter notebooks directory
   ├── requirements           # Package requirements directory
   ├── runner                 # Main PROG directory
   │   ├── data_prep          # Data preparation tasks
   │   ├── engine             # Auxiliary task running functions
   ├── scripts                # Auxiliary scripts for simulations
   └── tests                  # Tests directory


Data configuration
------------------

The data configuration file is **10-data.yaml**.

These files define data location, format and everything else required to read/write those files.  
The data configuration files are used in the io module, which is the main way to perform read write data operations in the application.

Using the io module to access data
------------------------------------

The io module can perform read/write operation of data files (mostly tables and pickles).  
To use the module, find which `domain` (ex: raw, preprocessed) and `table/pickle` (ex: perm_area) you want to read/write and use the standard functions of the io module.

There are examples of usage of the io module below

Pandas table
------------

* Read:

.. code:: python

   io.load_table("raw", "table_name")


* Write:

.. code:: python

   io.save_table(preprocessed_table, "preprocessed", "table_name")


Pickle
------

* Read:

.. code:: python

   io.load_pickle("raw", "pickle_name")


* Write:

.. code:: python

   io.files.save_pickle(pickle_variable, "preprocessed", "pickle_name")


Running tasks
--------------

A task is simply a function from a module. There are simple requirements
to be able to run them using the application standard process:

- Option 1: The task must accept \*args and \**kwargs
- Option 2: Add the decorator @click.command() on your function

The command to run a task has the following pattern:

- Pattern: `./run task module.path:function`

To run tasks, you will need to find which commands you want to run and
pass them as arguments to ``./run``. For example:

.. code:: bash

   ./run data-pipeline run-all

Run the following command line to see the basic usage of the project's
runner:

::

   ./run --help

The most common use cases is summarized in a few commands in the next subsections.

Data ingestion and preprocessing
--------------------------------

.. code:: bash

   ./run data-pipeline run-all

Jupyter
---------

Run the following command:

.. code:: bash

   . ./jupyter

This will set some useful env variables before launching Jupyter

