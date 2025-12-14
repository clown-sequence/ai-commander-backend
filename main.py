from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from typing import Optional

# Optional: Uncomment if using OpenAI
# from openai import AsyncOpenAI
# client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="AI Commander Backend")

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CommandParser:
    """Parse natural language commands into structured strategies"""
    
    def parse_command(self, command: str) -> dict:
        """
        Parse command into strategy object
        This is a simple rule-based parser. Replace with LLM for better results.
        """
        command_lower = command.lower()
        
        # Determine formation
        formation = "wedge"  # default
        if "spread" in command_lower or "scatter" in command_lower:
            formation = "spread"
        elif "line" in command_lower or "row" in command_lower:
            formation = "line"
        elif "circle" in command_lower or "surround" in command_lower:
            formation = "circle"
        
        # Determine target
        target = "patrol"  # default
        if "attack" in command_lower or "enemy" in command_lower or "offensive" in command_lower:
            target = "enemies"
        elif "defend" in command_lower or "protect" in command_lower or "base" in command_lower:
            target = "base"
        elif "resource" in command_lower or "collect" in command_lower:
            target = "resources"
        
        # Determine aggression level
        aggression = 0.5  # default
        if "aggressive" in command_lower or "hard" in command_lower or "full force" in command_lower:
            aggression = 0.9
        elif "careful" in command_lower or "cautious" in command_lower:
            aggression = 0.3
        elif "defend" in command_lower:
            aggression = 0.2
        elif "attack" in command_lower:
            aggression = 0.7
        
        return {
            "formation": formation,
            "target": target,
            "aggression": aggression
        }
    
    async def parse_with_llm(self, command: str) -> dict:
        """
        Use OpenAI to parse command (optional - requires API key)
        Uncomment and configure if you want to use real LLM
        """
        # system_prompt = '''You are a tactical AI commander. 
        # Translate natural language commands into structured strategies.
        
        # Respond ONLY with JSON in this exact format:
        # {
        #     "formation": "spread|line|wedge|circle",
        #     "target": "enemies|base|resources|patrol",
        #     "aggression": 0.0-1.0
        # }
        # '''
        
        # response = await client.chat.completions.create(
        #     model="gpt-4",
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": command}
        #     ],
        #     temperature=0.7
        # )
        
        # strategy = json.loads(response.choices[0].message.content)
        # return strategy
        
        # Fallback to rule-based if LLM not configured
        return self.parse_command(command)

parser = CommandParser()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "AI Commander Backend",
        "version": "1.0.0"
    }

@app.websocket("/ws/commander")
async def commander_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for receiving commands and sending strategies
    """
    await websocket.accept()
    print("✅ Client connected to AI Commander")
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to AI Commander Backend"
        })
        
        while True:
            # Receive command from frontend
            data = await websocket.receive_text()
            print(f"📩 Received: {data}")
            
            try:
                message = json.loads(data)
                command = message.get("command", "")
                
                if not command:
                    continue
                
                print(f"🎮 Processing command: '{command}'")
                
                # Parse command into strategy
                # Use parse_with_llm() if you have OpenAI API key configured
                strategy = parser.parse_command(command)
                
                print(f"📊 Generated strategy: {strategy}")
                
                # Send strategy back to frontend
                await websocket.send_json(strategy)
                print("✅ Strategy sent to frontend")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                await websocket.send_json({
                    "error": "Invalid JSON format"
                })
            except Exception as e:
                print(f"❌ Error processing command: {e}")
                await websocket.send_json({
                    "error": str(e)
                })
                
    except WebSocketDisconnect:
        print("🔌 Client disconnected")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Commander Backend Server...")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws/commander")
    print("🌐 Health check: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)