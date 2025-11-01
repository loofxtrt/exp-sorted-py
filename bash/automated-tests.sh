#!/usr/bin/bash

TEST_DIR="./automated"
mkdir -p $TEST_DIR
rm -f $TEST_DIR/*

echo "Testando criação de playlist..."
python3 main.py create "Minha Playlist" -d "Descrição de teste" -y

if [ -f "$TEST_DIR/Minha Playlist.json" ]; then
    echo "Criação OK"
else
    echo "Erro na criação"
fi

VIDEO_URL="https://www.youtube.com/watch?v=dQw4w9WgXcQ"

echo "Testando inserção de vídeo..."
python3 main.py insert "$TEST_DIR/Minha Playlist.json" "$VIDEO_URL"
echo "Teste de inserção concluído"

echo "Testando remoção de vídeo..."
python3 main.py remove "$TEST_DIR/Minha Playlist.json" "$VIDEO_URL"
echo "Teste de remoção concluído"

echo "Testando deleção da playlist..."
python3 main.py delete "$TEST_DIR/Minha Playlist.json"

if [ ! -f "$TEST_DIR/Minha Playlist.json" ]; then
    echo "Deleção OK"
else
    echo "Erro na deleção"
fi
