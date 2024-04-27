setup:
	curl -XPOST 'localhost:9200/_license/start_trial?acknowledge=true'
	poetry run eland_import_hub_model \
		--url "http://localhost:9200" \
		--hub-model-id cl-tohoku/bert-base-japanese-v2 \
		--task-type text_embedding \
		--start
	curl -XPUT 'localhost:9200/_ingest/pipeline/japanese-text-embeddings' -H 'Content-Type: application/json' -d @./pipeline.json
	eskeeper < eskeeper.yml
delete:
	 curl -X POST localhost:9200/docs/_delete_by_query -H 'Content-Type: application/json' -d '{"query":{"match_all":{}}}'
