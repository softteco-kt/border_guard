if [[ ! poetry ]]
then
    curl -sSL https://install.python-poetry.org | python3 -
fi

if [ ! -d "./data" ] 
then
    echo "Creating data folder..."
    mkdir data
fi

echo "Downloading ChromeDriver..."

if [[ "$OSTYPE" =~ ^msys ]]; then
    .\\venv\\scripts\\activate
    curl -LO https://chromedriver.storage.googleapis.com/108.0.5359.71/chromedriver_win32.zip

fi

if [[ "$OSTYPE" =~ ^linux ]]; then
    source ./venv/scripts/activate
    wget https://chromedriver.storage.googleapis.com/108.0.5359.71/chromedriver_linux64.zip
    export .env
fi

unzip *.zip -d .
rm -i *.zip