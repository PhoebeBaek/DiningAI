import os
from mcp.server.fastmcp import FastMCP
import config
import asyncio
import io
import re
import base64
import vertexai
from vertexai.vision_models import Image, MultiModalEmbeddingModel
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage
from pymongo import MongoClient

# Initialize the MCP server
mcp = FastMCP("mcp_server")

@mcp.tool()
def input_image(image_path):
    """
    Receiving multimodal menu image and analyze the menu.
    
    Args:
        image_path: Path to the image file containing a menu.
        
    Returns:
        Ingredients analysis about the menu.
    """
    # Open the uploaded image
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    # Initialize the model client
    llm = ChatBedrock(
        region="us-east-1",
        # provider = "anthropic",
        # model_id = "anthropic.claude-3-sonnet-20240229-v1:0",
        model_id = "amazon.nova-pro-v1:0",
        model_kwargs = {"temperature": 1}
    )

    #Define a message
    message = HumanMessage(
        content=[
            {"type": "text", 
            "text": """
                    You are a menu analyzer. Your are responsible for the tasks based on the rules below.
                    <Tasks>
                    1. Analyze menu images
                    2. Analyze what ingredients are required to cook the menu in Korean.
                    </Tasks>

                    <Rules>
                    1. Return the analysis result in the format below.
                    {Ingredients: ['소고기', '감자', '당근']}
                    2. Each element in array should be a string
                    3. Do not include any other text or formatting
                    </Rules>
                    """
            },
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64_image
                }
            }
        ]
    )
    # Invoke LLM
    response = llm.invoke([message]).content
    return response



# @mcp.tool()
# def mongodb_query(input_items):
#     """
#     Implement text to sql and run query in MongoDB.
#     Args:
#         input_items: String representation of a list of items from `menu_analysis_assistant`.
        
#     Returns:
#         Query output return by MongoDB.
#     """

#     try:
#         # Parse the input_items string to get the actual list
#         if input_items.startswith("{Ingredients:"):
#             input_items = input_items[11:-1]  # Remove {Ingredients: and ]
#         items_list = ast.literal_eval(f"[{input_items}]")
        
#         # Get the first item from the list
#         query_item = items_list[0] if items_list else None
        
#         if not query_item:
#             return []
            
#         # Construct the MongoDB query
#         query = [
#             {"$search": {"text": {"query": query_item, "path": "title"}}},
#             {"$limit": 3}
#         ]
        
#         # Connect to MongoDB
#         client = MongoClient(config.URI)
#         db = client["dining_ai"]
#         collection = db["items"]
        
#         # Execute the query
#         response = collection.aggregate(query)
#         item_list = list(response)
        
#         return item_list
        
#     except Exception as e:
#         print(f"Error in mongodb_query: {str(e)}")
#         return []


@mcp.tool()
def embed_image(image_path):
    # image_path = "/Users/sojeong/study/pseudo/image.jpeg"
    embedding_dimension = 512
    model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
    image = Image.load_from_file(
        image_path
    )

    embeddings = model.get_embeddings(
        image=image,
        dimension=embedding_dimension,
    )
    return embeddings.image_embedding

if __name__ == "__main__":
    mcp.run(transport='stdio')