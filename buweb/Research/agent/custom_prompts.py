import datetime
import importlib.resources
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Type

from langchain_core.messages import HumanMessage, SystemMessage

if TYPE_CHECKING:
    from browser_use.agent.views import ActionResult, AgentStepInfo
    from browser_use.browser.views import BrowserState

from browser_use.agent.prompts import SystemPrompt, AgentMessagePrompt
from buweb.Research.agent.custom_views import CustomBrowserState, CustomAgentStepInfo, CustomAgentOutput, create_browser_state_format, create_browser_state_values, create_current_state_format

class CustomSystemPrompt(SystemPrompt):
    def __init__(self, action_description: str, max_actions_per_step: int = 10):
        super().__init__(action_description, max_actions_per_step)

    def _load_prompt_template(self) -> None:
        """Load the prompt template from the markdown file."""
        try:
            # This works both in development and when installed as a package
            with importlib.resources.files('buweb.Research.agent').joinpath('system_prompt.md').open('r') as f:
                self.prompt_template = f.read()
        except Exception as e:
            raise RuntimeError(f'Failed to load system prompt template: {e}')

    def get_system_message(self) -> SystemMessage:
        """
        Get the system prompt for the agent.

        Returns:
            SystemMessage: Formatted system prompt
        """
        current_state_fmt = create_current_state_format(CustomAgentOutput)
        input_fmt = '\n'.join( create_browser_state_format((CustomAgentStepInfo,CustomBrowserState) ) )
        prompt = self.prompt_template.format(
            max_actions=self.max_actions_per_step,
            input_format=input_fmt,
            current_state_format=current_state_fmt)
        return SystemMessage(content=prompt)


# Functions:
# {self.default_action_description}

# Example:
# {self.example_response()}
# Your AVAILABLE ACTIONS:
# {self.default_action_description}


class CustomAgentMessagePrompt:
    def __init__(
        self,
        state: 'BrowserState',
        result: Optional[List['ActionResult']] = None,
        include_attributes: list[str] = [],
        step_info: Optional['CustomAgentStepInfo'] = None,
    ):
        self.state = state
        self.result = result
        self.include_attributes = include_attributes
        self.step_info = step_info

    def get_user_message(self, use_vision: bool = True) -> HumanMessage:
        elements_text = self.state.element_tree.clickable_elements_to_string(include_attributes=self.include_attributes)

        has_content_above = (self.state.pixels_above or 0) > 0
        has_content_below = (self.state.pixels_below or 0) > 0

        if elements_text != '':
            if has_content_above:
                elements_text = (
                    f'... {self.state.pixels_above} pixels above - scroll or extract content to see more ...\n{elements_text}'
                )
            else:
                elements_text = f'[Start of page]\n{elements_text}'
            if has_content_below:
                elements_text = (
                    f'{elements_text}\n... {self.state.pixels_below} pixels below - scroll or extract content to see more ...'
                )
            else:
                elements_text = f'{elements_text}\n[End of page]'
        else:
            elements_text = 'empty page'

        #if self.step_info:
        #	step_info_description = f'Current step: {self.step_info.step_number + 1}/{self.step_info.max_steps}'
        #else:
        #	step_info_description = ''
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        step_info_description = f'Current date and time: {time_str}'

        values = {
            'element_tree': f"from top layer of the current page inside the viewport:{elements_text}",
        }
        input_value = '\n'.join( create_browser_state_values( ( (CustomAgentStepInfo,self.step_info), (CustomBrowserState,self.state)), values ) )

        state_description = f"""
[Task history memory ends]
[Current state starts here]
The following is one-time information - if you need to remember it write it to memory:
{input_value}
{step_info_description}
"""
        # print(f"{state_description}")
        if self.result:
            for i, result in enumerate(self.result):
                if result.extracted_content:
                    state_description += f'\nResult of action {i + 1}/{len(self.result)}: {result.extracted_content}'
                if result.error:
                    # only use last line of error
                    error = result.error.split('\n')[-1]
                    state_description += f'\nError of action {i + 1}/{len(self.result)}: ...{error}'

        if self.state.screenshot and use_vision == True:
            # Format message for vision model
            return HumanMessage(
                content=[
                    {'type': 'text', 'text': state_description},
                    {
                        'type': 'image_url',
                        'image_url': {'url': f'data:image/png;base64,{self.state.screenshot}'},  # , 'detail': 'low'
                    },
                ]
            )

        return HumanMessage(content=state_description)


class PlannerPrompt(SystemPrompt):
    def get_system_message(self) -> SystemMessage:
        return SystemMessage(
            content="""You are a planning agent that helps break down tasks into smaller steps and reason about the current state.
Your role is to:
1. Analyze the current state and history
2. Evaluate progress towards the ultimate goal
3. Identify potential challenges or roadblocks
4. Suggest the next high-level steps to take

Inside your messages, there will be AI messages from different agents with different formats.

Your output format should be always a JSON object with the following fields:
{
    "state_analysis": "Brief analysis of the current state and what has been done so far",
    "progress_evaluation": "Evaluation of progress towards the ultimate goal (as percentage and description)",
    "challenges": "List any potential challenges or roadblocks",
    "next_steps": "List 2-3 concrete next steps to take",
    "reasoning": "Explain your reasoning for the suggested next steps"
}

Ignore the other AI messages output structures.

Keep your responses concise and focused on actionable insights."""
        )
