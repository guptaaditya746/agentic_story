import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# === Configuration ===
st.set_page_config(page_title="Model vs Human Ratings", layout="wide")
st.title("🧠 Human vs Model Evaluation Dashboard")

# === Load data ===
df = pd.read_csv("notebook/rating_of_story/aggregate_rating_of_story.csv")
df.columns = df.columns.str.strip()  # remove any accidental whitespace

# === Define dimensions and raters ===
dimensions = ['empathy', 'surprise', 'engagement', 'complexity', 'coherence', 'fluency']
raters = ['aditya', 'kole', 'dev']

# === Compute average human scores ===
for dim in dimensions:
    df[f'avg_human_{dim}'] = df[[f'{r}_{dim}_human' for r in raters]].mean(axis=1)

# === Compute human disagreement (std dev) ===
for dim in dimensions:
    df[f'{dim}_disagreement'] = df[[f'{r}_{dim}_human' for r in raters]].std(axis=1)

# === Sidebar: Story selection ===
story_idx = st.sidebar.slider("Select a Story Index", 0, len(df) - 1, 0)
story_id = df['story_id'].iloc[story_idx]
st.sidebar.markdown(f"**Story ID:** `{story_id}`")
st.sidebar.markdown(f"**Story:** {df['story'].iloc[story_idx]}")

# === Radar Chart ===
def radar_plot(idx):
    angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
    angles += angles[:1]

    avg_human = [df[f'avg_human_{dim}'].iloc[idx] for dim in dimensions] + [df[f'avg_human_{dimensions[0]}'].iloc[idx]]
    llama = [df[f'{dim}_llama3.1'].iloc[idx] for dim in dimensions] + [df[f'{dimensions[0]}_llama3.1'].iloc[idx]]
    gpt = [df[f'{dim}_gpt4o'].iloc[idx] for dim in dimensions] + [df[f'{dimensions[0]}_gpt4o'].iloc[idx]]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, avg_human, label='Avg Human', marker='o')
    ax.plot(angles, llama, label='LLaMA 3.1', marker='o')
    ax.plot(angles, gpt, label='GPT-4o', marker='o')
    ax.fill(angles, avg_human, alpha=0.1)
    ax.fill(angles, llama, alpha=0.1)
    ax.fill(angles, gpt, alpha=0.1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions)
    ax.set_yticklabels([])
    ax.set_title(f'Radar Chart for Story {idx} ({story_id})')
    ax.legend()
    return fig

st.subheader("📍 Story Radar Comparison")
st.pyplot(radar_plot(story_idx))

# === Disagreement Heatmap ===
st.subheader("📊 Human Disagreement per Dimension")
fig, ax = plt.subplots(figsize=(10, 6))
disagree_cols = [f'{dim}_disagreement' for dim in dimensions]
sns.heatmap(df[disagree_cols], annot=True, fmt=".2f", cmap="Reds",
            xticklabels=dimensions, yticklabels=df["story_id"], ax=ax)
ax.set_xlabel("Dimension")
ax.set_ylabel("Story ID")
st.pyplot(fig)

# === Correlation Matrix (Spearman) ===
st.subheader("🔗 Correlation Matrix (Spearman)")
corr_cols = [f'avg_human_{dim}' for dim in dimensions] + \
            [f'{dim}_llama3.1' for dim in dimensions] + \
            [f'{dim}_gpt4o' for dim in dimensions]

spearman_corr = df[corr_cols].corr(method='spearman')
fig, ax = plt.subplots(figsize=(12, 8))
sns.heatmap(spearman_corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Spearman Correlation Matrix")
st.pyplot(fig)

st.markdown("---")
st.caption("Built with ❤️ using Streamlit. Data: Human & Model Story Ratings")
