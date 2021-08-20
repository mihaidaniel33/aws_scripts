# Script for filtering AWS API Gateway Usage Plans by name, burst, rate limits and replacing the burst, rate values
Python 3.7 needed for this - should be no problem 
Run:
```
cd ./api_usage_plan_update
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

The aws session, filter, replace parameters can be found at the top level of the script. AWS Profile should be one of the profiles configured in ~/.aws/config

Run the script:
```
python api_usage_plan_update.py
```
