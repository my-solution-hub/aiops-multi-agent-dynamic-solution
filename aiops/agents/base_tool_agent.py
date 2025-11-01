"""Base class for tooling agents"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from ..orchestrator.base import BaseStrandsAgent, SystemState
from ..models.enums import AgentType


class BaseToolAgent(BaseStrandsAgent):
    """Base class for tooling agents that provide specific capabilities"""
    
    def __init__(self, agent_id: str, system_state: SystemState):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.TOOL,  # We'll need to add this to enums
            system_state=system_state
        )
    
    @abstractmethod
    def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task and return results"""
        pass
    
    @abstractmethod
    def get_available_operations(self) -> List[str]:
        """Get list of available operations this agent can perform"""
        pass
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this tooling agent"""
        return f"""You are a {self.agent_id} specialized in {self.get_specialty()}.

Your primary responsibilities:
{self._get_responsibilities()}

Available operations:
{chr(10).join(f"- {op}" for op in self.get_available_operations())}

**Key Principles:**
- Focus on data collection and analysis within your specialty
- Provide structured, actionable results
- Include confidence levels and data quality indicators
- Flag any limitations or missing data
- Return results in JSON format when possible

**Response Format:**
- Always provide clear, structured responses
- Include metadata about data sources and collection methods
- Specify any assumptions or limitations
- Provide recommendations for next steps if applicable

Be precise, thorough, and focus on delivering high-quality data and analysis."""

    @abstractmethod
    def get_specialty(self) -> str:
        """Get the specialty area of this agent"""
        pass
    
    @abstractmethod
    def _get_responsibilities(self) -> str:
        """Get formatted list of responsibilities"""
        pass