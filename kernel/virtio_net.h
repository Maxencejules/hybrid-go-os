#ifndef VIRTIO_NET_H
#define VIRTIO_NET_H

#include <stdint.h>

int  virtio_net_init(void);
int  virtio_net_send(const void *frame, uint32_t len);
int  virtio_net_recv(void *frame, uint32_t max_len);
void virtio_net_get_mac(uint8_t mac[6]);

#endif
