# 📊 LIDA Visualization Agent

This Streamlit application allows you to automatically summarize and visualize your tabular data using natural language prompts, powered by the [LIDA](https://github.com/vis-nlp/LIDA) framework and a local language model served via [LM Studio](https://lmstudio.ai/).

---

## 🔧 Features

* **Upload CSV Data**
* **Automatic Summarization**: Get a summary and suggested visualization goals
* **Custom Visual Questions**: Ask specific questions and get visualizations generated
* **Supports Multiple Chart Libraries**: Seaborn, Matplotlib, Plotly
* **Runs Fully Local** via LM Studio-compatible models like DeepSeek, Mistral, etc.

---

## 🛠️ Requirements

* Python 3.8+
* LM Studio running locally with a supported model (e.g., `deepseek-coder-v2-lite-instruct`)
* `pip install` the following Python packages:

```bash
pip install streamlit pandas requests openai python-dotenv llmx lida
```

---

## 🚀 Running the App

1. **Start LM Studio** and load a model (tested with `deepseek-coder-v2-lite-instruct`)
2. **Run the app**

```bash
streamlit run app.py
```

3. **Upload your CSV file** and choose between:

   * **"Summarize"**: Get data summary + suggested goals (charts are not shown here)
   * **"Question based graph"**: Enter a custom question to generate a specific chart

---

## ✅ Example Queries

Paste these in the "Question based graph" tab:

* "Show a bar chart of values in the Savings\_Objectives column."
* "Compare Mutual\_Funds and Equity\_Market investment counts."
* "Plot the frequency of Monitor\_Frequency."

---

## 📸 App Screenshots

### 🔹 Summary Page

![Screenshot 2025-05-26 230022](https://github.com/user-attachments/assets/267cfc85-93af-4241-af00-3f42ce770e8c)
![Screenshot 2025-05-26 230028](https://github.com/user-attachments/assets/7c10248e-d19b-422e-a306-3ee64cbc5c12)


---

### 🔹 Suggested Visualizations (Goals only)



---![Screenshot 2025-05-26 230133](https://github.com/user-attachments/assets/0d2e281f-e9b3-4be4-a4e4-fe120acdc880)


### 🔹 Custom Graph from User Query


---
![Screenshot 2025-05-26 225939](https://github.com/user-attachments/assets/50b8a57e-8436-4b18-a307-42e6a4391f23)
![Screenshot 2025-05-26 225953](https://github.com/user-attachments/assets/c0ca3ea1-0dad-4377-b149-176ee4ad4203)

## 🧠 Model Setup Notes


* The app auto-connects to LM Studio at `http://127.0.0.1:1234`
* Model ID should match what's loaded in LM Studio (e.g., `deepseek-coder-v2-lite-instruct`)

---

## 📁 Folder Structure

```
├── app.py               # Streamlit main app file
├── .env                 # Environment config for API key + base URL
├── testing_cleaned.csv  # Example input file (optional)
├── screenshots/         # Folder with screenshot images
├── README.md            # You're here!
```

---

## 🙌 Credits

* [LIDA by vis-nlp](https://github.com/vis-nlp/LIDA)
* [LM Studio](https://lmstudio.ai/)
* [Streamlit](https://streamlit.io/)

---

## 📜 License

This project is licensed under the MIT License.
