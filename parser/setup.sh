if ( ! -d "./data" ); 
then
    echo "Creating data folder..."
    mkdir data
fi

# Chrome versions are available at https://www.ubuntuupdates.org/package/google_chrome/stable/main/base/google-chrome-stable?id=202706&page=1
# Chromedriver versions are available at https://chromedriver.chromium.org/downloads

export CHROMEDRIVER_VERSION=108.0.5359.71
export CHROME_VERSION=$CHROMEDRIVER_VERSION-1

echo "Downloading ChromeDriver..."

if [[ "$OSTYPE" =~ ^msys ]] ; then
    curl -LO https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_win32.zip
fi

if [[ "$OSTYPE" =~ ^linux ]]; then
    wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
fi

unzip *.zip -d . && rm *.zip

python3 -m venv .venv && \
    source .venv/bin/activate && \
    pip3 install --no-cache-dir -r requirements.txt