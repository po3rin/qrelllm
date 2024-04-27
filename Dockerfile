FROM docker.elastic.co/elasticsearch/elasticsearch:8.11.3

# Add your elasticsearch plugins setup here
# Example: RUN elasticsearch-plugin install analysis-icu
RUN curl -L -k -O https://artifacts.elastic.co/downloads/elasticsearch-plugins/analysis-kuromoji/analysis-kuromoji-8.11.3.zip
RUN curl -L -k -O https://artifacts.elastic.co/downloads/elasticsearch-plugins/analysis-icu/analysis-icu-8.11.3.zip 

RUN cp analysis-* /tmp

RUN /usr/share/elasticsearch/bin/elasticsearch-plugin install file:///tmp/analysis-kuromoji-8.11.3.zip
RUN /usr/share/elasticsearch/bin/elasticsearch-plugin install file:///tmp/analysis-icu-8.11.3.zip