# model-deploymen-example
Example of heavy model deployment with celery and FastAPI, model kakaobrain/align-base is used. 

## Usage

Set up docker containers
```
docker-compose up --build --scale worker=2
```

Set up the local env 
```shell
uv venv --python=3.12 
source .venv/bin/activate
uv pip install -r requirements_local.txt s
```

Test the deployed model
```shell
python3.12 test.py --image data/cat2.jpg --categories 'dog', 'cat'
ls data | xargs -P4 -I{} python3.12 test.py --image data/{} --categories 'dog', 'cat'
```