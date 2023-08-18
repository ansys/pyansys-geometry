


Module ``material``
===================



.. py:module:: ansys.geometry.core.materials.material



Description
-----------

Provides the data structure for material and for adding a material property.




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

   ansys.geometry.core.materials.material.Material




.. py:class:: Material(name: str, density: pint.Quantity, additional_properties: beartype.typing.Optional[beartype.typing.Sequence[ansys.geometry.core.materials.property.MaterialProperty]] = None)


   Provides the data structure for a material.

   Parameters
   ----------
   name: str
       Material name.
   density: ~pint.Quantity
       Material density.
   additional_properties: Sequence[MaterialProperty], default: None
       Additional material properties.

   .. py:property:: properties
      :type: beartype.typing.Dict[ansys.geometry.core.materials.property.MaterialPropertyType, ansys.geometry.core.materials.property.MaterialProperty]

      Dictionary of the material property type and material properties.


   .. py:property:: name
      :type: str

      Material name.


   .. py:method:: add_property(type: ansys.geometry.core.materials.property.MaterialPropertyType, name: str, quantity: pint.Quantity) -> None

      Add a material property to the ``Material`` class.

      Parameters
      ----------
      type : MaterialPropertyType
          Material property type.
      name: str
          Material name.
      quantity: ~pint.Quantity
          Material value and unit.



