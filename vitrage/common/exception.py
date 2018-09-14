# Copyright 2015 - Alcatel-Lucent
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""
**********
Exceptions
**********

Base exceptions and errors for Vitrage.

"""


# the root of all Exceptions
class VitrageException(Exception):
    """Base class for exceptions in Vitrage."""


class VitrageError(VitrageException):
    """Exception for a serious error in Vitrage"""


class VitrageInputError(VitrageError):
    """Exception raised for errors in the input"""


class VitrageAlgorithmError(VitrageException):
    """Exception for unexpected termination of algorithms."""


class VitrageTransformerError(VitrageException):
    """Exception for a serious error in Vitrage transformer"""
