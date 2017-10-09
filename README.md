# ACM-ICN-2017
This repository exposes source code to reproduce experiments as presented in the paper:
"The Need for a Name to MAC Address Mapping in NDN: Towards Quantifying the Resource Gain".

## Prerequisites
Our experiments base on different Open Source software a hardware platforms: 
- [RIOT](https://github.com/RIOT-OS/RIOT)
- [CCN-lite](https://github.com/cn-uofbasel/ccn-lite)
- [FIT IoT-LAB](https://www.iot-lab.info/)

Thereby we use the [M3 nodes](https://www.iot-lab.info/hardware/m3/) (`iotlab-m3`
in RIOT). For prerequisites of the software platforms, please refer to the particular community. To deploy
the scenarios on the testbed you need an account which can be requested [here](https://www.iot-lab.info/testbed/signup.php).

Furthermore we use python2 scripts which involde a couple of standard libraries.

## About
This repository contains submodules. To get all contents, please clone with
`git clone --recursive https://github.com/inetrg/ACM-ICN-2017.git`. The command will clone and checkout
a dedicated RIOT version (see [source code](https://github.com/inetrg/RIOT/tree/ICN_MAC)). RIOT itself
includes CCN-lite as an external software package. When CCN-lite gets build, a dedicated version will be
cloned and checked out (see [source code](https://github.com/inetrg/ccn-lite/tree/ICN_MAC). Besides
of that, the repository contains RIOT [applications](https://github.com/inetrg/ACM-ICN-2017/tree/master/applications) which will run on IoT nodes, a couple of helper [scripts](https://github.com/inetrg/ACM-ICN-2017/tree/master/scripts) to automate testing and a collection of text files that provide information
about (i) nodes hardware addresses on different IoT-LAB sites and (ii) a static topology for
multi-hop measurements. This topology was discovered beforehand by using an algorithm as described in
the draft: [draft-gundogan-icnrg-pub-iot-01](https://datatracker.ietf.org/doc/draft-gundogan-icnrg-pub-iot/).

## Execution
The script [automate_calls.py](https://github.com/inetrg/ACM-ICN-2017/blob/master/scripts/automate_calls.py)
can be used to configure different measurement setups (e.g. different network sizes, numbers of content
items per producer, single-hop or multi-hop). For further documentation refer to the comments in the file.

Once an experiment runs, the aggregated serial output of all nodes will be logged in a file that will be
stored in the root directory of your repository clone. To identify different dumps, a couple of experiment
information as well as the unique experiment ID are part of the file name. These files can be incorporated for further post processing.

## Special Modes
The provided test [application](https://github.com/inetrg/ACM-ICN-2017/tree/master/applications/ccn_exp) provides two special modes which can be enabled by `CFLAGS`. Proper dummies can be found in the
applications [Makefile](https://github.com/inetrg/ACM-ICN-2017/blob/master/applications/ccn_exp/Makefile#L22).
`USE_DUP_CHECK` enables a duplicate nonce check which drops packets (i.e. Interests) that have already
been sent/forwarded.
`ALLOW_DATA_BCAST` enforces data packets to be send via broadcast MAC address.