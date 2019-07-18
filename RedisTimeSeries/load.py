#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""sample module for redistimeseries tsbs benchmark tests
"""

import argparse
import boto3
import os
import datetime
import logging
import botocore


parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, help="redis instance port", default=6379)
parser.add_argument(
    "--password", type=int, help="redis instance password", default=None
)
parser.add_argument("--verbose", help="enable verbose output", action="store_true")
parser.add_argument("--host", type=str, help="redis instance host", default="127.0.0.1")
parser.add_argument(
    "--benchmarks",
    type=str,
    help="dataset benchmarks to run split by comma",
    default="redistimeseries-data-3days-100devices-10metrics",
)
parser.add_argument(
    "--arch", type=str, help="arch of machine running tsbs benchmark", default="amd64"
)
parser.add_argument(
    "--os", type=str, help="os of machine running tsbs benchmark", default="darwin"
)
parser.add_argument("--load_workers", type=int, help="tsbs load workers", default=2)
parser.add_argument(
    "--load_reporting_period",
    type=str,
    help="tsbs load tool reporting period in seconds",
    default="1s",
)
parser.add_argument(
    "--load_connections",
    type=int,
    help="tsbs load tool number of connections per worker",
    default=10,
)
parser.add_argument(
    "--load_batch_size", type=int, help="tsbs load tool batch size", default=10000
)
parser.add_argument(
    "--load_pipeline",
    type=int,
    help="tsbs load tool Redis pipeline's size.",
    default=100,
)
parser.add_argument(
    "--redistimeseries_version",
    type=str,
    help="RedisTimeSeries version number to which the tsbs load will be runned against.",
    default="NA",
)
parser.add_argument(
    "--redisenterprise_version",
    type=str,
    help="Redis version number to which the tsbs load will be runned against.",
    default="NA",
)

args = parser.parse_args()

log_level = logging.ERROR
if args.verbose is True:
    log_level = logging.INFO
logging.basicConfig(level=log_level)

s3 = boto3.resource("s3")

exec_os = args.os
arch = args.arch
load_host = "{}:{}".format(args.host, args.port)
load_workers = args.load_workers
load_reporting_period = args.load_reporting_period
load_batch_size = args.load_batch_size
load_connections = args.load_connections
load_pipeline = args.load_pipeline
redistimeseries_version = args.redistimeseries_version
redisenterprise_version = args.redisenterprise_version

bucket_name = "performance-cto-group"

common_key = "benchmarks/redistimeseries/tsbs/"

benchmark_tests = ["redistimeseries-data-3days-100devices-10metrics"]

####### dont change bellow this line #######

bucket = s3.Bucket(bucket_name)

with open("tsbs_load_redistimeseries", "wb") as data:
    bucket.download_fileobj(
        "{common_key}executables/{os}_{arch}__tsbs_load_redistimeseries".format(
            common_key=common_key, os=exec_os, arch=arch
        ),
        data,
    )

os.chmod("tsbs_load_redistimeseries", 0o711)


with open("redis-cli", "wb") as data:
    bucket.download_fileobj(
        "{common_key}executables/{os}_{arch}__redis-cli".format(
            common_key=common_key, os=exec_os, arch=arch
        ),
        data,
    )

os.chmod("redis-cli", 0o711)

for benchmark_test in benchmark_tests:
    benchmark_test_filename = "{}.gz".format(benchmark_test)
    logging.info(
        "Will run tsbs_load_redistimeseries for dataset {}".format(benchmark_test)
    )
    try:
        with open(benchmark_test_filename, "wb") as data:
            bucket.download_fileobj(
                "{common_key}gz/{benchmark}.gz".format(
                    common_key=common_key, benchmark=benchmark_test
                ),
                data,
            )

        # clear the database
        cmd = "./redis-cli -h {h} -p {p} flushall".format(
            h=load_host.split(":")[0], p=load_host.split(":")[1]
        )
        os.system(cmd)

        # reset stats info
        cmd = "./redis-cli -h {h} -p {p} config resetstat".format(
            h=load_host.split(":")[0], p=load_host.split(":")[1]
        )
        os.system(cmd)

        test_date_time = datetime.datetime.now()
        output_file = "LOG_RAW_{test}_{version}_{time}.log".format(
            test=benchmark_test,
            version=redistimeseries_version,
            time=test_date_time.strftime("%Y_%m_%d_%H_%M_%S"),
        )

        benchmark_cmd = "cat {benchmark_test}.gz | gunzip | ./tsbs_load_redistimeseries -host {host} -workers {workers} -reporting-period {reporting_period} -batch-size {batch_size} -connections {connections} -pipeline {pipeline} 2>&1 | tee {output_file}".format(
            benchmark_test=benchmark_test,
            host=load_host,
            workers=load_workers,
            reporting_period=load_reporting_period,
            batch_size=load_batch_size,
            connections=load_connections,
            pipeline=load_pipeline,
            output_file=output_file,
        )
        os.system(benchmark_cmd)

        cmd = 'echo "# Benchmark command" >> {output_file} && echo "" >> {output_file} && echo "{cmd}" >> {output_file}'.format(
            cmd=benchmark_cmd, output_file=output_file
        )
        os.system(cmd)

        # retrive RedisTimeSeries commandstats
        cmd = "./redis-cli -h {h} -p {p} info commandstats | grep ts. >> {output_file}".format(
            h=load_host.split(":")[0],
            p=load_host.split(":")[1],
            output_file=output_file,
        )
        os.system(cmd)

        # retrive full info
        cmd = "./redis-cli -h {h} -p {p} info >> {output_file}".format(
            h=load_host.split(":")[0],
            p=load_host.split(":")[1],
            output_file=output_file,
        )
        os.system(cmd)

        output = open(output_file, "r").read()

        bucket.put_object(
            Key="{common_key}results/{version}/{filename}".format(
                common_key=common_key,
                version=redistimeseries_version,
                filename=output_file,
            ),
            Body=output,
        )

        os.remove(benchmark_test_filename)
        os.remove(output_file)

    except botocore.exceptions.ClientError as e:
        logging.error(e)


os.remove("redis-cli")
os.remove("tsbs_load_redistimeseries")
