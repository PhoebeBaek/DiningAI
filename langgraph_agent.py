import config
import asyncio
import base64
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from IPython.display import Image, display



async def dining_ai(image_path):
    try:
        mcp_client = MultiServerMCPClient(
            {
                "MongoDB": {
                    "transport": "stdio",
                    "command": "npx",
                    "args": [
                        "-y",
                        "mongodb-mcp-server",
                        "--connectionString",
                        config.URI
                    ]
                },
                "Input_image": {
                    "transport": "stdio",
                    "command": "/Users/sojeong/study/pseudo/.env/bin/python", 
                    "args": ["mcp_server.py"]
                }
            }
        )

        tools = await mcp_client.get_tools()

        analysis_node = create_react_agent(
                model = "bedrock_converse:anthropic.claude-3-5-sonnet-20240620-v1:0",
                tools = tools,
                prompt= """
                        You are a menu analyer. 
                        Your task is analyzing the ingredients required to cook the given menu image and only return a response in the rules below.
                        
                        <Rules>
                        1. Return the menu name and ingredients analysis result in the format below.
                        Ingredients: ['소고기', '감자', '당근']
                        2. Ingredients should be only in Korean.
                        3. Do not include other description or translation explanation except for menu descriptiona and ingredients in your response.
                        </Rules>
                        """
            )
            
        query_node = create_react_agent(
                model = "bedrock_converse:anthropic.claude-3-5-sonnet-20240620-v1:0",
                tools = tools,
                prompt= """
                        Your task is querying data against MongoDB using provided `MongoDB` tool and return ingredients data following the rules below. 
                        Proceed with your task when you receive ingredients list from analysis_node.
                        
                        <Rules>
                        1. Run query against the namespace `dining_ai.items`.
                        2. Create and run MongoDB aggregation $search query for each ingredient.
                        3. Return one document for each ingredient with title, link, price fields.
                        4. Do not include words like "Ok", "Certainly!" etc. in your response.
                        </Rules>

                        <Examples>
                        Input: "Ingredients: ['소고기', '감자', '당근']"
                        Search query: db.items.aggregate([{'$search':{'text':{'query':'소고기','path':'title'}}},{'$limit':3}])
                        Return: [{
                                    _id: ObjectId('67f514edb85ced008b67d2bc'),
                                    title: '미국산 채끝 100G/소고기',
                                    link: 'https://shopping.naver.com/outlink/itemdetail/4996105973',
                                    image: 'https://shopping-phinf.pstatic.net/main_8254062/82540626640.jpg',
                                    lprice: '23700',
                                    hprice: '',
                                    mallName: 'Homeplus',
                                    productId: '82540626640',
                                    productType: '2',
                                    brand: '',
                                    maker: '',
                                    category1: '식품',
                                    category2: '축산물',
                                    category3: '쇠고기',
                                    category4: '수입산쇠고기'
                                }]
                        </Examples>
                        """
            )

        workflow = StateGraph(MessagesState)
        workflow.add_node("analysis", analysis_node)
        workflow.add_node("query", query_node)
        workflow.add_edge(START, "analysis")
        workflow.add_edge("analysis", "query")
        workflow.add_edge("query", END)
        graph = workflow.compile()

        input = {"messages": 
                            [{
                                "role": "user",
                                "content": f"Analyze this menu image at {image_path} and provide the ingredient items required to cook the menu.",
                                "stream_mode": "messages"
                            }]}

        # Stream chunks as they are generated
        async for chunk in graph.astream(input):
            yield chunk

    except Exception as e:
        print(f"Error in dining_ai: {str(e)}")
        raise

# image_path = "/Users/sojeong/study/pseudo/galbi.jpeg"
# asyncio.run(dining_ai(image_path))