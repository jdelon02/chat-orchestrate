import json
import csv
from pathlib import Path
from typing import Union

class ProcessorClass:
    def __init__(self):
        self.assets_dir = Path(__file__).parent.parent.parent / 'assets'
        self.assets_dir.mkdir(exist_ok=True)
        self.tools_file = self.assets_dir / 'available.tools'
        self._progress_token = 0

    async def process_tools(self, tools_data: Union[str, dict, list], client=None) -> None:
        """Process tools data from FastMCP and save tool names to CSV"""
        try:
            if isinstance(tools_data, str):
                data = json.loads(tools_data)
            else:
                data = tools_data

            if not data:
                data = []
            elif isinstance(data, dict) and "content" in data:
                data = data["content"]
            
            total_items = len(data) if isinstance(data, list) else 1
            processed = 0

            with open(self.tools_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Tool Name'])
                
                if isinstance(data, list):
                    for tool in data:
                        name = ""
                        if isinstance(tool, dict):
                            name = tool.get("name", "")
                        elif isinstance(tool, str):
                            name = tool
                        writer.writerow([name])
                        processed += 1
                        if client:
                            await client.progress(self._progress_token, processed, total_items)
                else:
                    if isinstance(data, dict):
                        writer.writerow([data.get("name", "")])
                    else:
                        writer.writerow([str(data)])
                    if client:
                        await client.progress(self._progress_token, 1, 1)

            if client:
                await client.progress(self._progress_token, total_items, total_items)
            self._progress_token += 1

        except Exception as e:
            print(f"Error processing tools data: {str(e)}")
            raise