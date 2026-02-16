#include "syscall.h"

/* ---- Network constants ---- */

#define ETH_ALEN       6
#define ETH_HLEN       14
#define ETH_TYPE_ARP   0x0806
#define ETH_TYPE_IP    0x0800

#define ARP_OP_REQUEST 1
#define ARP_OP_REPLY   2

#define IP_PROTO_UDP   17

/* Our hardcoded SLIRP IP: 10.0.2.15 */
static const uint8_t our_ip[4] = {10, 0, 2, 15};

static uint8_t our_mac[6];
static uint8_t pkt_buf[1600];
static uint8_t tx_buf[1600];

/* ---- Byte-order helpers (network = big-endian) ---- */

static inline uint16_t ntohs(uint16_t n) {
    return (n >> 8) | (n << 8);
}

static inline uint16_t htons(uint16_t h) {
    return (h >> 8) | (h << 8);
}

static inline uint32_t ntohl(uint32_t n) {
    return ((n >> 24) & 0xFF) |
           ((n >> 8) & 0xFF00) |
           ((n << 8) & 0xFF0000) |
           ((n << 24) & 0xFF000000);
}

/* ---- Helpers ---- */

static void mcpy(void *dst, const void *src, uint32_t n) {
    uint8_t *d = (uint8_t *)dst;
    const uint8_t *s = (const uint8_t *)src;
    for (uint32_t i = 0; i < n; i++) d[i] = s[i];
}

static int ip_match(const uint8_t *a, const uint8_t *b) {
    return a[0]==b[0] && a[1]==b[1] && a[2]==b[2] && a[3]==b[3];
}

/* ---- IP header checksum ---- */

static uint16_t ip_checksum(const uint8_t *hdr, uint32_t len) {
    uint32_t sum = 0;
    for (uint32_t i = 0; i < len; i += 2) {
        uint16_t word = ((uint16_t)hdr[i] << 8);
        if (i + 1 < len)
            word |= hdr[i + 1];
        sum += word;
    }
    while (sum >> 16)
        sum = (sum & 0xFFFF) + (sum >> 16);
    return (uint16_t)(~sum);
}

/* ---- ARP handler ---- */

static void handle_arp(const uint8_t *pkt, uint32_t len) {
    if (len < ETH_HLEN + 28) return;  /* ARP packet = 28 bytes */

    const uint8_t *arp = pkt + ETH_HLEN;
    uint16_t op = ((uint16_t)arp[6] << 8) | arp[7];

    if (op != ARP_OP_REQUEST) return;

    /* Target IP is at arp+24 (4 bytes) */
    if (!ip_match(arp + 24, our_ip)) return;

    /* Build ARP reply */
    uint8_t *tx = tx_buf;

    /* Ethernet header: dst = sender MAC, src = our MAC, type = ARP */
    mcpy(tx, pkt + ETH_ALEN, ETH_ALEN);  /* dst = original sender */
    mcpy(tx + ETH_ALEN, our_mac, ETH_ALEN);  /* src = us */
    tx[12] = 0x08; tx[13] = 0x06;  /* EtherType ARP */

    /* ARP payload */
    uint8_t *reply = tx + ETH_HLEN;
    reply[0] = 0x00; reply[1] = 0x01;  /* hardware type: Ethernet */
    reply[2] = 0x08; reply[3] = 0x00;  /* protocol type: IPv4 */
    reply[4] = 6;    /* hw addr len */
    reply[5] = 4;    /* proto addr len */
    reply[6] = 0x00; reply[7] = 0x02;  /* opcode: reply */

    /* Sender = us */
    mcpy(reply + 8, our_mac, 6);
    mcpy(reply + 14, our_ip, 4);

    /* Target = original sender */
    mcpy(reply + 18, arp + 8, 6);   /* sender hw addr from request */
    mcpy(reply + 24, arp + 14, 4);  /* sender proto addr from request */

    sys_net_send(tx, ETH_HLEN + 28);
}

/* ---- UDP echo handler ---- */

static void handle_ip(const uint8_t *pkt, uint32_t len) {
    if (len < ETH_HLEN + 20) return;  /* minimum IP header */

    const uint8_t *ip = pkt + ETH_HLEN;
    uint8_t ihl = (ip[0] & 0x0F) * 4;
    if (len < ETH_HLEN + (uint32_t)ihl) return;

    uint8_t proto = ip[9];
    if (proto != IP_PROTO_UDP) return;

    /* Check destination IP is us */
    if (!ip_match(ip + 16, our_ip)) return;

    const uint8_t *udp = ip + ihl;
    uint32_t udp_off = ETH_HLEN + ihl;
    if (len < udp_off + 8) return;

    uint16_t dst_port = ((uint16_t)udp[2] << 8) | udp[3];
    uint16_t src_port = ((uint16_t)udp[0] << 8) | udp[1];
    uint16_t udp_len  = ((uint16_t)udp[4] << 8) | udp[5];

    if (dst_port != 7) return;  /* only echo port */

    if (len < udp_off + udp_len) return;

    sys_debug_write("NET: udp echo\n", 14);

    /* Build echo reply */
    uint8_t *tx = tx_buf;
    uint32_t total = ETH_HLEN + (uint32_t)ihl + udp_len;
    if (total > 1514) return;

    /* Copy entire original packet */
    mcpy(tx, pkt, ETH_HLEN + (uint32_t)ihl + udp_len);

    /* Swap Ethernet MACs */
    mcpy(tx, pkt + ETH_ALEN, ETH_ALEN);       /* dst = original src */
    mcpy(tx + ETH_ALEN, our_mac, ETH_ALEN);   /* src = us */

    /* Swap IP addresses */
    uint8_t *tip = tx + ETH_HLEN;
    mcpy(tip + 12, ip + 16, 4);  /* src IP = original dst (us) */
    mcpy(tip + 16, ip + 12, 4);  /* dst IP = original src */

    /* Recalculate IP checksum */
    tip[10] = 0; tip[11] = 0;
    uint16_t cksum = ip_checksum(tip, ihl);
    tip[10] = (uint8_t)(cksum >> 8);
    tip[11] = (uint8_t)(cksum & 0xFF);

    /* Swap UDP ports */
    uint8_t *tudp = tip + ihl;
    tudp[0] = (uint8_t)(dst_port >> 8);
    tudp[1] = (uint8_t)(dst_port & 0xFF);
    tudp[2] = (uint8_t)(src_port >> 8);
    tudp[3] = (uint8_t)(src_port & 0xFF);

    /* Zero UDP checksum (optional for IPv4) */
    tudp[6] = 0; tudp[7] = 0;

    sys_net_send(tx, total);
}

/* ---- Main ---- */

void main(void) {
    sys_net_get_mac(our_mac);

    sys_debug_write("NETD: start\n", 12);

    for (;;) {
        int64_t n = sys_net_recv(pkt_buf, sizeof(pkt_buf));
        if (n <= 0) {
            sys_yield();
            continue;
        }

        uint32_t len = (uint32_t)n;
        if (len < ETH_HLEN) continue;

        uint16_t eth_type = ((uint16_t)pkt_buf[12] << 8) | pkt_buf[13];

        if (eth_type == ETH_TYPE_ARP)
            handle_arp(pkt_buf, len);
        else if (eth_type == ETH_TYPE_IP)
            handle_ip(pkt_buf, len);
    }
}
