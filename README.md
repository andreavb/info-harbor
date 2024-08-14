# info-harbor
Some tooling to find chess players and their games.

### Update and upgrade system
$ sudo yum update

### Install dependencies
$ sudo yum install python3-pip libX11

$ pip3 install python-chess beautifulsoup4 selenium

### Install chromedriver
## Find most recent here: https://googlechromelabs.github.io/chrome-for-testing/
$ wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chrome-linux64.zip

$ unzip chromedriver-linux64.zip

$ sudo mv chromedriver-linux64/chromedriver /usr/bin/chromedriver

$ chromedriver --version

### Install google-chrome
$ curl https://intoli.com/install-google-chrome.sh | bash

$ sudo mv /usr/bin/google-chrome-stable /usr/bin/google-chrome

$ google-chrome --version && which google-chrome


### Docker
@TODO
