#ifndef FS_PROTOCOL_H
#define FS_PROTOCOL_H

/* FS IPC operation codes */
#define FS_OP_LIST   1
#define FS_OP_OPEN   2
#define FS_OP_READ   3
#define FS_OP_CREATE 4
#define FS_OP_WRITE  5
#define FS_OP_CLOSE  6

/* Status codes */
#define FS_OK        0
#define FS_ERR       (-1)
#define FS_NOT_FOUND (-2)

/* SimpleFS magic */
#define SFS_MAGIC    0x53465331  /* "SFS1" */

/* Package magic */
#define PKG_MAGIC    0x01474B50  /* "PKG\x01" */

/*
 * Request message (128 bytes, fits in one IPC message).
 * Used by clients (pkg, sh) to talk to fsd.
 */
struct fs_request {
    unsigned char  op;          /* FS_OP_xxx */
    unsigned char  fd;          /* file table index */
    unsigned short flags;       /* reserved */
    unsigned int   offset;      /* byte offset for READ */
    unsigned int   size;        /* bytes to read/write */
    unsigned int   reply_port;  /* caller's IPC port for response */
    char           data[112];   /* path (OPEN/CREATE) or inline data (WRITE) */
};

/*
 * Response message (128 bytes).
 * Sent by fsd back to the client's reply_port.
 */
struct fs_response {
    int            status;      /* FS_OK, FS_ERR, or FS_NOT_FOUND */
    unsigned int   size;        /* actual bytes in data[] */
    unsigned int   total_size;  /* total file size (OPEN response) */
    unsigned char  data[116];   /* inline file data (READ) or fd in data[0] (OPEN/CREATE) */
};

#endif
