wget https://offshoreleaks-data.icij.org/offshoreleaks/csv/csv_paradise_papers.2018-02-14.zip
sudo apt-get install unzip
unzip csv_paradise_papers.2018-02-14.zip -d backend/dataset/ && rm -f csv_paradise_papers.2018-02-14.zip
