# Copyright 2017 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

COMPUTE_INSTANCE_CREATE_END = {
    "state_description": "", "availability_zone": "nova", "terminated_at": "",
    "ephemeral_gb": 0, "instance_type_id": 11, "message": "Success",
    "deleted_at": "", "reservation_id": "r-0yonac30", "memory_mb": 64,
    "display_name": "YOY", "fixed_ips": [{
        "version": 4, "vif_mac": "fa:16:3e:a0:5c:40", "floating_ips": [],
        "label": "NetA", "meta": {}, "address": "8.8.8.11", "type": "fixed"}],
    "hostname": "yoy", "state": "active", "progress": "",
    "launched_at": "2017-05-24T15:49:16.137248", "metadata": {},
    "node": "###", "ramdisk_id": "", "access_ip_v6": None,
    "disk_gb": 0, "access_ip_v4": None, "kernel_id": "",
    "host": "###", "user_id": "609544a5d1de4023b44bb71d624281ab",
    "image_ref_url": "http://127.0.0.1:9292/images/", "cell_name": "",
    "root_gb": 0, "tenant_id": "ef3f81058a934157b42454e3fc63c213",
    "created_at": "2017-05-24 15:48:22+00:00",
    "instance_id": "###",
    "instance_type": "m1.nano", "vcpus": 1, "image_meta": {
        "min_disk": "0", "container_format": "bare", "min_ram": "0",
        "disk_format": "raw", "base_image_ref": ""},
    "architecture": None, "os_type": None, "instance_flavor_id": "42"}

PORT_CREATE_END = {u'port': {
    u'allowed_address_pairs': [], u'extra_dhcp_opts': [],
    u'updated_at': u'2017-05-24T15:48:25Z', u'device_owner': u'compute:nova',
    u'revision_number': 7, u'port_security_enabled': True,
    u'binding:profile': {}, u'fixed_ips': [{
        u'subnet_id': u'bb5a20d0-07ea-4f01-89cb-ec9e7678cb84',
        u'ip_address': u'8.8.8.11'}],
    u'id': u'###',
    u'security_groups': [u'2cd64353-05a7-43fa-abd7-8ba20c6b3326'],
    u'binding:vif_details': {u'port_filter': True, u'ovs_hybrid_plug': True},
    u'binding:vif_type': u'ovs', u'mac_address': u'fa:16:3e:a0:5c:40',
    u'project_id': u'ef3f81058a934157b42454e3fc63c213', u'status': u'DOWN',
    u'binding:host_id': u'###', u'description': u'', u'tags': [],
    u'device_id': u'###', u'name': u'', u'admin_state_up': True,
    u'network_id': u'###',
    u'tenant_id': u'ef3f81058a934157b42454e3fc63c213',
    u'created_at': u'2017-05-24T15:48:24Z', u'binding:vnic_type': u'normal'}}

VOLUME_CREATE_END = {
    u'status': u'available', u'user_id': u'609544a5d1de4023b44bb71d624281ab',
    u'display_name': u'ssssss', u'availability_zone': u'nova',
    u'tenant_id': u'ef3f81058a934157b42454e3fc63c213',
    u'created_at': u'2017-05-28T10:43:13+00:00',
    u'volume_attachment': [],
    u'volume_type': u'e8b50d6e-0bc3-47aa-b378-ac06e5917873',
    u'host': u'compute-0-0@lvmdriver-1#lvmdriver-1',
    u'snapshot_id': None, u'replication_status': None,
    u'volume_id': u'###',
    u'replication_extended_status': None, u'replication_driver_data': None,
    u'size': 2, u'launched_at': u'2017-05-28T10:43:14.521562+00:00',
    u'metadata': []}

VOLUME_ATTACH_END = {
    u'status': u'in-use', u'display_name': u'', u'availability_zone': u'nova',
    u'tenant_id': u'ef3f81058a934157b42454e3fc63c213',
    u'created_at': u'2017-05-28T10:40:21+00:00',
    u'volume_attachment': [{
        u'instance_uuid': u'e9687e55-307b-4d1a-b57d-778cf52d78ee',
        u'volume': {
            u'migration_status': None, u'provider_id': None,
            u'availability_zone': u'nova', u'terminated_at': None,
            u'updated_at': u'2017-05-28T10:42:10.000000',
            u'provider_geometry': None, u'replication_extended_status': None,
            u'replication_status': None, u'snapshot_id': None,
            u'ec2_id': None, u'deleted_at': None,
            u'id': u'5e41d178-4349-47aa-9be9-a9ee80ccdcc8', u'size': 1,
            u'user_id': u'609544a5d1de4023b44bb71d624281ab',
            u'display_description': u'', u'cluster_name': None,
            u'project_id': u'ef3f81058a934157b42454e3fc63c213',
            u'launched_at': u'2017-05-28T10:42:05.000000',
            u'scheduled_at': u'2017-05-28T10:40:23.000000',
            u'status': u'in-use',
            u'volume_type_id': u'e8b50d6e-0bc3-47aa-b378-ac06e5917873',
            u'multiattach': False, u'deleted': False,
            u'provider_location': u'127.0.0.1:3260,3 iqn.2010-10.org.openstac'
                                  u'k:volume-5e41d178-4349-47aa-9be9-a9ee80cc'
                                  u'dcc8 1',
            u'host': u'compute-0-0@lvmdriver-1#lvmdriver-1',
            u'consistencygroup_id': None, u'source_volid': None,
            u'provider_auth': u'CHAP 5j3WZ6nHp6rYgh5u8HcJ P3Duwhx7ECUrSieo',
            u'previous_status': None, u'display_name': u'', u'bootable': True,
            u'created_at': u'2017-05-28T10:40:21.000000',
            u'attach_status': u'attached', u'_name_id': None,
            u'encryption_key_id': None, u'replication_driver_data': None,
            u'group_id': None},
        u'attach_time': u'2017-05-28T10:42:10.000000',
        u'deleted': False, u'attached_host': None,
        u'created_at': u'2017-05-28T10:42:10.000000', u'attach_mode': u'rw',
        u'updated_at': None,
        u'attach_status': u'attached', u'detach_time': None,
        u'volume_id': u'5e41d178-4349-47aa-9be9-a9ee80ccdcc8',
        u'mountpoint': u'/dev/vda', u'deleted_at': None,
        u'id': u'935e0db2-956b-464f-af47-cadfb6ad9c2f'}],
    u'volume_type': u'e8b50d6e-0bc3-47aa-b378-ac06e5917873',
    u'host': u'compute-0-0@lvmdriver-1#lvmdriver-1', u'glance_metadata': [{
        u'deleted': False, u'created_at': u'2017-05-28T10:42:05.000000',
        u'snapshot_id': None, u'updated_at': None, u'value': u'bare',
        u'key': u'container_format',
        u'volume_id': u'5e41d178-4349-47aa-9be9-a9ee80ccdcc8',
        u'deleted_at': None, u'id': 25}, {
        u'deleted': False,
        u'created_at': u'2017-05-28T10:42:05.000000', u'snapshot_id': None,
        u'updated_at': None, u'value': u'0', u'key': u'min_ram',
        u'volume_id': u'5e41d178-4349-47aa-9be9-a9ee80ccdcc8',
        u'deleted_at': None, u'id': 26}, {
        u'deleted': False, u'created_at': u'2017-05-28T10:42:05.000000',
        u'snapshot_id': None, u'updated_at': None, u'value': u'raw',
        u'key': u'disk_format',
        u'volume_id': u'5e41d178-4349-47aa-9be9-a9ee80ccdcc8',
        u'deleted_at': None, u'id': 27}, {
        u'deleted': False, u'created_at': u'2017-05-28T10:42:05.000000',
        u'snapshot_id': None, u'updated_at': None, u'value': u'TinyLinux',
        u'key': u'image_name',
        u'volume_id': u'5e41d178-4349-47aa-9be9-a9ee80ccdcc8',
        u'deleted_at': None, u'id': 28}, {
        u'deleted': False, u'created_at': u'2017-05-28T10:42:05.000000',
        u'snapshot_id': None, u'updated_at': None,
        u'value': u'9a43d75b-d58c-45eb-8112-872db1ad18df',
        u'key': u'image_id',
        u'volume_id': u'5e41d178-4349-47aa-9be9-a9ee80ccdcc8',
        u'deleted_at': None, u'id': 29}, {
        u'deleted': False, u'created_at': u'2017-05-28T10:42:05.000000',
        u'snapshot_id': None, u'updated_at': None,
        u'value': u'3b9c2d448424435f30d10e620c1f8392', u'key': u'checksum',
        u'volume_id': u'5e41d178-4349-47aa-9be9-a9ee80ccdcc8',
        u'deleted_at': None, u'id': 30}, {
        u'deleted': False, u'created_at': u'2017-05-28T10:42:05.000000',
        u'snapshot_id': None, u'updated_at': None, u'value': u'0',
        u'key': u'min_disk',
        u'volume_id': u'5e41d178-4349-47aa-9be9-a9ee80ccdcc8',
        u'deleted_at': None, u'id': 31}, {
        u'deleted': False, u'created_at': u'2017-05-28T10:42:05.000000',
        u'snapshot_id': None, u'updated_at': None, u'value': u'19791872',
        u'key': u'size',
        u'volume_id': u'5e41d178-4349-47aa-9be9-a9ee80ccdcc8',
        u'deleted_at': None, u'id': 32}],
    u'snapshot_id': None, u'replication_status': None,
    u'volume_id': u'5e41d178-4349-47aa-9be9-a9ee80ccdcc8',
    u'replication_extended_status': None,
    u'user_id': u'609544a5d1de4023b44bb71d624281ab', u'size': 1,
    u'launched_at': u'2017-05-28T10:42:05+00:00',
    u'replication_driver_data': None, u'metadata': []}
