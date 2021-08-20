import boto3
import json
import os
import sys
import time
from tabulate import tabulate


SESSION_TYPE = 'LOCAL'
AWS_PROFILE = ''

# Filters
NAME_FILTER = ''
BURST_LIMIT_FILTER = 200
RATE_LIMIT_FILTER = 20

# New Valuess
NEW_BURST_LIMIT = 5
NEW_RATE_LIMIT = 10

# Output file name
OUTPUT_FILE = 'updated_plans'



if SESSION_TYPE == 'LOCAL':
    session = boto3.session.Session(profile_name=AWS_PROFILE)
    api_gateway = session.client('apigateway')
elif SESSION_TYPE == 'DEPLOY':
    api_gateway = boto3.client('apigateway')


def write_to_file(data, filename):
    file_termination = filename.split('.')[-1]
    with open(filename, 'w') as f:
        if file_termination == 'json':
            json.dump(data, f)
        elif file_termination == 'txt':
            f.write(data)
        else:
            print(f'Wrong type of file: .{file_termination}')


def filter_by_name(usage_plan_data, name_filter):
    print(f'Filtering by name, ignoring case. Filter: {NAME_FILTER} ...')
    res = {
        "items": []
    }

    for entry in usage_plan_data["items"]:
        if name_filter in entry["name"].lower():
            res["items"].append(entry)
    
    return res


def filter_by_throttle(usage_plan_data, burst_limit_filter, rate_limit_filter):
    print(f'Filtering by throttle. Burst limit filter: {BURST_LIMIT_FILTER}  Rate limit filter: {RATE_LIMIT_FILTER}')
    res = {
        "items": []
    }

    items_without_throttle = {
        "items": []
    }

    for entry in usage_plan_data["items"]:
        if "throttle" in entry:
            if burst_limit_filter == entry["throttle"]["burstLimit"] and rate_limit_filter == entry["throttle"]["rateLimit"]:
                res["items"].append(entry)
        else:
            items_without_throttle["items"].append(entry)
        
    # write_to_file(items_without_throttle, "usage_plans_without_throttle.json")

    return res


def get_usage_plans():
    print(f'GETTING USAGE PLAN DATA FROM AWS ON ACCOUNT {AWS_PROFILE} ...')
    res = api_gateway.get_usage_plans(limit=500)
    return res


def check_input(input_message):
    while True:
        input_data = input(input_message)
        if input_data in ('yes', 'y'):
            print(f'Continuing ...')
            break
        elif input_data in ('no', 'n'):
            print(f'Exiting ...')
            sys.exit(0)
            break
        else:
            print(f'Wrong input ... use yes or no')


def try_update_plan(usage_plan, new_burst_limit, new_rate_limit):
    try: 
        res = api_gateway.update_usage_plan(
            usagePlanId=usage_plan["id"],
            patchOperations=[
                {
                    'op': 'replace',
                    'path': '/throttle/burstLimit',
                    'value': str(new_burst_limit),
                },
            ]
        )
        res = api_gateway.update_usage_plan(
            usagePlanId=usage_plan["id"],
            patchOperations=[
                {
                    'op': 'replace',
                    'path': '/throttle/rateLimit',
                    'value': str(new_rate_limit),
                },
            ]
        )

    except Exception as e:
        print(f'{e}')
        return None
    
    return res


def update_usage_plans(usage_plans, new_burst_limit, new_rate_limit):
    updated_items = {
        "items": []
    }

    backoff_limit = 7
    apply_for_all = False

    for usage_plan in usage_plans["items"]:
        print(f"Updating plan with plan with name - {usage_plan['name']}  id - {usage_plan['id']}")

        res = try_update_plan(usage_plan, new_burst_limit, new_rate_limit)
        if res == None:
            for i in range(0, backoff_limit):
                print(f"Retrying with a backoff of {2 ** i} seconds")
                time.sleep(2 ** i)
                res = try_update_plan(usage_plan, new_burst_limit, new_rate_limit)
                if res != None:
                    break
                if res == None and i == backoff_limit - 1:
                    print(f'Could not update plan with name - {usage_plan["name"]}  id - {usage_plan["id"]} \n Passing to next one')


        if not apply_for_all:
            print(f"Usage plan with id {usage_plan['id']} updated: \n {res}")
            input_data = input(f'Do you want to apply changes for all usage plans ? (yes/no):')
            if input_data in ('yes', 'y'):
                print(f'Continuing for all usage plans ...')
                apply_for_all = True
                continue
            elif input_data in ('no', 'n'):
                print(f'Finished updating')
                del res["ResponseMetadata"]
                updated_items["items"].append(res)
                return updated_items
            else:
                print(f'Wrong input ... use yes or no')
        
        if res != None:
            del res["ResponseMetadata"]
            updated_items["items"].append(res)

    return updated_items



if __name__ == '__main__':

    data = get_usage_plans()
    filtered_by_name = filter_by_name(data, name_filter=NAME_FILTER)
    filtered_by_throttle = filter_by_throttle(filtered_by_name, burst_limit_filter=BURST_LIMIT_FILTER, rate_limit_filter=RATE_LIMIT_FILTER)

    print(f'\nThe following usage plans are staged for changes: \n')
    table_filtered_data = tabulate([[elem["name"], elem["id"], elem["throttle"]["burstLimit"], elem["throttle"]["rateLimit"]] for elem in filtered_by_throttle["items"]], headers=["Name", "Id", "Burst Limit", "Rate Limit"])
    print(table_filtered_data)

    check_input(f'\nDo you want to start updating usage plan data ? (yes/no):')

    updated_plans = update_usage_plans(filtered_by_throttle, new_burst_limit=NEW_BURST_LIMIT, new_rate_limit=NEW_RATE_LIMIT)

    print(f'\nUpdated usage plan data: \n')
    tabled_updated_data = tabulate([[elem["name"], elem["id"], elem["throttle"]["burstLimit"], elem["throttle"]["rateLimit"]] for elem in updated_plans["items"]], headers=["Name", "Id", "Burst Limit", "Rate Limit"])
    print(tabled_updated_data)
    print('\n')

    print(f'Output data to {OUTPUT_FILE}.txt ...')
    write_to_file(tabled_updated_data, f'{OUTPUT_FILE}.txt')

    print(f'Output data to {OUTPUT_FILE}.json ...')
    write_to_file(updated_plans, f'{OUTPUT_FILE}.json')
