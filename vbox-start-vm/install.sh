#!/usr/bin/env bash

mkdir -p "$HOME/filesystem/vbox-start-vm/bin"
mkdir -p "$HOME/filesystem/vbox-start-vm/etc/bash_completion.d"

ln -sf "$(pwd)/vbox-start-vm" "$HOME/filesystem/vbox-start-vm/bin/"
ln -sf "$(pwd)/bash_completion.d/vbox-start-vm" "$HOME/filesystem/vbox-start-vm/etc/bash_completion.d/"
