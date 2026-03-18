ENTRY(_start)

PHDRS
{
    app PT_LOAD FLAGS(7);
}

SECTIONS
{
    . = 0x400000;

    .text : ALIGN(16) {
        *(.text .text.*)
        *(.rodata .rodata.*)
        *(.data .data.*)
    } :app

    .bss : ALIGN(16) {
        *(.bss .bss.*)
        *(COMMON)
    } :app

    /DISCARD/ : {
        *(.comment)
        *(.note*)
        *(.eh_frame*)
    }
}
