#!/usr/bin/env python2
#
# Copyright (C) Peter Kietzmann <peter.kietzmann@haw-hamburg.de>

import subprocess, sys, math


#### CONFIGURE ####

# Not used here
CPY_OML_FILES           = 0

# Script to be called from here
SCRIPT                  = 'build_and_run.py'

# Experiment name submitted to the testbed
EXP_NAME                = 'ndn_exp_fix_conts' # single-hop
#EXP_NAME                = 'ndn_exp_fix_nodes' # single-hop
#EXP_NAME                = 'multihop'

ROUTES                  = 'all_default' # Common prefix routes in FIB on all nodes
#ROUTES                  = 'none'       # No additional routes on all nodes

CCN_FIB_MODE            = {'unicast', 'broadcast'}

NUM_CONTENTS            = [10]
#NUM_CONTENTS            = [5, 10, 15, 20, 25]

# we will reserve consumer in addition
IOTLAB_PHY_NUM_NODES    = [10]
#IOTLAB_PHY_NUM_NODES    = [10, 20, 30, 40, 50]

# Must match with applications name in '../applications/''
RIOT_APP                = 'ndn_exp'

# Use your iotlab account here. Requires configured account credentials (see 'auth-cli')
IOTLAB_USER             = 'SET-YOUR-ACCOUNT-HERE'
IOTLAB_TYPE             = 'm3'
IOTLAB_SITE             = 'lille' # used for singlehop experiments
#IOTLAB_SITE             = 'grenoble' # used for multi-hop experiments

IOTLAB_AUTHORITY        = (IOTLAB_USER+'@'+IOTLAB_SITE+".iot-lab.info")

# Profile name (e.g. power monitoring profile). Not mandatory.
IOTLAB_PROFILE          = 'none'

# We defined the minimum Interest period to be 2 seconds
MIN_INTEREST_PERIOD     = 2

# Can be used as additional input or the script
DUMMY                   = 'dummy'


#### Calls execution script with abouve settings ####

for mode in CCN_FIB_MODE:
    for num_phy_nodes in IOTLAB_PHY_NUM_NODES:
        for num_contents in NUM_CONTENTS:
            if EXP_NAME == 'ndn_exp_fix_conts':
                # rate increases linear with num nodes
                INTEREST_INTERVAL = (num_contents * 10) / float(num_phy_nodes)

            elif EXP_NAME == 'ndn_exp_fix_nodes':
                # set a statitc inverval
                INTEREST_INTERVAL = 5 # seconds

            elif EXP_NAME == 'multihop':
                INTEREST_INTERVAL = 5 # seconds
            else:
                print 'WRONT EXP_NAME GIVEN. EXETING'
                sys.exit()

            NUM_RND_INTERESTS = num_contents * num_phy_nodes
            IOTLAB_DURATION   = int(math.ceil((NUM_RND_INTERESTS * INTEREST_INTERVAL) / float(60)))+10 # result in minutes
            subprocess.Popen(['python '+SCRIPT+' '\
                            +str(CPY_OML_FILES)        +' '\
                            +RIOT_APP                  +' '\
                            +EXP_NAME                  +' '\
                            +DUMMY                     +' '\
                            +mode                      +' '\
                            +str(MIN_INTEREST_PERIOD)  +' '\
                            +str(num_contents)         +' '\
                            +str(num_phy_nodes)        +' '\
                            +str(INTEREST_INTERVAL)    +' '\
                            +str(NUM_RND_INTERESTS)    +' '\
                            +str(IOTLAB_DURATION)      +' '\
                            +IOTLAB_USER               +' '\
                            +IOTLAB_TYPE               +' '\
                            +IOTLAB_SITE               +' '\
                            +IOTLAB_PROFILE            +' '\
                            +IOTLAB_AUTHORITY          +' '\
                            +ROUTES\
                            ], shell=True).wait()

sys.exit()