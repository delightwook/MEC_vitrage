# Copyright 2018 - Nokia
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

from vitrage.common.constants import TemplateTypes
from vitrage.evaluator.template_fields import TemplateFields
from vitrage.evaluator.template_validation.content.v2.metadata_validator \
    import MetadataValidator
from vitrage.tests.unit.evaluator.template_validation.content.base import \
    ValidatorTest


class MetadataValidatorTest(ValidatorTest):

    def test_validate_metadata_standard(self):
        metadata = {TemplateFields.NAME: 'blabla',
                    TemplateFields.VERSION: '2',
                    TemplateFields.TYPE: TemplateTypes.STANDARD}
        result = MetadataValidator.validate(metadata)
        self._assert_correct_result(result)

    def test_validate_metadata_definition(self):
        metadata = {TemplateFields.NAME: 'blabla',
                    TemplateFields.VERSION: '2',
                    TemplateFields.TYPE: TemplateTypes.DEFINITION}
        result = MetadataValidator.validate(metadata)
        self._assert_correct_result(result)

    def test_validate_metadata_equivalence(self):
        metadata = {TemplateFields.NAME: 'blabla',
                    TemplateFields.VERSION: '2',
                    TemplateFields.TYPE: TemplateTypes.EQUIVALENCE}
        result = MetadataValidator.validate(metadata)
        self._assert_correct_result(result)

    def test_validate_metadata_invalid_type(self):
        metadata = {TemplateFields.NAME: 'blabla',
                    TemplateFields.VERSION: '2',
                    TemplateFields.TYPE: 'invalid type'}
        result = MetadataValidator.validate(metadata)
        self._assert_fault_result(result, 65)

    def test_validate_metadata_no_type(self):
        metadata = {TemplateFields.NAME: 'blabla',
                    TemplateFields.VERSION: '2'}
        result = MetadataValidator.validate(metadata)
        self._assert_fault_result(result, 64)
