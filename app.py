import streamlit as st
from transformers import AutoModel
from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os

# Layer keyword explanations
layer_info = {
    "embedding": "Converts tokens into vector representations.",
    "attention": "Focuses on important tokens in the input.",
    "linear": "Applies learned transformations to data.",
    "dropout": "Helps prevent overfitting by randomly zeroing values.",
    "layernorm": "Normalizes data to stabilize training."
}

def explain(name):
    for keyword, expl in layer_info.items():
        if keyword in name.lower():
            return expl
    return "Function not recognized."

def visualize_model(model):
    net = Network(height="600px", width="100%", directed=True)
    net.set_options('''{
      "layout": {"hierarchical": {"enabled": true, "direction": "LR"}},
      "physics": {"enabled": false}
    }''')
    net.add_node("Root", label="Model", title="Model Root")

    def add_nodes(module, parent="Root", prefix=""):
        for name, child in module.named_children():
            node_id = prefix + name
            label = f"{name}\\n({child.__class__.__name__})"
            title = explain(child.__class__.__name__)
            net.add_node(node_id, label=label, title=title)
            net.add_edge(parent, node_id)
            add_nodes(child, node_id, node_id + ".")

    add_nodes(model)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        tmp_path = tmp.name
    net.write_html(tmp_path)

    with open(tmp_path, "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=650, scrolling=True)
    os.remove(tmp_path)

# Streamlit app UI
st.title("🤖 Basic Transformer Visualizer")
model_name = st.text_input("Enter model name", "distilbert-base-uncased")

if st.button("Visualize Model"):
    with st.spinner("Loading model..."):
        model = AutoModel.from_pretrained(model_name)
        visualize_model(model)
