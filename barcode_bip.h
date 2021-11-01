#ifndef BARCODE_BIP_H
#define BARCODE_BIP_H

#include "libbip.h"

struct context
{
    void *ret_f;
    Elf_proc_ *proc;

    short currentScreen;
};

void init_app(void *return_screen);
void keypress_handler();
int touch_handler(void *param);
void update_screen();
void draw_screen();

void initial_values();
void show_screen();

#endif // BARCODE_BIP_H