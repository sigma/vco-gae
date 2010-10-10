===========================================
 Welcome to vCO Simulator's documentation!
===========================================

.. toctree::
   :maxdepth: 2

Introduction
============

The goal of this application is to provide a reference point for developing
client software for the `VMware vCenter Orchestrator
<http://www.vmware.com/products/vcenter-orchestrator/>`_, and more precisely
for its SOAP WebService. This site provides:

* a public reference implementation against which client code can be tested.

* code examples explaining the various behaviors.

Although the author/maintainer is a VMware employee, this software is not
affiliated with VMware. Complete source code for this site is available under
MIT license at http://gitorious.org/vco-gae.

Quick start
===========

For the impatient, just point your vCO client to
http://vco-gae.appspot.com/vmware-vmo-webcontrol/webservice. That's it, you can
now browse available workflows, objects, run or schedule some activities,…

How it works
============

There is no real vCO server behind this application. Instead, there is
a simulator, that exposes the same SOAP API as vCO 4.1 (more versions might
appear in the future).

This simulator is implemented on top of the `Google App Engine
<code.google.com/appengine/>`_ framework, and more precisely, the Python
version of it. Still, there is no obvious difference in behavior, compared to
a real vCO. Except for :ref:`limitations`, of course.

Client libraries
================

Here is a list of available client libraries for vCO. Don't hesitate to
notify me of publicly available libraries that are missing.

+------------------------+--------+----------+------------------------------+----------------------------------+
| Client                 | Author | Language | License                      | Examples                         |
+========================+========+==========+==============================+==================================+
| Official Java bindings | VMware | Java     | VMware Technological Preview | TODO                             |
+------------------------+--------+----------+------------------------------+----------------------------------+
| vmw.vco                | VMware | Python   | MIT                          | :ref:`examples <pyvco:examples>` |
+------------------------+--------+----------+------------------------------+----------------------------------+

For now, this vCO simulator is mainly tested using the `vmw.vco
<http://sigma.github.com/vmw.vco>`_ client library (since they share the same
developer), so this one might be the easiest starting point for
running examples.

Simulator versions
==================

Currently there is only one version of this simulator, which mimics the
behavior of vCO 4.1. In the future, there might be more versions available,
including 4.0 support and potentially future versions. Also, a special
"torture" version would be interesting, to serve as a robustness testbed.

+---------------------------+-------------------------------------------------------------+
| vCO version               | SOAP URL                                                    |
+===========================+=============================================================+
| vCO 4.0                   | TODO                                                        |
+---------------------------+-------------------------------------------------------------+
| vCO 4.1                   | http://vco-gae.appspot.com/vmware-vmo-webcontrol/webservice |
+---------------------------+-------------------------------------------------------------+
| vCO 4.1 (torture version) | TODO                                                        |
+---------------------------+-------------------------------------------------------------+

Available objects
=================

Those are the objects that are guaranteed to exist when you run client
code. Others might exist as well, depending on the activities that are
triggered by other users at the same time.

Plugins
-------

+-------+---------------+
| Id    | Description   |
+=======+===============+
| dummy | Dummy plug-in |
+-------+---------------+

Workflows
---------

+--------------------------------------+------------------+------------+-------------+-------------------------------------------------------------+
| Id                                   | Description      | Input      | Output      | Specification                                               |
+======================================+==================+============+=============+=============================================================+
| 94db6b5e-cabf-11df-9ffb-002618405f6e | Dummy workflow   | in: string | out: string | 'out' is set to 'in' after 10 seconds                       |
+--------------------------------------+------------------+------------+-------------+-------------------------------------------------------------+
| a29f742e-cabf-11df-9ffb-002618405f6e | Waiting workflow |            |             | enters WAITING state after 5 seconds,                       |
|                                      |                  |            |             | timeouts after 1 hour                                       |
+--------------------------------------+------------------+------------+-------------+-------------------------------------------------------------+

Plugin Objects
--------------

+-----+--------+------+--------------+
| Id  | Plugin | Type | Properties   |
+=====+========+======+==============+
| foo | dummy  | Foo  | isTrue, name |
+-----+--------+------+--------------+

.. _limitations:

Limitations
===========

Authentication
--------------

Currently, no authentication support is provided (you can basically connect
using whatever login/password you like, so feel free to pick something that's
*not* important to you)

Permissions
-----------

Similarly, no permission is enforced on any user object. Only base objects
(those that are necessary for the simulator to well behave) are read-only.

Reset
-----

Obviously, the simulator needs to be reset from time to time, so that objects
don't accumulate forever. This is achieved every night for objects that are
older than 24h, so don't count on your objects to stay there forever.
