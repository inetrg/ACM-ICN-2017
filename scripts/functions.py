#!/usr/bin/env python2
#
# Copyright (C) Peter Kietzmann <peter.kietzmann@haw-hamburg.de>

import subprocess, sys, time, numpy, random

def small_delay():
    time.sleep(0.35)


def get_active_nodes(site, IOTLAB_PHY_NUM_NODES, exclude):
    p = subprocess.Popen(['experiment-cli --jmespath "items[*].'+site+'.m3.Alive|[0]"  --fmt="str" info -li'], 
            shell=True, stdout=subprocess.PIPE)
    stdout_value = p.communicate()[0]
    splitted = (map(lambda y: y.split("-"),stdout_value.split("+")))
    active_nodes=[];
    for i in splitted:
        converted = map(int, i)
        if len(i) == 1: # single node
            active_nodes.append(converted)
        elif len(i) == 2: # node range
            active_nodes.append(range(converted[0], converted[1]+1))

    # array of all active nodes
    concatenated = numpy.concatenate(active_nodes[:], axis=0)

    if exclude:
        print 'EXCLUDE SET TO '+str(exclude)
        for i in exclude:
            for index, j in enumerate(concatenated):
                if j == i:
                    concatenated = numpy.delete(concatenated,index)

    iotlab_active_nodes_num = len(concatenated)
    if IOTLAB_PHY_NUM_NODES > iotlab_active_nodes_num:
        print 'ERROR: There are only '+str(iotlab_active_nodes_num)+' active nodes available on '\
                +site+' site'
        sys.exit()
    else:
        print 'Found '+str(iotlab_active_nodes_num)+' active nodes on '\
                +site+' site. Select first '+str(IOTLAB_PHY_NUM_NODES)

    out_str=[];
    for i in range(0,IOTLAB_PHY_NUM_NODES):
        out_str.append(str(concatenated[i])+'+')

    out_str = "".join(out_str)
    out_str = out_str[:-1]
    return (out_str, concatenated[:IOTLAB_PHY_NUM_NODES])


def init_all_producers(p, exp_nodes, num_contents):
    content_names=[];
    for j in range(0, num_contents):
        for i in exp_nodes:
            ccnl_cont = 'ccnl_cont /'+format(i, '03d')+'/'+format(j, '03d')+' '+format(i, '03d')+'/'+format(j, '03d')
            p.stdin.write('m3-'+str(i)+';'+ccnl_cont+'\n');

            content_names.append('/'+format(i, '03d')+'/'+format(j, '03d'))
            small_delay()

    # randomly sort the content names list -> could be done elsewhere
    content_names= list(numpy.random.permutation(content_names))
    return content_names


def init_all_producers_pre(p, exp_nodes, num_contents, prefix):
    content_names=[];
    for j in range(0, num_contents):
        for i in exp_nodes:
            ccnl_cont = 'ccnl_cont '+prefix+'/'+format(i, '03d')+'/'+format(j, '03d')+' '+format(i, '03d')+'/'+format(j, '03d')
            p.stdin.write('m3-'+str(i)+';'+ccnl_cont+'\n');

            content_names.append(prefix+'/'+format(i, '03d')+'/'+format(j, '03d'))
            small_delay()

    # randomly sort the content names list -> could be done elsewhere
    content_names= list(numpy.random.permutation(content_names))
    return content_names


def init_consumer_broadcast(p, exp_nodes, consumer_node):
    for i in exp_nodes:
        p.stdin.write('m3-'+str(consumer_node)+';  ccnl_fib add /'+format(i, '03d')+' ff:ff\n');
        small_delay()


def init_all_default_routes(p, exp_nodes_all, prefix):
    p.stdin.write(' ccnl_fib add '+prefix+' ff:ff\n');
    small_delay()


def init_consumer_unicast(p, exp_nodes, consumer_node, hw_addys):
    for i in exp_nodes:
        name = 'm3-'+str(i)
        address = hw_long_addy_by_node(name, hw_addys)
        p.stdin.write('m3-'+str(consumer_node)+';  ccnl_fib add /'+format(i, '03d')+' '+address+'\n');
        small_delay() 


def init_consumer_unicast_pre(p, exp_nodes, consumer_node, hw_addys, prefix):
    for i in exp_nodes:
        name = 'm3-'+str(i)
        address = hw_long_addy_by_node(name, hw_addys)
        p.stdin.write('m3-'+str(consumer_node)+';  ccnl_fib add '+prefix+'/'+format(i, '03d')+' '+address+'\n');
        small_delay() 


def idx_addy_by_node(node,all_addys):
    if node == all_addys: return []
    if isinstance(all_addys,str) and len(all_addys)<=1: return None
    try:
        for i,e in enumerate(all_addys):
          r = idx_addy_by_node(node,e)
          if r is not None:
            r.insert(0,i)
            return r
    except TypeError:
        pass
    return None


# assumes node in a format like 'm3-123'
def hw_short_addy_by_node(node,all_addys):
    r=idx_addy_by_node(node, all_addys)
    # r[0] indicates the "row". [1] gets the short hw address
    return all_addys[r[0]][1]


def hw_long_addy_by_node(node,all_addys):
    r=idx_addy_by_node(node, all_addys)
    # r[0] indicates the "row". [2] gets the long hw address
    return all_addys[r[0]][2]


def node_by_hw_long_addy(address,hw_addys):
    for line in hw_addys:
        if address in line:
            node = line[0]
            node =  node.split('-')[1]
    return int(node)