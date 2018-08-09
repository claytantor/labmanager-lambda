# labmanager-lambda
The lab manager cron job that tears down lab POCs.

## install
```
virtualenv venv
source venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
pip install -r requirements.txt
```

## deploy the serverless package
`serverless deploy -v`

## deploy the function
`serverless deploy function -f cron`
