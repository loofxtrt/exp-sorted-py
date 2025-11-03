#!/usr/bin/bash

set -e  # para parar no primeiro erro

TEST_DIR="./tests"
TEST_PLAYLIST="$TEST_DIR/test_playlist.json"
SECOND_PLAYLIST="$TEST_DIR/second_playlist.json"
YOUTUBE_URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
YOUTUBE_PLAYLIST_URL="https://www.youtube.com/playlist?list=PLExample"

mkdir -p "$TEST_DIR"

echo "=== Testando criação de playlist ==="
python3 main.py create "Test Playlist" "$TEST_DIR" -d "Playlist de teste" -y

echo "=== Testando inserção de vídeo ==="
python3 main.py insert "$TEST_PLAYLIST" "$YOUTUBE_URL"

echo "=== Testando remoção de vídeo ==="
python3 main.py remove "$TEST_PLAYLIST" "$YOUTUBE_URL"

echo "=== Testando importação de playlist ==="
python3 main.py import "$YOUTUBE_PLAYLIST_URL" "$TEST_DIR" -nt "Imported Playlist"

echo "=== Testando visualização de diretório ==="
python3 main.py view-dir "$TEST_DIR"

echo "=== Testando visualização de playlist ==="
python3 main.py view-pl "$TEST_PLAYLIST" -sd

echo "=== Testando mover vídeo entre playlists ==="
python3 main.py create "Second Playlist" "$TEST_DIR" -y
python3 main.py move "$TEST_PLAYLIST" "$SECOND_PLAYLIST" "$YOUTUBE_URL"

echo "=== Testando atualização do cache ==="
python3 main.py update-cache "$TEST_DIR" -ia

echo "=== Testando reset de configurações ==="
python3 main.py reset-settings

echo "=== Testes concluídos ==="
