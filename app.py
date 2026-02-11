import gradio as gr
import requests
import pandas as pd
import json
from datetime import datetime

# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------
# Your active ngrok Webhook URL
WEBHOOK_URL = "https://gratifiable-nonequably-israel.ngrok-free.dev/webhook/21c6802a-eb78-4a76-8d39-552ee0f73afa"

# ---------------------------------------------------------
# 2. CORE LOGIC FUNCTION
# ---------------------------------------------------------
def process_ticket(review_text, source, image_filepath=None):
    """
    Sends the review to n8n, analyzes sentiment, and prepares files for download.
    """
    
    # A. Prepare the Payload for n8n
    payload = {
        "message": {
            "content": review_text,
            "source": source,
            "has_attachment": True if image_filepath else False 
        }
    }
    
    try:
        # B. Send to n8n Webhook
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # C. Extract Data (Safely handle missing keys)
        sentiment_score = data.get("sentiment_score", 0)
        sentiment_label = data.get("sentiment_label", "Unknown")
        summary = data.get("summary", "No summary provided.")
        suggested_response = data.get("suggested_response", "No response generated.")
        
        # D. Create Visual Report (Clean Markdown ONLY)
        # Determine emoji based on score
        emoji = "🔴" if int(sentiment_score) <= 5 else "🟢"
        if 5 < int(sentiment_score) < 8:
            emoji = "🟡"
            
        visual_report = f"""
        # {emoji} Analysis Report
        
        | Metric | Value |
        | :--- | :--- |
        | **Sentiment** | **{sentiment_label}** ({sentiment_score}/10) |
        | **Source** | {source} |
        | **Attachment** | {"✅ Yes" if image_filepath else "❌ No"} |
        
        ### 📝 AI Summary
        > *{summary}*
        """
        
        # E. Create Downloadable CSV
        df = pd.DataFrame([{
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Source": source,
            "Review": review_text,
            "Sentiment": sentiment_label,
            "Score": sentiment_score,
            "Summary": summary,
            "Suggested Response": suggested_response
        }])
        
        csv_filename = "ticket_analysis_result.csv"
        df.to_csv(csv_filename, index=False)
        
        # Return Report AND the clean Suggested Response text separately
        return visual_report, suggested_response, csv_filename, data

    except Exception as e:
        # Error Handling
        error_msg = f"❌ Error: {str(e)}"
        return error_msg, "Error generating response.", None, {"error": str(e)}

# ---------------------------------------------------------
# 3. USER INTERFACE (Gradio Blocks)
# ---------------------------------------------------------
# Note: Moved 'theme' to the launch() call at the bottom to fix the warning
with gr.Blocks(title="Smart Customer Router") as demo:
    
    # Header
    gr.Markdown(
        """
        # 🤖 Smart Customer Service Router
        **Analyze reviews, detect sentiment, and triage tickets automatically.**
        """
    )
    
    with gr.Row():
        # --- LEFT COLUMN: INPUTS ---
        with gr.Column(scale=1):
            gr.Markdown("### 📥 New Ticket Input")
            
            input_source = gr.Dropdown(
                ["Email Support", "Google Reviews", "Twitter", "Phone Transcript"], 
                label="Source Platform", 
                value="Email Support"
            )
            
            input_text = gr.Textbox(
                label="Customer Review / Complaint", 
                placeholder="Paste the customer's message here...", 
                lines=5
            )
            
            input_image = gr.Image(
                label="Attach Photo Proof (Optional)", 
                type="filepath", 
                height=150
            )
            
            submit_btn = gr.Button("🚀 Process Ticket", variant="primary", size="lg")

        # --- RIGHT COLUMN: OUTPUTS ---
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Analysis Results")
            
            # 1. Visual Report (Top Half)
            output_visual = gr.Markdown(label="Report Dashboard")
            
            # 2. Suggested Reply (Bottom Half - BIG BOX)
            # FIXED: Removed 'show_copy_button=True' to prevent crash
            output_reply = gr.Textbox(
                label="🤖 Suggested Response (Copy & Paste)", 
                lines=8
            )
            
            # 3. Download Button
            output_file = gr.File(label="Download Report (.csv)")
            
            # 4. Raw JSON (Hidden)
            with gr.Accordion("See Raw Data (JSON)", open=False):
                output_json = gr.JSON()

    # --- CLICKABLE EXAMPLES ---
    gr.Markdown("### ⚡ Quick Test Examples")
    gr.Examples(
        examples=[
            ["This is the absolute worst product. It arrived broken and I want a refund!", "Email Support", None],
            ["I just wanted to say thank you! The service was amazing and Mike was so helpful.", "Google Reviews", None],
            ["Where is my package? The tracking number is 1Z999999999. This is a scam!", "Twitter", None]
        ],
        inputs=[input_text, input_source, input_image]
    )

    # Connect the Button to the Function
    submit_btn.click(
        fn=process_ticket, 
        inputs=[input_text, input_source, input_image], 
        outputs=[output_visual, output_reply, output_file, output_json] 
    )

# Launch the App
if __name__ == "__main__":
    # FIXED: Added theme here to satisfy the warning
    demo.launch(theme=gr.themes.Soft())
