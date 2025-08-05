Welcome to Vertiport Autonomy's documentation!
===============================================

Vertiport Autonomy is a Deep Reinforcement Learning platform for autonomous vertiport coordination. This project implements a sophisticated simulation environment for training and evaluating autonomous agents that manage drone traffic at vertiports (vertical take-off and landing ports).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/modules
   tutorials/index

Features
--------

* **Deep Reinforcement Learning Environment**: Built on Gymnasium API with PPO agent support
* **Realistic Simulation**: Discrete-time vertiport simulation with formal state machines
* **Curriculum Learning**: Progressive training strategy for complex scenarios
* **Comprehensive Evaluation**: Built-in metrics and performance analysis framework
* **Configurable Scenarios**: YAML-based configuration system with Pydantic validation

Quick Start
-----------

Install the package:

.. code-block:: bash

   pip install -e .

Run a basic evaluation:

.. code-block:: bash

   python scripts/evaluate.py --agent heuristic --scenario scenarios/easy_world.yaml --episodes 10

Train a new agent:

.. code-block:: bash

   python scripts/train.py --scenario scenarios/easy_world.yaml --timesteps 10000

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`