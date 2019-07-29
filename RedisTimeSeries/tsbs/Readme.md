
### Auto benchmarking insert/write performance

#### Context

The following script includes:
- Resets stats from redis and flushes db
- Saves the output of tsbs benchmarking insert/write performance
- Saves the output of Commandstats only for TS.* commands
- Saves INFO after running benchmark

-------
#### Included executables

We recur to TSBS to measure insert/write performance by taking the data generated and stored in our s3 bucket and using it as input to a database-specific command
line program.
 
 We maked usage of previously compiled (for linux and darwin OSs, and amd64 architecture):

- tsbs_load_redistimeseries : used for bechmarking insert/write performance.
- redis-cli  : used for retrieving general statistics from Redis and executing auxiliary commands between benchmarks like flushall.


#### Included datasets

We've generated and included in our s3 bucket the following datasets. Please denote that some are not fit for pipeline due to the timetaken to run:

|Query type|Cardinality|Rows|Benchmark name| Expected time to complete on pipeline | Fit for pipeline?
|:---|:---|:---|:---|:---|:---|
|1 month interval for 100 devices x 1 metric| 100 | 25M | redistimeseries-data-1month-100devices-1metric | | No
|3 days interval for 100 devices x 10 metrics| 1000 | 2.6M | redistimeseries-data-3days-100devices-10metrics | 60s | Yes
|1 month interval for 100 devices x 10 metrics| 1000 | 25M | redistimeseries-data-1month-100devices-10metrics | | No
|3 days for 4,000 devices x 10 metrics| 40K | 25M | redistimeseries-data-3days-4000devices-10metrics| | No
|3 minutes for 4,000 devices x 10 metrics| 40K | 2.6M | redistimeseries-data-3minutes-4000devices-10metrics| | Yes
|3 hours for 4,000 devices x 10 metrics| 1M | 26M | redistimeseries-data-3hours-100Kdevices-10metrics| | No
|3 minutes for 4,000 devices x 10 metrics| 1M | 2.6M | redistimeseries-data-3minutes-100Kdevices-10metrics | | Yes
|3 minutes for 1,000,000 devices x 10 metrics| 10M | 26M | redistimeseries-data-3minutes-1Mdevices-10metrics| | No

#### Integrating automatic tests to benchmark insert/write performance

So for integrating automatic tests to benchmark insert/write performance you need to retrieve the project and its dependencies:
0) Install pre-requesites
    ```bash
    $ git clone https://github.com/filipecosta90/RedisModulesBenchmarks.git
    $ cd RedisTimeSeries/tsbs
    $ pip3 install -r requirements.txt
    ```

1) Run benchmark insert/write performance passing as argument the datasets to be tested, the Redis and RedisTimeSeries versions being used, as well as the architecture and OS of the machine running it:
    ```bash
    $ python3 load.py --redistimeseries_version "oss_1.0.0" --redis_version "oss_5.0.4" --verbose --os "darwin" --arch "amd64"
    ```
--------

#### Generated output

Information regarding the required executables and datasets is printed to the stdout, as well as statistics about the load performance are printed every 1s.,
The complete test log will be saved on the performance s3 bucket for further analysis in the following path:
 - benchmarks/redistimeseries/tsbs/results/{redis_version}/{redistimeseries_version}/{benchmark_output_filename}.


An example execution output:
```text
$ python3 load.py --redistimeseries_version "oss_1.0.0" --redis_version "oss_5.0.4" --verbose --os "darwin" --arch "amd64"
INFO:botocore.credentials:Found credentials in environment variables.
INFO:root:Will run tsbs_load_redistimeseries for dataset redistimeseries-data-3days-100devices-10metrics
INFO:root:Downloading: benchmarks/redistimeseries/tsbs/gz/redistimeseries-data-3days-100devices-10metrics.gz
INFO:root:flushing redis db
OK
INFO:root:resetting stats info
OK
INFO:root:Benchmarking insert/write performance. Saving output to file LOG_RAW_redistimeseries-data-3days-100devices-10metrics_oss_5.0.4_oss_1.0.0_2019_07_29_11_02_13.log
time,per. metric/s,metric total,overall metric/s,per. row/s,row total,overall row/s
1564394534,588867.41,5.910000E+05,588867.41,59783.49,6.000000E+04,59783.49
1564394535,400815.81,9.910000E+05,495107.35,40081.58,1.000000E+05,49960.38
1564394536,598488.77,1.591000E+06,529607.56,59848.88,1.600000E+05,53260.35
1564394537,600231.67,2.191000E+06,547240.35,60023.17,2.200000E+05,54948.83
1564394538,599959.03,2.791000E+06,557776.81,59995.90,2.800000E+05,55957.54
1564394539,601317.90,3.391000E+06,565015.82,60131.79,3.400000E+05,56651.54
1564394540,600209.06,3.991000E+06,570040.78,60020.91,4.000000E+05,57132.63
1564394541,600313.53,4.591000E+06,573822.55,60031.35,4.600000E+05,57494.74
1564394542,798367.46,5.391000E+06,598815.29,79836.75,5.400000E+05,59981.50
1564394543,799833.56,6.191000E+06,618915.30,79983.36,6.200000E+05,61981.50
1564394544,400419.77,6.591000E+06,599076.39,40041.98,6.600000E+05,59989.44
1564394545,598834.86,7.191000E+06,599056.23,59883.49,7.200000E+05,59980.60
1564394546,601340.58,7.791000E+06,599231.53,60134.06,7.800000E+05,59992.38
1564394547,598215.97,8.391000E+06,599158.80,59821.60,8.400000E+05,59980.14
1564394548,802733.13,9.191000E+06,612683.11,80273.31,9.200000E+05,61328.31
1564394549,798400.72,9.991000E+06,624311.36,79840.07,1.000000E+06,62487.37
1564394550,799234.00,1.079100E+07,634608.25,79923.40,1.080000E+06,63513.75
1564394551,801705.45,1.159100E+07,643870.62,80170.55,1.160000E+06,64437.06
1564394552,600930.40,1.219100E+07,641614.17,60093.04,1.220000E+06,64208.78
1564394553,1000121.85,1.319100E+07,659537.01,100012.19,1.320000E+06,65998.70
1564394554,796113.04,1.399100E+07,666070.75,79611.30,1.400000E+06,66649.92
1564394555,803957.16,1.479100E+07,672307.36,80395.72,1.480000E+06,67271.64
1564394556,798647.80,1.559100E+07,677809.23,79864.78,1.560000E+06,67820.05
1564394557,598870.57,1.619100E+07,674514.46,59887.06,1.620000E+06,67488.94
1564394558,801247.65,1.699100E+07,679575.41,80124.77,1.700000E+06,67993.54
1564394559,801515.40,1.779100E+07,684256.46,80151.54,1.780000E+06,68460.26
1564394560,599910.55,1.839100E+07,681132.14,59991.06,1.840000E+06,68146.55
1564394561,799844.78,1.919100E+07,685372.58,79984.48,1.920000E+06,68569.40
1564394562,599908.26,1.979100E+07,682425.18,59990.83,1.980000E+06,68273.55
1564394563,800452.09,2.059100E+07,686357.13,80045.21,2.060000E+06,68665.71
1564394564,797445.12,2.139100E+07,689951.68,79744.51,2.140000E+06,69024.20
1564394565,800000.31,2.219100E+07,693390.31,80000.03,2.220000E+06,69367.15
1564394566,801520.58,2.299100E+07,696660.60,80152.06,2.300000E+06,69693.33
1564394567,800869.20,2.379100E+07,699722.17,80086.92,2.380000E+06,69998.69
1564394568,798662.13,2.459100E+07,702553.57,79866.21,2.460000E+06,70281.07
1564394569,800387.82,2.539100E+07,705269.74,80038.78,2.540000E+06,70551.97

Summary:
loaded 25920000 metrics in 36.637sec with 2 workers (mean rate 707481.84 metrics/sec)
loaded 2592900 rows in 36.637sec with 2 workers (mean rate 70772.75 rows/sec)
INFO:root:Saving used benchmark insert/write performance command into file LOG_RAW_redistimeseries-data-3days-100devices-10metrics_oss_5.0.4_oss_1.0.0_2019_07_29_11_02_13.log
INFO:root:retrive RedisTimeSeries commandstats into file LOG_RAW_redistimeseries-data-3days-100devices-10metrics_oss_5.0.4_oss_1.0.0_2019_07_29_11_02_13.log
INFO:root:retrive full info command output into file LOG_RAW_redistimeseries-data-3days-100devices-10metrics_oss_5.0.4_oss_1.0.0_2019_07_29_11_02_13.log
INFO:root:Saving results in file benchmarks/redistimeseries/tsbs/results/oss_5.0.4/oss_1.0.0/LOG_RAW_redistimeseries-data-3days-100devices-10metrics_oss_5.0.4_oss_1.0.0_2019_07_29_11_02_13.log
INFO:root:removing local file redistimeseries-data-3days-100devices-10metrics.gz
INFO:root:removing local file LOG_RAW_redistimeseries-data-3days-100devices-10metrics_oss_5.0.4_oss_1.0.0_2019_07_29_11_02_13.log
INFO:root:total time to setup and run     58.444 secs
INFO:root:removing local copy of redis-cli
INFO:root:removing local copy of tsbs_load_redistimeseries
```


