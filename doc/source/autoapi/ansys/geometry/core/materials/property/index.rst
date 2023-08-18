


Module ``property``
===================



.. py:module:: ansys.geometry.core.materials.property



Description
-----------

Provides the ``MaterialProperty`` class.




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

   ansys.geometry.core.materials.property.MaterialPropertyType
   ansys.geometry.core.materials.property.MaterialProperty




.. py:class:: MaterialPropertyType


   Bases: :py:obj:`enum.Enum`

   Provides an enum holding the possible values for ``MaterialProperty`` objects.

   .. py:attribute:: DENSITY
      :value: 'Density'



   .. py:attribute:: ELASTIC_MODULUS
      :value: 'ElasticModulus'



   .. py:attribute:: POISSON_RATIO
      :value: 'PoissonsRatio'



   .. py:attribute:: SHEAR_MODULUS
      :value: 'ShearModulus'



   .. py:attribute:: SPECIFIC_HEAT
      :value: 'SpecificHeat'



   .. py:attribute:: TENSILE_STRENGTH
      :value: 'TensileStrength'



   .. py:attribute:: THERMAL_CONDUCTIVITY
      :value: 'ThermalConductivity'



   .. py:method:: from_id() -> MaterialPropertyType

      Return the ``MaterialPropertyType`` value from the service representation.

      Parameters
      ----------
      id : str
          Geometry Service string representation of a property type.

      Returns
      -------
      MaterialPropertyType
          Common name for property type.



.. py:class:: MaterialProperty(type: MaterialPropertyType, name: str, quantity: pint.Quantity)


   Provides the data structure for a material property.

   Parameters
   ----------
   type : MaterialPropertyType
       Type of the material property.
   name: str
       Material property name.
   quantity: ~pint.Quantity
       Value and unit.

   .. py:property:: type
      :type: MaterialPropertyType

      Material property ID.


   .. py:property:: name
      :type: str

      Material property name.


   .. py:property:: quantity
      :type: pint.Quantity

      Material property quantity and unit.



