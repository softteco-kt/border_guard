if ( ! -d "./data" ); 
then
    echo "Creating data folder..."
    mkdir data
fi

echo "Downloading ChromeDriver..."


if [[ "$OSTYPE" =~ ^msys ]] ; then
    curl -LO https://chromedriver.storage.googleapis.com/108.0.5359.71/chromedriver_win32.zip
fi

if [[ "$OSTYPE" =~ ^linux ]]; then
    wget https://chromedriver.storage.googleapis.com/108.0.5359.71/chromedriver_linux64.zip
fi

unzip *.zip -d .
rm -i *.zip