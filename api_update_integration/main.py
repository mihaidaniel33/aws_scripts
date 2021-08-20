import boto3


session = boto3.session.Session(profile_name="", region_name="")
client = session.client('apigateway')

api_ids = {

}
methods_to_update = ['GET', 'POST', 'PUT', 'DELETE', 'UPDATE']
value_to_update = '120000'


def update_integration():

    for api, id in api_ids.items():
        print(f'Starting for {api}')

        resources = client.get_resources(
            restApiId=id,
            limit=500,
        )

        for resource in resources['items']:
            if 'resourceMethods' not in resource.keys():
                continue
            for method in resource['resourceMethods'].keys():
                if method in methods_to_update:
                    try:
                        response = client.update_integration(
                            restApiId=id,
                            resourceId=resource['id'],
                            httpMethod=method,
                            patchOperations=[
                                {
                                    'op': 'replace',
                                    'path': '/timeoutInMillis',
                                    'value': value_to_update
                                },
                            ]
                        )
                        print(f"Completed for id: {resource['id']}")
                    except Exception as e:
                        print(e)
                        print(f"Could not complete for id: {resource['id']}")
                        continue
                else:
                    continue

    


if __name__ == '__main__':
    update_integration()