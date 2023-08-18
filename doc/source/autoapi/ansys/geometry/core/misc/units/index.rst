


Module ``units``
================



.. py:module:: ansys.geometry.core.misc.units



Description
-----------

Provides for handling units homogeneously throughout PyGeometry.




Summary
-------

.. tab-set::




    .. tab-item:: Classes

        Content 2

    .. tab-item:: Functions

        Content 2

    .. tab-item:: Enumerations

        Content 2

    .. tab-item:: Attributes

        Content 2






Contents
--------

Classes
~~~~~~~

.. autoapisummary::

   ansys.geometry.core.misc.units.PhysicalQuantity




Attributes
~~~~~~~~~~

.. autoapisummary::

   ansys.geometry.core.misc.units.UNITS


.. py:data:: UNITS

   Units manager.


.. py:class:: PhysicalQuantity(unit: pint.Unit, expected_dimensions: beartype.typing.Optional[pint.Unit] = None)


   Provides the base class for handling units homogeneously throughout PyGeometry.

   Parameters
   ----------
   unit : ~pint.Unit
       Units for the class.
   expected_dimensions : ~pint.Unit, default: None
       Units for the dimensionality of the physical quantity.

   .. py:property:: unit
      :type: pint.Unit

      Unit of the object.


   .. py:property:: base_unit
      :type: pint.Unit

      Base unit of the object.



