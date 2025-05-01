import json
import csv
from pathlib import Path
from typing import Union

class ProcessorClass:
    def __init__(self):
        self.assets_dir = Path(__file__).parent.parent.parent / 'assets'
        self.assets_dir.mkdir(exist_ok=True)
        self.tools_file = self.assets_dir / 'available.tools'

    async def process_tools(self, tools_data: Union[str, dict, list]) -> None:
        """Process tools data from FastMCP and save tool names to CSV"""
        try:
            # Parse JSON string if needed
            if isinstance(tools_data, str):
                data = json.loads(tools_data)
            else:
                data = tools_data

            # Write to CSV
            with open(self.tools_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Tool Name'])
                
                # Handle both list and dictionary formats
                if isinstance(data, list):
                    for tool in data:
                        # Handle Tool objects directly
                        try:
                            writer.writerow([getattr(tool, 'name', '')])
                        except AttributeError:
                            # Fallback to dictionary access if it's a dict
                            writer.writerow([tool.get('name', '')])
                else:
                    # Handle dictionary format
                    for tool_name, _ in data.items():
                        writer.writerow([tool_name])

        except Exception as e:
            print(f"Error processing tools data: {str(e)}")
            raise