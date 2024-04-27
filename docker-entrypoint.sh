#!/bin/bash

set -ex

cd /usr/share/elasticsearch

test -d /usr/share/elasticsearch/plugins/analysis-kuromoji || bin/elasticsearch-plugin install analysis-kuromoji
test -d /usr/share/elasticsearch/plugins/analysis-icu || bin/elasticsearch-plugin install analysis-icu

# execute docker.elastic.co/elasticsearch/elasticsearch image original entrypoint
docker-entrypoint.sh
