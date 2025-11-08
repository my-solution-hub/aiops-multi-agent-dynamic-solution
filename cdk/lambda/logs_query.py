import json
import boto3
import time

logs = boto3.client('logs')

def lambda_handler(event, context):
    """Query CloudWatch Logs."""
    print("Received event:", event)
    # params = event.get('params', {})
    # print(f"Received params: {params}")
    log_group = event.get('log_group_name')
    query_string = event.get('query_string', 'fields @timestamp, @message | limit 20')
    start_time = int(event.get('start_time'))
    end_time = int(event.get('end_time'))
    
    if not log_group or not start_time or not end_time:
        return {
            'content': [{
                'type': 'text',
                'text': json.dumps({'error': 'log_group_name, start_time, and end_time are required'})
            }]
        }
    
    # Start query
    response = logs.start_query(
        logGroupName=log_group,
        startTime=start_time,
        endTime=end_time,
        queryString=query_string
    )
    
    query_id = response['queryId']
    
    # Wait for query to complete
    max_wait = 60
    waited = 0
    while waited < max_wait:
        result = logs.get_query_results(queryId=query_id)
        status = result['status']
        
        if status == 'Complete':
            print(result)
            return {
                'content': [{
                    'type': 'text',
                    'text': json.dumps({
                        'status': 'success',
                        'log_group': log_group,
                        'results': result['results'][:50]
                    }, indent=2)
                }]
            }
        elif status == 'Failed':
            return {
                'content': [{
                    'type': 'text',
                    'text': json.dumps({'error': 'Query failed'})
                }]
            }
        
        time.sleep(1)
        waited += 1
    
    return {
        'content': [{
            'type': 'text',
            'text': json.dumps({'error': 'Query timeout'})
        }]
    }
