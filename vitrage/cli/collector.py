# Copyright 2017 - Nokia
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

import cotyledon
import sys


from vitrage.cli import VITRAGE_TITLE
from vitrage.common import utils
from vitrage.datasources.listener_service import ListenerService
from vitrage.datasources.rpc_service import CollectorRpcHandlerService
from vitrage import service


class CollectorService(cotyledon.Service):

    def __init__(self, worker_id, conf):
        super(CollectorService, self).__init__(worker_id)
        self.csvc = CollectorRpcHandlerService(conf)
        utils.spawn(self.csvc.start)
        self.lsvc = ListenerService(conf)
        utils.spawn(self.lsvc.start)

    def terminate(self):
        super(CollectorService, self).terminate()
        self.lsvc.stop()
        self.csvc.stop()


def main():

    """Starts all the datasources drivers services"""

    print(VITRAGE_TITLE)
    conf = service.prepare_service()
    sm = cotyledon.ServiceManager()
    sm.add(CollectorService, args=(conf,))
    sm.run()


if __name__ == "__main__":
    sys.exit(main())
