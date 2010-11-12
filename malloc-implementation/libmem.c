#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include "mem.h"

int merror;

int 
Mem_Init(int sizeOfRegion, int debug) 
{
    printf("calling: Mem_Init()!\n");

    // open the /dev/zero device
    int fd = open("/dev/zero", O_RDWR);

    // sizeOfRegion (in bytes) needs to be evenly divisible by the page size
    void *ptr = mmap(NULL, sizeOfRegion, 
		     PROT_READ | PROT_WRITE, MAP_PRIVATE, fd, 0);
    if (ptr == MAP_FAILED) {
	perror("mmap");
	return -1;
    }

    // close the device (don't worry, mapping should be unaffected)
    close(fd);
    merror = 1;
    return 0;
}

void *
Mem_Alloc(int size) 
{
    return NULL;
}

int 
Mem_Free(void *ptr) 
{
    return -1;
}

void 
Mem_Dump()
{
    printf("dump:\n");
}
