"""DynamoDB helper for storing investigations and workflows."""

import boto3
from datetime import datetime
from typing import Dict, List, Optional
import os

class InvestigationStore:
    """Store and retrieve investigation workflows in DynamoDB."""
    
    def __init__(self, table_name: str = None):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = table_name or os.getenv('INVESTIGATIONS_TABLE', 'aiops-investigations')
        self.table = self.dynamodb.Table(self.table_name)
    
    def save_workflow(self, investigation_id: str, alarm_summary: Dict, tasks: List[Dict]) -> None:
        """Save investigation workflow to DynamoDB.
        
        Args:
            investigation_id: Unique investigation ID
            alarm_summary: Alarm summary dict
            tasks: List of task dicts
        """
        timestamp = datetime.utcnow().isoformat()
        task_ids = [task['task_id'] for task in tasks]
        
        # Save metadata with execution plan
        self.table.put_item(Item={
            'investigation_id': investigation_id,
            'item_type': 'METADATA',
            'alarm_summary': alarm_summary,
            'execution_plan': {
                'current_task': task_ids[0] if task_ids else None,
                'completed_tasks': [],
                'pending_tasks': task_ids
            },
            'status': 'PENDING',
            'created_at': timestamp,
            'updated_at': timestamp
        })
        
        # Save tasks
        for task in tasks:
            self.table.put_item(Item={
                'investigation_id': investigation_id,
                'item_type': f"TASK#{task['task_id']}",
                'task_id': task['task_id'],
                'agent_type': task['agent_type'],
                'description': task['description'],
                'priority': task['priority'],
                'status': 'PENDING',
                'created_at': timestamp
            })
    
    def get_workflow(self, investigation_id: str) -> Dict:
        """Get investigation workflow from DynamoDB.
        
        Args:
            investigation_id: Investigation ID
            
        Returns:
            Dict with investigation_id, metadata, status, and tasks
        """
        response = self.table.query(
            KeyConditionExpression='investigation_id = :id',
            ExpressionAttributeValues={':id': investigation_id}
        )
        
        items = response.get('Items', [])
        metadata = next((i for i in items if i['item_type'] == 'METADATA'), {})
        tasks = [i for i in items if i['item_type'].startswith('TASK#')]
        
        return {
            'investigation_id': investigation_id,
            'alarm_summary': metadata.get('alarm_summary', {}),
            'status': metadata.get('status', 'UNKNOWN'),
            'tasks': tasks
        }
    
    def get_next_task(self, investigation_id: str) -> Optional[Dict]:
        """Get the next task to execute.
        
        Args:
            investigation_id: Investigation ID
            
        Returns:
            Task dict or None if no pending tasks
        """
        # Get metadata
        response = self.table.get_item(
            Key={
                'investigation_id': investigation_id,
                'item_type': 'METADATA'
            }
        )
        
        metadata = response.get('Item', {})
        execution_plan = metadata.get('execution_plan', {})
        current_task_id = execution_plan.get('current_task')
        
        if not current_task_id:
            return None
        
        # Get current task
        task_response = self.table.get_item(
            Key={
                'investigation_id': investigation_id,
                'item_type': f"TASK#{current_task_id}"
            }
        )
        
        return task_response.get('Item')
    
    def complete_task(self, investigation_id: str, task_id: str, result: Dict) -> None:
        """Mark task as completed and move to next task.
        
        Args:
            investigation_id: Investigation ID
            task_id: Task ID
            result: Task result dict
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Get current metadata
        response = self.table.get_item(
            Key={
                'investigation_id': investigation_id,
                'item_type': 'METADATA'
            }
        )
        
        metadata = response.get('Item', {})
        execution_plan = metadata.get('execution_plan', {})
        
        # Update execution plan
        completed = execution_plan.get('completed_tasks', [])
        pending = execution_plan.get('pending_tasks', [])
        
        completed.append(task_id)
        if task_id in pending:
            pending.remove(task_id)
        
        next_task = pending[0] if pending else None
        
        # Update metadata
        self.table.update_item(
            Key={
                'investigation_id': investigation_id,
                'item_type': 'METADATA'
            },
            UpdateExpression='SET execution_plan = :plan, updated_at = :timestamp',
            ExpressionAttributeValues={
                ':plan': {
                    'current_task': next_task,
                    'completed_tasks': completed,
                    'pending_tasks': pending
                },
                ':timestamp': timestamp
            }
        )
        
        # Update task status
        self.table.update_item(
            Key={
                'investigation_id': investigation_id,
                'item_type': f"TASK#{task_id}"
            },
            UpdateExpression='SET #status = :status, updated_at = :timestamp',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'COMPLETED',
                ':timestamp': timestamp
            }
        )
        
        # Save result
        self.table.put_item(Item={
            'investigation_id': investigation_id,
            'item_type': f"RESULT#{task_id}",
            'task_id': task_id,
            'result': result,
            'created_at': timestamp
        })
    
    def delete_investigation(self, investigation_id: str) -> None:
        """Delete all items for an investigation.
        
        Args:
            investigation_id: Investigation ID
        """
        # Query all items for this investigation
        response = self.table.query(
            KeyConditionExpression='investigation_id = :id',
            ExpressionAttributeValues={':id': investigation_id}
        )
        
        # Delete all items
        with self.table.batch_writer() as batch:
            for item in response.get('Items', []):
                batch.delete_item(
                    Key={
                        'investigation_id': item['investigation_id'],
                        'item_type': item['item_type']
                    }
                )
