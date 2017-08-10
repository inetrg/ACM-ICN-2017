/*
 * Copyright (C) 2015 Inria, 2017 HAW Hamburg
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
 */

/**
 * @ingroup     examples
 * @{
 *
 * @file
 * @brief       Basic ccn-lite relay example (produce and consumer via shell)
 *
 * @author      Oliver Hahm <oliver.hahm@inria.fr>
 * @author      Peter Kietzmann <peter.kietzmann@haw-hamburg.de>
 *
 * @}
 */

#include <stdio.h>

#include "tlsf-malloc.h"
#include "msg.h"
#include "shell.h"
#include "ccn-lite-riot.h"
#include "net/netopt.h"
#include "net/gnrc/netapi.h"
#include "net/gnrc/netif.h"
#include "board.h"

/* main thread's message queue */
#define MAIN_QUEUE_SIZE     (8)
static msg_t _main_msg_queue[MAIN_QUEUE_SIZE];

/* 10kB would be default in */
#define TLSF_BUFFER     (40960 / sizeof(uint32_t))
static uint32_t _tlsf_heap[TLSF_BUFFER];

int main(void)
{
    LED0_ON;
    LED1_ON;
    LED2_ON;
    tlsf_create_with_pool(_tlsf_heap, sizeof(_tlsf_heap));
    msg_init_queue(_main_msg_queue, MAIN_QUEUE_SIZE);

    puts("Basic CCN-Lite example");

    ccnl_core_init();

    ccnl_start();

    /* get the default interface */
    kernel_pid_t ifs[GNRC_NETIF_NUMOF];

    /* set the relay's PID, configure the interface to use CCN nettype */
    if ((gnrc_netif_get(ifs) == 0) || (ccnl_open_netif(ifs[0], GNRC_NETTYPE_CCN) < 0)) {
        puts("Error registering at network interface!");
        return -1;
    }
 
    uint16_t chan = 20; // This should corelate with the sniffer profile used on the testbed
    int ret = gnrc_netapi_set(ifs[0], NETOPT_CHANNEL, 0, &chan, sizeof(chan));
    if (ret < 0) {
        printf("Error setting channel %i, returned with %i\n", chan, ret);
    }

    /* Use long addresses to avoid duplicates */
    uint16_t src_len = 8;
    ret = gnrc_netapi_set(ifs[0], NETOPT_SRC_LEN, 0, &src_len, sizeof(src_len));
    if (ret < 0) {
        printf("Error setting src_len %i, returned with %i\n", src_len, ret);
    }

#if UCAST_WITH_RETRANS == 0
    puts("Disable unicast retransmits");
    bool ack_req = 0;
    ret = gnrc_netapi_set(ifs[0], NETOPT_ACK_REQ, 0, &ack_req, sizeof(ack_req));
    if (ret < 0) {
        printf("Error setting ACK REQ returned with %i\n", ret);
    }

    uint8_t retrans = 0;
    ret = gnrc_netapi_set(ifs[0], NETOPT_RETRANS, 0, &retrans, sizeof(retrans));
    if (ret < 0) {
        printf("Error setting retrans %i, returned with %i\n", retrans, ret);
    }
#endif

    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(NULL, line_buf, SHELL_DEFAULT_BUFSIZE);
    return 0;
}
