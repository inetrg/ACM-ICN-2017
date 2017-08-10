/*
 * Copyright (C) 2017 HAW Hamburg
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
 */

/**
 * @file
 *
 * @author      Peter Kietzann <peter.kietzmann@haw-hamburg.de>
 *
 */


#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

#include "xtimer.h"
#include "random.h"
#include "thread.h"
#include "net/netstats.h"
#include "net/ipv6/addr.h"
#include "net/gnrc/ipv6/netif.h"
#include "net/gnrc/netif.h"
#include "net/gnrc/netapi.h"
#include "net/netopt.h"
#include "net/gnrc/pkt.h"
#include "net/gnrc/pktbuf.h"
#include "net/gnrc/netif/hdr.h"
#include "net/gnrc/sixlowpan/netif.h"


int main(void)
{

    kernel_pid_t dev;
    gnrc_pktsnip_t *pkt, *hdr;
    char data[20];

    /* Any long hardware address */
    uint8_t hwaddr[8] = {0xca, 0xfe, 0xbe, 0xef, 0xca, 0xff, 0x8f, 0xee};

    gnrc_netif_get(&dev);

    uint16_t chan = 20; // SYNC WITH ccn_exp
    int ret = gnrc_netapi_set(dev, NETOPT_CHANNEL, 0, &chan, sizeof(chan));
    if (ret < 0) {
        printf("Error setting channel %i, returned with %i\n", chan, ret);
    }
    uint8_t retrans = 0;
    ret = gnrc_netapi_set(dev, NETOPT_RETRANS, 0, &retrans, sizeof(retrans));
    if (ret < 0) {
        printf("Error setting retrans %i, returned with %i\n", retrans, ret);
    }
    bool csma = 0;
    ret = gnrc_netapi_set(dev, NETOPT_CSMA, 0, &csma, sizeof(csma));
    if (ret < 0) {
        printf("Error setting csma %i, returned with %i\n", retrans, ret);
    }
    bool ack_req = 0;
    ret = gnrc_netapi_set(dev, NETOPT_ACK_REQ, 0, &ack_req, sizeof(ack_req));
    if (ret < 0) {
        printf("Error setting ACK REQ returned with %i\n", ret);
    }

    random_init(xtimer_now().ticks32);
    while(1){
        // put packet together
        pkt = gnrc_pktbuf_add(NULL, &data, sizeof(data), GNRC_NETTYPE_UNDEF);
        if (pkt == NULL) {
            puts("error: packet buffer full");
            return 1;
        }
        hdr = gnrc_netif_hdr_build(NULL, 0, hwaddr, sizeof(hwaddr));
        if (hdr == NULL) {
            puts("error: packet buffer full");
            gnrc_pktbuf_release(pkt);
            return 1;
        }
        LL_PREPEND(pkt, hdr);

        if (gnrc_netapi_send(dev, pkt) < 1) {
            puts("error: unable to send");
            gnrc_pktbuf_release(pkt);
            return 1;
        }
        xtimer_usleep(random_uint32_range(3000, 10000));
    }
    return 0;
}