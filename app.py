import gradio as gr
import requests
import json
import time

# ---------------------------------------------------------
# 1. PASTE YOUR N8N WEBHOOK URL HERE
# ---------------------------------------------------------

N8N_WEBHOOK_URL = "https://gratifiable-nonequably-israel.ngrok-free.dev/webhook-test/21c6802a-eb78-4a76-8d39-552ee0f73afa"
def send_to_n8n(review_text, platform_source):
    """
    Sends the review to your n8n workflow via Webhook.
    """
    if not review_text:
        return "⚠️ Error: Please enter a review to analyze."

    # This JSON structure matches what your OpenAI node expects
    payload = {
        "message": {
            "content": review_text
        },
        "source": platform_source,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        # Send the data to n8n
        response = requests.post(N8N_WEBHOOK_URL, json=payload)
        
        # Check if it worked
        if response.status_code == 200:
            return f"""
            ### ✅ Success!
            
            **Status:** Sent to Agent.
            **Action:** The AI is analyzing the sentiment and routing the file.
            
            *(Note: Check your Google Drive. A new file has been created in the specific folder based on the sentiment!)*
            """
        else:
            return f"❌ Error {response.status_code}: {response.text}"

    except Exception as e:
        return f"❌ Connection Failed: {str(e)}"

# ---------------------------------------------------------
# 2. THE USER INTERFACE (Layout)
# ---------------------------------------------------------
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    
    # Title and Description
    gr.Markdown(
        """
        # 🧠 Smart Customer Service Router
        ### Powered by n8n + OpenAI
        
        **How it works:** Enter a customer review below. This tool sends it to an AI Agent which:
        1. Analyzes the sentiment (Positive vs. Negative).
        2. Routes it to the correct department (Google Drive Folder).
        """
    )
    
    with gr.Row():
        # Left Side (Inputs)
        with gr.Column():
            gr.Markdown("### 📥 New Ticket")
            input_text = gr.Textbox(
                label="Customer Review / Complaint", 
                placeholder="Example: I ordered this 3 weeks ago and it still hasn't arrived! I am very angry.",
                lines=5
            )
            input_source = gr.Dropdown(
                choices=["Google Reviews", "Yelp", "Email Support", "Twitter"], 
                value="Google Reviews", 
                label="Source Platform"
            )
            submit_btn = gr.Button("🚀 Process Ticket", variant="primary")
            
            gr.Markdown("--- \n **Student:** Manav Kheni | **Course:** AI Workflow Design")

        # Right Side (Output)
        with gr.Column():
            gr.Markdown("### ⚙️ System Status")
            output_display = gr.Markdown(value="*Waiting for input...*")

    # Connect the button to the function
    submit_btn.click(
        fn=send_to_n8n, 
        inputs=[input_text, input_source], 
        outputs=output_display
    )

# Run the app
if __name__ == "__main__":
    demo.launch()