import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import litellm
import json
import asyncio

app = FastAPI()

@app.get("/")
@app.get("/v1")
@app.head("/")
@app.head("/v1")
async def health_check():
    return Response(status_code=200)

@app.post("/v1/messages")
async def anthropic_messages(request: Request):
    data = await request.json()
    
    messages = data.get("messages", [])
    model = "ollama/qwen3.5-9b-local"
    stream = data.get("stream", False)
    
    # Handle system message
    if "system" in data:
        # LiteLLM handles system messages at the start
        if isinstance(data["system"], str):
            messages.insert(0, {"role": "system", "content": data["system"]})
        elif isinstance(data["system"], list):
            for block in reversed(data["system"]):
                if block.get("type") == "text":
                    messages.insert(0, {"role": "system", "content": block["text"]})

    # Call LiteLLM (it handles the Anthropic -> OpenAI conversion for Ollama)
    try:
        response = litellm.completion(
            model=model,
            messages=messages,
            stream=stream,
            api_base="http://localhost:11434"
        )
    except Exception as e:
        print(f"Error calling LiteLLM: {e}")
        return {"error": str(e)}, 500

    if stream:
        async def event_generator():
            yield f"data: {json.dumps({'type': 'message_start', 'message': {'id': 'msg_123', 'type': 'message', 'role': 'assistant', 'content': [], 'model': model, 'usage': {'input_tokens': 0, 'output_tokens': 0}}})}\n\n"
            yield f"data: {json.dumps({'type': 'content_block_start', 'index': 0, 'content_block': {'type': 'text', 'text': ''}})}\n\n"
            
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                if content:
                    yield f"data: {json.dumps({'type': 'content_block_delta', 'index': 0, 'delta': {'type': 'text_delta', 'text': content}})}\n\n"
            
            yield f"data: {json.dumps({'type': 'content_block_stop', 'index': 0})}\n\n"
            yield f"data: {json.dumps({'type': 'message_delta', 'delta': {'stop_reason': 'end_turn', 'stop_sequence': None}, 'usage': {'output_tokens': 0}})}\n\n"
            yield f"data: {json.dumps({'type': 'message_stop'})}\n\n"
            
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        content = response.choices[0].message.content
        return {
            "id": response.id,
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": content}],
            "model": model,
            "usage": {"input_tokens": 0, "output_tokens": 0}
        }

if __name__ == "__main__":
    print("Bridge starting on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
