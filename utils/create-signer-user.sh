#! /bin/sh

set -eu

ENV_ID="${1:?"ENV ID Required"}"

USER_NAME="pdfsigner-${ENV_ID}"
adduser --disabled-password --quiet "$USER_NAME"

HOME_DIR="$(getent passwd "$USER_NAME" | cut -d : -f 6)"

SSH_DIR="$HOME_DIR/.ssh/"
mkdir "$SSH_DIR"
cp "keys/${ENV_ID}_ecdsa.pub" "$SSH_DIR/authorized_keys"

chown -R "$USER_NAME:$USER_NAME" "$SSH_DIR"

echo $USER_NAME
