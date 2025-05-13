
import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Load course data
df = pd.read_csv("aero_courses.csv")

# Build graph
G = nx.DiGraph()

# Assign fixed positions in 8x5 grid layout
positions = {}
max_rows = 5
x_gap, y_gap = 2, 1.5

layout_tracker = {}  # track number of courses per semester
for idx, row in df.iterrows():
    course = row["Course Code"]
    semester = int(row["Semester"])
    row_number = layout_tracker.get(semester, 0)
    positions[course] = (semester * x_gap, -row_number * y_gap)
    layout_tracker[semester] = row_number + 1
    G.add_node(course, title=row["Course Title"])

# Add edges for prerequisites and corequisites
for idx, row in df.iterrows():
    course = row["Course Code"]
    prereqs = str(row["Prerequisites"]).split(",") if pd.notna(row["Prerequisites"]) else []
    coreqs = str(row["Corequisites"]).split(",") if pd.notna(row["Corequisites"]) else []
    for pre in prereqs:
        pre = pre.strip()
        if pre and pre in df["Course Code"].values:
            G.add_edge(pre, course)
    for co in coreqs:
        co = co.strip()
        if co and co in df["Course Code"].values:
            G.add_edge(co, course)

# Streamlit app interface
st.title("Aerospace Engineering Curriculum Map")
selected_course = st.selectbox("Select a course to trace its dependencies:", df["Course Code"])

# Highlight logic
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

downstream = get_downstream(G, selected_course)

# Draw the graph
fig, ax = plt.subplots(figsize=(16, 10))
node_colors = []
for node in G.nodes():
    if node == selected_course:
        node_colors.append("orange")
    elif node in downstream:
        node_colors.append("lightgreen")
    else:
        node_colors.append("lightblue")

nx.draw(G, pos=positions, with_labels=True, node_color=node_colors,
        node_size=2000, font_size=7, font_weight="bold", arrows=True, ax=ax)

plt.title(f"Dependencies from {selected_course}")
st.pyplot(fig)
st.caption("Orange = selected course | Green = courses that depend on it")
