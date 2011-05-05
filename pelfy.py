#!/usr/bin/env python

"""
Read an elf file and print out information about it.
Basically just a terrible objdump clone.
"""

import struct
import sys
import string

def remove_unprintable(s):
    "Remove unprintable characters from a string."""
    return ''.join([chr(c) if chr(c) in string.printable else "☆" for c in bytes(s)])

def ellipsize_data(data, size=50):
    "Ellipsize a string, keeping it at most size characters long."
    ellipsis = "…"

    if len(data) <= size:
        return remove_unprintable(data)

    if size < 3:
        raise Exception("size cannot be less than three")

    # make sure size is never even
    if size % 2 == 0:
        size -= 1

    first_part = remove_unprintable(data[:int(size/2)])
    second_part = remove_unprintable(data[-int(size/2):])

    return "%s%s%s" % (first_part, ellipsis, second_part)
    

class StructReader():
    """Read a binary structure."""

    def __init__(self, contents, start=0):
        self.contents = contents
        self.start = start
        self.current = start

    def unpack(self, strformat):
        size = struct.calcsize(strformat)
        #print("current = %s" % self.current)
        #print("size = %s" % size)
        result = struct.unpack(strformat, self.contents[self.current:self.current+size])
        self.skip(size)
        return result

    def unpackone(self, strformat):
        return self.unpack(strformat)[0]

    def skip(self, size):
        self.current += size

    def sizeread(self):
        return self.current - self.start


class ElfHeader():
    """Read the elf header.  This corresponds to the Elf64_Ehdr."""

    EI_NIDENT = 16

    def __init__(self, fullcontents):
        self.fullcontents = fullcontents
        structreader = StructReader(fullcontents)

        self.ident = structreader.unpackone("4s")

        if self.ident != b"\177ELF":
            sys.stderr.write("ERROR! File is not an elf file.\n")
            sys.exit(1)

        # 12 bytes we don't care about
        structreader.skip(12)

        self.etype, self.machine, self.version = structreader.unpack('HHI')
        self.entry, self.phoff, self.shoff = structreader.unpack('PPP')
        self.flags, self.ehsize = structreader.unpack('IH')
        self.phentsize, self.phnum = structreader.unpack('HH')
        self.shentsize, self.shnum = structreader.unpack('HH')
        self.shstrndx = structreader.unpackone('H')

        if structreader.sizeread() != self.ehsize:
            sys.stderr.write("ERROR! Actual elf header size does not equal ehsize field..\n")
            sys.exit(1)

    def __str__(self):
        retstr = ""
        retstr += "ELF HEADER (Elf64_Ehdr):\n"
        retstr += "\tobject file type (e_type): %s\n" % self.etype
        retstr += "\tarchitecture (e_machine): %s\n" % self.machine
        retstr += "\tobject file version (e_version): %s\n" % self.version
        retstr += "\tentry point virtual address (e_entry): 0x%x\n" % self.entry
        # specifies where, counting from the beginning of the file, the program
        # header table starts
        retstr += "\tprogram header table file offset (e_phoff): 0x%x\n" % self.phoff
        retstr += "\tsection header table file offset (e_shoff): 0x%x\n" % self.shoff
        retstr += "\tprocessor-specific flags (e_flags): 0x%x\n" % self.flags
        retstr += "\telf header size in bytes (e_ehsize): 0x%x\n" % self.ehsize
        # contains size of each entry in the program header table. This is useful only
        # as a run-time consistency check for the binary.
        retstr += "\tprogram header table entry size (e_phentsize): 0x%x\n" % self.phentsize
        # number of entries in the program header table
        retstr += "\tprogram header table entry count (e_phnum): 0x%x\n" % self.phnum
        retstr += "\tsection header table entry size (e_shentsize): 0x%x\n" % self.shentsize
        retstr += "\tsection header table entry count (e_shnum): 0x%x\n" % self.shnum
        retstr += "\tsection header string table index (e_shstrndx): 0x%x\n" % self.shstrndx
        return retstr

class ElfProgramHeader():
    """Read an elf program header.  This corresponds to the Elf64_Phdr structure."""

    def __init__(self, fullcontents, start, size):
        self.fullcontents = fullcontents
        self.start = start
        structreader = StructReader(fullcontents, start=start)

        self.ptype, self.flags = structreader.unpack('II')
        self.offset, self.vaddr, self.paddr = structreader.unpack('PPP')
        self.filesz, self.memsz, self.align = structreader.unpack('QQQ')

        if structreader.sizeread() != size:
            sys.stderr.write("ERROR! Actual elf program header size does not equal phentsize field..\n")
            sys.exit(1)

    def __str__(self):
        retstr = ""
        retstr += "ELF Program HEADER (Elf64_Phdr) at 0x%x:\n" % self.start
        # The different segments are represented by the program header entries 
        # with the PT_LOAD value in the p_type field
        retstr += "\tsegment type (p_type): %s (0x%x)\n" % (self._ptype(self.ptype), self.ptype)
        retstr += "\tsegment flags (p_flags): 0x%x\n" % self.flags
        # where in the file the segment starts
        retstr += "\tsegment file offset (p_offset): 0x%x\n" % self.offset
        # Where the segment is located in the processes virtual address
        # space. This is not necessarily required to be the final load address.
        # DSOs can be loaded at arbitrary addresses in the virtual address space.
        # But the relative position of the segments is important.
        retstr += "\tsegment virtual address (p_vaddr): 0x%x\n" % self.vaddr
        retstr += "\tsegment physical address (p_paddr): 0x%x\n" % self.paddr
        # How long a segment is. (The size in the file (filesz) can be smaller
        # than the address space it takes up in memory (memsz) because the first
        # filesz bytes of the memory region are initialized from the data of the
        # segment in the file, the difference is initialized to zero.  Handling
        # uninitialized variables this way has the advantage that the file size
        # can be reduced since no initialization value has to be stored, no data
        # has to be copied from disc to memory, and the memory provided by the OS
        # via the mmap interface is already initialized with zero.
        retstr += "\tsegment size in a file (p_filesz): 0x%x\n" % self.filesz
        # how large is the memory region for the segment located in the 
        # process' virtual address space
        retstr += "\tsegment size in memory (p_memsz): 0x%x\n" % self.memsz
        retstr += "\tsegment alignment (p_align): 0x%x\n" % self.align
        retstr += "\tsegment value: %s\n" % \
                ellipsize_data(self.fullcontents[self.offset:self.offset+self.filesz])
        return retstr

    @staticmethod
    def _ptype(ptype_value, verbose=True):
        """Interpret the value of the p_type field in the Elf64_Phdr."""
        types = {
                0:["PT_NULL","Program header table entry unused"],
                1:["PT_LOAD","Loadable program segment"],
                2:["PT_DYNAMIC","Dynamic linking information"],
                3:["PT_INTERP","Program interpreter"],
                4:["PT_NOTE","Auxiliary information"],
                5:["PT_SHLIB","Reserved"],
                6:["PT_PHDR","Entry for header table itself"],
                7:["PT_TLS","Thread-local storage segment"],
                8:["PT_NUM","Number of defined types"],
                0x60000000:["PT_LOOS","Start of OS-specific"],
                0x6474e550:["PT_GNU_EH_FRAME","GCC .eh_frame_hdr segment"],
                0x6474e551:["PT_GNU_STACK","Indicates stack executability"],
                0x6474e552:["PT_GNU_RELRO","Read-only after relocation"],
                0x6ffffffa:["PT_SUNWBSS","Sun Specific segment"],
                0x6ffffffb:["PT_SUNWSTACK","Stack segment"],
                0x6fffffff:["PT_HIOS","End of OS-specific"],
                0x70000000:["PT_LOPROC","Start of processor-specific"],
                0x7fffffff:["PT_HIPROC","End of processor-specific"],
                }

        if types.get(ptype_value):
            value = types[ptype_value]
            if verbose:
                return "%s (%s)" % (value[0], value[1])
            else:
                return "%s" % value[0]
        else:
            return "UNKNOWN"

class ElfReader():
    """Read the binary data out of an elf file, including all the headers."""

    def __init__(self, elffile):
        self.elffile = elffile
        self.f = open(elffile, 'rb')
        self.contents = self.f.read()

        self.elf_header = ElfHeader(self.contents)

        print(self.elf_header)

        self.program_headers = []

        for program_header_index in range(self.elf_header.phnum):
            start = self.elf_header.phoff + program_header_index * self.elf_header.phentsize
            program_header = ElfProgramHeader(self.contents, start, self.elf_header.phentsize)
            print(program_header)
            self.program_headers.append(program_header)


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("ERROR! You must specify the elf file to look at on the command line.\n")
        sys.exit(1)

    ElfReader(sys.argv[1])

if __name__ == '__main__':
    main()
