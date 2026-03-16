#!/bin/bash
set -e

pip install -r requirements.txt

mkdir -p fonts

echo "Downloading Lora fonts..."
curl -sL "https://github.com/cyrealtype/Lora-Cyrillic/raw/main/fonts/ttf/Lora-Regular.ttf" -o fonts/Lora-Regular.ttf
curl -sL "https://github.com/cyrealtype/Lora-Cyrillic/raw/main/fonts/ttf/Lora-Italic.ttf" -o fonts/Lora-Italic.ttf

echo "Downloading Poppins fonts..."
curl -sL "https://github.com/itfoundry/Poppins/raw/master/products/Poppins-Light.ttf" -o fonts/Poppins-Light.ttf
curl -sL "https://github.com/itfoundry/Poppins/raw/master/products/Poppins-Regular.ttf" -o fonts/Poppins-Regular.ttf
curl -sL "https://github.com/itfoundry/Poppins/raw/master/products/Poppins-Medium.ttf" -o fonts/Poppins-Medium.ttf
curl -sL "https://github.com/itfoundry/Poppins/raw/master/products/Poppins-Bold.ttf" -o fonts/Poppins-Bold.ttf

echo "Fonts downloaded successfully!"
ls -la fonts/
