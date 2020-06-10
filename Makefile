S3_UPLOAD_PATH=data/external
S3_DOWNLOAD_PATH=data/raw_data
MODEL_DATA=data/model_data
MODEL_ARTIFACTS=models

s3_upload: config/model_config.yaml
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source="`pwd`",target=/app/ got_make run.py upload -c=config/model_config.yaml -i=${S3_UPLOAD_PATH}

s3_download: config/model_config.yaml
	docker run -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY --mount type=bind,source="`pwd`",target=/app/ got_make run.py download -c=config/model_config.yaml --lfp=${S3_DOWNLOAD_PATH}

clean_base: config/model_config.yaml
	docker run --mount type=bind,source="`pwd`",target=/app/ got_make run.py clean -i=${S3_DOWNLOAD_PATH}/character-deaths.csv --config=config/model_config.yaml --output=${MODEL_DATA}/clean_base.csv

features: config/model_config.yaml
	docker run --mount type=bind,source="`pwd`",target=/app/ got_make run.py featurize -i=${MODEL_DATA}/clean_base.csv -i_p=${S3_DOWNLOAD_PATH}/character-profile.csv --lfp=${MODEL_DATA} -c=config/model_config.yaml -o=${MODEL_DATA}/features.csv

model: config/model_config.yaml
	docker run --mount type=bind,source="`pwd`",target=/app/ got_make run.py model -i=${MODEL_DATA}/features.csv -c=config/model_config.yaml --lfp=${MODEL_ARTIFACTS}

score: config/model_config.yaml
	docker run --mount type=bind,source="`pwd`",target=/app/ got_make run.py score -c=config/model_config.yaml -o=${MODEL_DATA}/offline_score.csv --lfp=${MODEL_ARTIFACTS}

database:
	docker run -e SQLALCHEMY_DATABASE_URI --mount type=bind,source="`pwd`",target=/app/ got_make run.py create_db -i=${MODEL_ARTIFACTS}/offline_score.csv -c=config/model_config.yaml -t

tests:
	python3 -m pytest test/*

clean:
	rm -rf data/model_artifacts/*
	rm -rf data/model_data/*
	rm -rf data/raw_data/*

pipeline: s3_download clean_base features model score

.PHONY: pipeline