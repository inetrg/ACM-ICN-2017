#!/usr/bin/env python2
#
# Copyright (C) Peter Kietzmann <peter.kietzmann@haw-hamburg.de>

import subprocess, os, datetime, sys, threading, time, csv
from functions import *


#### Input parameters from script automate_calls_single_hop.py ####

# CPY_OML_FILES not used here
RIOT_APP                =sys.argv[2]
EXP_NAME                =sys.argv[3]
# DUMMY not used here
blub=sys.argv[4]
CCN_FIB_MODE            =sys.argv[5]
MIN_INTEREST_PERIOD     =int(sys.argv[6])
NUM_CONTENTS            =int(sys.argv[7])
IOTLAB_PHY_NUM_NODES    =int(sys.argv[8])
INTEREST_INTERVAL       =float(sys.argv[9])
NUM_RND_INTERESTS       =int(sys.argv[10])
IOTLAB_DURATION         =int(sys.argv[11])
IOTLAB_USER             =sys.argv[12]
IOTLAB_TYPE             =sys.argv[13]
IOTLAB_SITE             =sys.argv[14]
IOTLAB_PROFILE          =sys.argv[15]
IOTLAB_AUTHORITY        =sys.argv[16]
ROUTES                  =sys.argv[17]

print RIOT_APP
print EXP_NAME
print CCN_FIB_MODE
print MIN_INTEREST_PERIOD
print NUM_CONTENTS
print IOTLAB_PHY_NUM_NODES
print INTEREST_INTERVAL
print NUM_RND_INTERESTS
print IOTLAB_DURATION
print IOTLAB_USER
print IOTLAB_TYPE
print IOTLAB_SITE
print IOTLAB_PROFILE
print IOTLAB_AUTHORITY
print ROUTES

if IOTLAB_PROFILE == 'none':
    IOTLAB_PROFILE = ''

### functions ####

all_names=[];
periodic_counter=0;
iotlab_consumer_node = 999;

def periodic():
    global next_call
    global periodic_counter
    global p

    # next call
    next_call = next_call+INTEREST_INTERVAL
    t = threading.Timer( next_call - time.time(), periodic )
    t.start()

    if periodic_counter < len(all_names):
        ccnl_int = ' ccnl_int '+all_names[periodic_counter]
        p.stdin.write('m3-'+str(iotlab_consumer_node)+';'+ccnl_int+'\n')
        small_delay()
        p.stdin.write('m3-'+str(iotlab_consumer_node)+'; clean\n')

    else:
        t.cancel()
        # turn leds on after completion to identify exp end in energy profile
        p.stdin.write(' leds_on\n')
        time.sleep(10)
        p.stdin.write(' ccnl_stats\n')
        small_delay()
        p.stdin.write(' ifconfig\n')
        small_delay()
        p.stdin.write(' ps\n')
        sys.exit()

    #incdement loop counter
    periodic_counter+=1



#### Build applications ####

THIS_PATH_EVAL = os.getcwd();

RIOT_APP_PATH       = "../applications/"
BINARY           = RIOT_APP_PATH+RIOT_APP+'/bin/iotlab-m3/'+RIOT_APP+'.elf'

myenv = dict(os.environ)
myenv["BOARD"] = 'iotlab-m3';

# change to tx app dir and build
os.chdir(RIOT_APP_PATH+RIOT_APP)
subprocess.check_call(["make", "clean", "all"], env=myenv)


#### Submit experiment ####

os.chdir(THIS_PATH_EVAL)

# exclude these nodes in Lille due do duplicate addresses and defect nodes
exclude=[6, 11, 35, 36, 37, 42, 9, 15, 19, 26, 31, 34, 50, 57, 67, 69, 76, 88, 91, 96, 117, \
122, 135, 136, 139, 144, 151, 154, 157, 167, 173, 182, 189, 201, 210, 223, 223, 233, 258]


# check for active nodes and select the first IOTLAB_PHY_NUM_NODES
# +1 for consumer node
exp_nodes_str, exp_nodes= get_active_nodes(IOTLAB_SITE, IOTLAB_PHY_NUM_NODES+1, exclude)
iotlab_consumer_node = exp_nodes[-1]


if ROUTES == 'all_default':
    # remove last entry because array will be used for produces only
    # in this case
    exp_producers = exp_nodes[:-1]

print 'EXP_NODES: '+str(exp_nodes)
print 'iotlab_consumer_node: '+str(iotlab_consumer_node)

# now that binarys and everything are there, build this helper 
NODES_PARAM = (" -l "+IOTLAB_SITE+','+IOTLAB_TYPE+','+exp_nodes_str+','+BINARY+','+IOTLAB_PROFILE)

# submit new experiment
p = subprocess.Popen(["experiment-cli submit -n "+EXP_NAME+" -d "+str(IOTLAB_DURATION)+NODES_PARAM],
    shell=True, stdout=subprocess.PIPE)
stdout_value,stderr_value = p.communicate()

if stdout_value:
    stdout_value = stdout_value.split()
    # get ID of experiment
    IOTLAB_EXP_ID =stdout_value[2]
    print 'Experiment ID is '+IOTLAB_EXP_ID
else:
    print 'Error. Exit program'
    sys.exit()

# wait until the experiment has started
print ["experiment-cli wait -i "+IOTLAB_EXP_ID]
p = subprocess.Popen(["experiment-cli wait -i"+IOTLAB_EXP_ID], shell=True, stdout=subprocess.PIPE)
stdout_value,stderr_value = p.communicate()
if stdout_value:
    stdout_value = stdout_value.split()


#### start serial aggregation ####

p = subprocess.Popen(["ssh "+IOTLAB_AUTHORITY+" serial_aggregator -i "+IOTLAB_EXP_ID],
    shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, bufsize=0)

# initialize all producers with contents and return all contents in random order
if ROUTES == 'all_default':
    all_names = init_all_producers_pre(p, exp_producers, NUM_CONTENTS, '/t')
elif ROUTES == 'none':
    all_names = init_all_producers(p, exp_nodes, NUM_CONTENTS)

# fill FIB(s)
if CCN_FIB_MODE=='broadcast':
    print 'CCN_FIB_MODE is '+CCN_FIB_MODE

    # all nodes get an entry mapping to the broadcast address
    if ROUTES == 'all_default':
        init_all_default_routes(p, exp_nodes, '/t')
    # only consumer gets FIB entrys
    elif ROUTES == 'none':
        init_consumer_broadcast(p, exp_nodes, iotlab_consumer_node)

elif CCN_FIB_MODE=='unicast':
    print 'CCN_FIB_MODE is '+CCN_FIB_MODE
    # the list contains hardware address of all nodes, generated during RIOT startup
    import_hw_addys = open('../lille_nodes_hwaddy_fmt.txt', 'r')
    hw_addys = csv.reader(import_hw_addys)
    hw_addys = list(hw_addys)

    if ROUTES == 'all_default':
        init_consumer_unicast_pre(p, exp_nodes, iotlab_consumer_node, hw_addys, '/t')

    elif ROUTES == 'none':
        init_consumer_unicast(p, exp_nodes, iotlab_consumer_node, hw_addys)
else:
    print 'CCN_FIB_MODE can not be handeled'
    sys.exit()


#### Generate debug file and start content requests ####


# write the output data to file and give the filename the time
now = datetime.datetime.now()
file_name_string = str(IOTLAB_EXP_ID)+'-'+RIOT_APP+'-'+CCN_FIB_MODE+'-'+str(IOTLAB_PHY_NUM_NODES)+\
                    '-nodes-'+str(NUM_CONTENTS)+'-contents-'+str(INTEREST_INTERVAL)+'-interval-'+\
                    ROUTES+'-'+str(now.hour)+str(now.minute)
thefile = open('../'+file_name_string+'.txt', 'a')
thefile.write('m3-'+str(iotlab_consumer_node)+' consumer\n')
thefile.write(str(IOTLAB_PHY_NUM_NODES)+' producer nodes\n')
thefile.write(str(NUM_CONTENTS)+' contents on each producer\n')
thefile.write(str(len(all_names))+' contents to request\n')
thefile.write(str(INTEREST_INTERVAL)+' sec interval\n')

# guard
time.sleep(5)

# turn off LEDs at beginning and on after experiment completion (for eventual power profiling)
p.stdin.write(' leds_off\n')
p.stdin.write('m3-'+str(iotlab_consumer_node)+'; ccnl_dump\n')

# Will request all content items with a fixed rate
next_call = time.time()
periodic()

# write outout to file
for line in iter(p.stdout.readline, ''):
    print line
    thefile.write("%s " % line)

# close file
thefile.close()