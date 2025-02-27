#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import argparse

from pipeline.backend.pipeline import PipeLine
from pipeline.component import Reader
from pipeline.component import DataTransform
from pipeline.component import FeldmanVerifiableSum
from pipeline.interface import Data


from pipeline.utils.tools import load_job_config


def main(config="../../config.yaml", namespace=""):
    # obtain config
    if isinstance(config, str):
        config = load_job_config(config)
    parties = config.parties
    guest = parties.guest[0]
    hosts = parties.host

    guest_train_data = {"name": "breast_homo_test", "namespace": f"experiment{namespace}"}
    host_train_data = {"name": "breast_homo_test", "namespace": f"experiment{namespace}"}

    # initialize pipeline
    pipeline = PipeLine()
    # set job initiator
    pipeline.set_initiator(role="guest", party_id=guest)
    # set participants information
    pipeline.set_roles(guest=guest, host=hosts)

    # define Reader components to read in data
    reader_0 = Reader(name="reader_0")
    # configure Reader for guest
    reader_0.get_party_instance(role="guest", party_id=guest).component_param(table=guest_train_data)
    # configure Reader for host
    reader_0.get_party_instance(role="host", party_id=hosts).component_param(table=host_train_data)

    data_transform_0 = DataTransform(name="data_transform_0")
    # get and configure DataTransform party instance of guest
    data_transform_0.get_party_instance(role="guest", party_id=guest).component_param(with_label=False, output_format="dense")
    # get and configure DataTransform party instance of host
    data_transform_0.get_party_instance(role="host", party_id=hosts).component_param(with_label=False)

    # define FeldmanVerifiableSum components
    feldmanverifiablesum_0 = FeldmanVerifiableSum(name="feldmanverifiablesum_0")

    feldmanverifiablesum_0.get_party_instance(role="guest", party_id=guest).component_param(sum_cols=[1, 2, 3], q_n=6)

    feldmanverifiablesum_0.get_party_instance(role="host", party_id=hosts).component_param(sum_cols=[1, 2, 3], q_n=6)

    # add components to pipeline, in order of task execution.
    pipeline.add_component(reader_0)
    pipeline.add_component(data_transform_0, data=Data(data=reader_0.output.data))
    pipeline.add_component(feldmanverifiablesum_0, data=Data(data=data_transform_0.output.data))

    # compile pipeline once finished adding modules, this step will form conf and dsl files for running job
    pipeline.compile()

    # fit model
    pipeline.fit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("PIPELINE DEMO")
    parser.add_argument("-config", type=str,
                        help="config file")
    args = parser.parse_args()
    if args.config is not None:
        main(args.config)
    else:
        main()
