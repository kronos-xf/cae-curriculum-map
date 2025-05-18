
import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("aero_courses.csv")

# Build full graph with all connections
G_full = nx.DiGraph()

# Positioning for 8x5 layout
positions = {}
layout_tracker = {}
x_gap, y_gap = 2, 1.5

for idx, row in df.iterrows():
    course = row["Course Code"]
    semester = int(row["Semester"])
    row_number = layout_tracker.get(semester, 0)
    positions[course] = (semester * x_gap, -row_number * y_gap)
    layout_tracker[semester] = row_number + 1
    G_full.add_node(course, title=row["Course Title"])

# Add all edges (prereq and coreq)
for idx, row in df.iterrows():
    course = row["Course Code"]
    prereqs = str(row["Prerequisites"]).split(",") if pd.notna(row["Prerequisites"]) else []
    coreqs = str(row["Corequisites"]).split(",") if pd.notna(row["Corequisites"]) else []
    for pre in prereqs:
        pre = pre.strip()
        if pre and pre in df["Course Code"].values:
            G_full.add_edge(pre, course)
    for co in coreqs:
        co = co.strip()
        if co and co in df["Course Code"].values:
            G_full.add_edge(co, course)

# Streamlit UI
st.title("Aerospace Engineering Curriculum Map")

# Create mapping for dropdown
course_options = {f"{row['Course Code']} – {row['Course Title']}": row["Course Code"] for _, row in df.iterrows()}
dropdown_selection = st.selectbox("Select a course to trace its dependencies:", list(course_options.keys()))
selected_course = course_options[dropdown_selection]

# Get upstream and downstream nodes
def get_upstream(graph, start_node):
    visited = set()
    stack = [start_node]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            stack.extend(graph.predecessors(node))
    visited.discard(start_node)
    return visited

def get_downstream(graph, start_node):
    visited = set()
    stack = [start_node]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            stack.extend(graph.successors(node))
    visited.discard(start_node)
    return visited

upstream = get_upstream(G_full, selected_course)
downstream = get_downstream(G_full, selected_course)
connected = upstream.union(downstream)

# Create display subgraph
G_display = nx.DiGraph()
for node in G_full.nodes():
    G_display.add_node(node)

for u, v in G_full.edges():
    if selected_course in (u, v) or (u in connected and v in connected):
        G_display.add_edge(u, v)

# Draw graph
fig, ax = plt.subplots(figsize=(16, 10))
node_colors = []
for node in G_display.nodes():
    if node == selected_course:
        node_colors.append("orange")
    elif node in connected:
        node_colors.append("lightgreen")
    else:
        node_colors.append("lightblue")

nx.draw(G_display, pos=positions, with_labels=True, node_color=node_colors,
        node_size=2200, font_size=9, font_weight="bold", arrows=True, ax=ax)

plt.title(f"Upstream & Downstream Dependencies for {selected_course}", fontsize=14)
st.pyplot(fig)
st.caption("Orange = selected course | Green = upstream/downstream connected courses")
