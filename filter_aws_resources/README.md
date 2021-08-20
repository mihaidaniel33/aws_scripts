# Basic aws resource filter  
Python 3.7 needed for this - should be no problem 
Run:
```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Currently added features: 
    - AWS resources: S3, ELB, EC2, ASG
    - Filter: by resource name (tag with value: "name", in case of EC2 instances)


At the top level of the script there are some capitalized parameters which configures how the script is ran. 
In the PROFILES list we should have the names of our AWS Profiles, usually found in ~/.aws/config
The FILTER parameter cand be filled with specific names to look for or with Regex expressions.

Run the script:
```
python filter.py
```
