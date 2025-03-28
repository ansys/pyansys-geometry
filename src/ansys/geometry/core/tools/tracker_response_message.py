# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Module for tracker response message."""

#from typing import TYPE_CHECKING

# if TYPE_CHECKING:  # pragma: no cover
#     from ansys.geometry.core.designer.body import Body

from ansys.api.geometry.v0.models_pb2 import TrackerCommandResponse


class TrackerResponseMessage:
    """Provides response for tracked functionallity."""

    # def __init__(
    #     self,
    #     success: bool,
    #     created_bodies: list[str],
    #     modified_bodies: list[str],
    #     deleted_bodies: list[str],
    #     created_components: list[str],
    #     modified_components: list[str],
    #     deleted_components: list[str],
    #     ):
    #     """Initialize the TrackerResponseMessage instance.
        
    #     Parameters
    #     ----------
    #     success: bool
    #         True if the tracking was successful, false if it is not.
    #     created_bodies: list[str]
    #         List of bodies created during tracked operation.
    #     modified_bodies: list[str]
    #         List of bodies modified during tracked operation.
    #     deleted_bodies: list[str]
    #         List of bodies deleted during tracked operation.
    #     created_components: list[str]
    #         List of components created during tracked operation.
    #     modified_components: list[str]
    #         List of components modified during tracked operation.
    #     deleted_components: list[str]
    #         List of components deleted during tracked operation.
            
            
    #     """
    #     self._success = success
    #     self._created_bodies = created_bodies
    #     self._modified_bodies = modified_bodies
    #     self._deleted_bodies = deleted_bodies
    #     self._created_components = created_components
    #     self._modified_components = modified_components
    #     self._deleted_components = deleted_components
        
    def __init__(
        self,
        message: TrackerCommandResponse,
        ):
        """Initialize the TrackerResponseMessage instance from another message."""
        self._success = message.success
        created_body_list = [str]
        for body in message.created_bodies:
            created_body_list.append(body.id)
        self._created_bodies = created_body_list
        
        modified_body_list = [str]
        for body in message.modified_bodies:
            modified_body_list.append(body.id)
        self._modified_bodies = modified_body_list
        
        deleted_body_list = [str]
        for body in message.deleted_bodies:
            deleted_body_list.append(body.id)
        self._deleted_bodies = deleted_body_list
        
        created_component_list = [str]
        for component in message.created_components:
            created_component_list.append(component.id)
        self._created_components = created_component_list
        
        modified_component_list = [str]
        for component in message.modified_components:
            modified_component_list.append(component.id)
        self._modified_components = modified_component_list
        
        deleted_component_list = [str]
        for component in message.deleted_components:
            deleted_component_list.append(component.id)
        self._deleted_components = deleted_component_list    
        
    
    @property
    def success(self) -> bool:
        """Return success status."""
        return self._success
    
    @property
    def created_bodies(self) -> list[str]:
        """Return list of created bodies."""
        return self._created_bodies
    
    @property
    def modified_bodies(self) -> list[str]:
        """Return list of modified bodies."""
        return self._modified_bodies
    
    @property
    def deleted_bodies(self) -> list[str]:
        """Return list of deleted bodies."""
        return self._deleted_bodies
    
    @property
    def created_components(self) -> list[str]:
        """Return list of created components."""
        return self._created_components
    
    @property
    def modified_components(self) -> list[str]:
        """Return list of modified components."""
        return self._modified_components
    
    @property
    def deleted_components(self) -> list[str]:
        """Return list of deleted components."""
        return self._deleted_components