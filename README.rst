Alexa + Uplink
=============================

Uplink blockchain integration with Alexa. This is meant to be a demoware application showing various simple use cases of Alexa + Uplink.

*The project is in early stages so the code written will be rushed and won't be fully production ready.* 


Setup
-----
#.  Uplink must be installed and running. For details: 

.. _uplink: https://github.com/adjoint-io/uplink
.. _documentation: https://www.adjoint.io/docs


It is recommended to run this project in a virtualenv. If virtualenvs are unfamiliar to you, `this handy tutorial`_
might be a good place to start.

#.  Create a virtualenv for this project, and activate it.
#.  Use ``pip install -r requirements.txt`` to install the required Python packages.
#.  You will require ``ngrok`` to make your skill accessible to Alexa for testing. You can download ngrok `here`_.

.. _here: https://ngrok.com/download
.. _this handy tutorial: http://docs.python-guide.org/en/latest/dev/virtualenvs/

Quickstart
----------

Follow these easy steps to test the project.

#. Launch the server by invoking ``python uplink_alexa.py``.
#. With the server running, start ``ngrok http 6000``.
#. Configure your app on the `Alexa Developer Portal`_. `This video`_ by `John Wheeler`_ shows how to deploy your speech assets configuration to the `Alexa Developer Portal`_.
#. That's all! If you are using a browser that supports WebRTC for micophone input (Chrome, Firefox or Opera), you may use `echosim`_ to test your script - simply log in with the same credentials you used to deploy your Skill.

.. _Alexa Developer Portal: https://developer.amazon.com/alexa
.. _This video: https://alexatutorial.com
.. _John Wheeler: https://alexatutorial.com/flask-ask/
.. _echosim: http://www.echosim.io/


Commands
---------

1.  Simple Block Explorer

Say "Alexa Get Peers" to get number of peers in chain.
Say "Alexa Get Blocks" - to get the number of blocks in the chain.
Say "Alexa Get BLock 3" - to get the number of transactions in block 3.
Say "Alexa Get Block 3 Transaction 1" - to get the transactions details.


2.  Short Term Rental Lease (Single Payment and Security Deposit)
    
Status: in-progress

