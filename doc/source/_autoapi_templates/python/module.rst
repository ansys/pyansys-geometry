{% if not obj.display %}
:orphan:

{% endif %}

{% if obj.name.split(".") | length == 3 %}
{{ obj.name }}
{{ "=" * obj.name|length }}

{% else %}

{% if obj.type == "package" %}

Package ``{{ obj.short_name }}``
{{ "============" + "=" * obj.short_name|length }}

{% else %}

Module ``{{ obj.short_name }}``
{{ "===========" + "=" * obj.short_name|length }}

{% endif %}

{% endif %}

.. py:module:: {{ obj.name }}


{# Include the description for the module #}

{% if obj.docstring %}
Description
-----------

{{ obj.docstring }}

{% endif %}


Summary
-------

.. tab-set::

    {% set visible_subpackages = obj.subpackages|selectattr("display")|list %}
    {% if visible_subpackages %}
    .. tab-item:: Subpackages

        .. list-table::
           :header-rows: 0
           :widths: auto

           {% for subpackage in visible_subpackages %}
           * - :py:mod:`{{ subpackage.name }}`
             - {{ subpackage.summary }}
           {% endfor %}
    {% endif %}

    {% set visible_submodules = obj.submodules|selectattr("display")|list %}
    {% if visible_submodules %}
    .. tab-item:: Submodules

        .. list-table::
           :header-rows: 0
           :widths: auto

           {% for submodule in visible_submodules %}
           * - :py:mod:`{{ submodule.name }}`
             - {{ submodule.summary }}
           {% endfor %}
    {% endif %}


    .. tab-item:: Classes

        Content 2

    .. tab-item:: Functions

        Content 2

    .. tab-item:: Enumerations

        Content 2

    .. tab-item:: Attributes

        Content 2


{% block subpackages %}
{% set visible_subpackages = obj.subpackages|selectattr("display")|list %}
{% if visible_subpackages %}
Subpackages
-----------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Name
     - Description
   {% for subpackage in visible_subpackages %}
   * - :py:mod:`{{ subpackage.name }}`
     - {{ subpackage.summary }}
   {% endfor %}

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :hidden:

{% for subpackage in visible_subpackages %}
   {{subpackage.short_name}}<{{ subpackage.short_name }}/index.rst>
{% endfor %}


{% endif %}
{% endblock %}




{% block submodules %}
{% set visible_submodules = obj.submodules|selectattr("display")|list %}
{% if visible_submodules %}
Submodules
----------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Name
     - Description
   {% for submodule in visible_submodules %}
   * - :py:mod:`{{ submodule.name }}`
     - {{ submodule.summary }}
   {% endfor %}

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :hidden:

{% for submodule in visible_submodules %}
   {{submodule.short_name}}<{{ submodule.short_name }}/index.rst>
{% endfor %}


{% endif %}
{% endblock %}
{% block content %}
{% if obj.all is not none %}
{% set visible_children = obj.children|selectattr("short_name", "in", obj.all)|list %}
{% elif obj.type is equalto("package") %}
{% set visible_children = obj.children|selectattr("display")|list %}
{% else %}
{% set visible_children = obj.children|selectattr("display")|rejectattr("imported")|list %}
{% endif %}
{% if visible_children %}
Contents
--------

{% set visible_classes = visible_children|selectattr("type", "equalto", "class")|list %}
{% set visible_functions = visible_children|selectattr("type", "equalto", "function")|list %}
{% set visible_attributes = visible_children|selectattr("type", "equalto", "data")|list %}
{% if "show-module-summary" in autoapi_options and (visible_classes or visible_functions) %}
{% block classes scoped %}
{% if visible_classes %}
Classes
~~~~~~~

.. autoapisummary::

{% for klass in visible_classes %}
   {{ klass.id }}
{% endfor %}


{% endif %}
{% endblock %}

{% block functions scoped %}
{% if visible_functions %}
Functions
~~~~~~~~~

.. autoapisummary::

{% for function in visible_functions %}
   {{ function.id }}
{% endfor %}


{% endif %}
{% endblock %}

{% block attributes scoped %}
{% if visible_attributes %}
Attributes
~~~~~~~~~~

.. autoapisummary::

{% for attribute in visible_attributes %}
   {{ attribute.id }}
{% endfor %}


{% endif %}
{% endblock %}
{% endif %}
{% for obj_item in visible_children %}
{{ obj_item.render()|indent(0) }}
{% endfor %}
{% endif %}
{% endblock %}

