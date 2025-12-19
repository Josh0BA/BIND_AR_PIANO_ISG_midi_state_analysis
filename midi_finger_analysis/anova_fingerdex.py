import pandas as pd
import numpy as np
from scipy.stats import t
from scipy.stats import zscore
from scipy.stats import shapiro
from scipy.stats import mannwhitneyu
from scipy.stats import ttest_ind
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import seaborn as sns
import matplotlib.pyplot as plt  # Extract participant ID, appointment, song, and attempt from filename
participant_id = filename.split('_')[0]
appointment = filename.split('_')[1]
song = filename.split('_')[2]
attempt = filename.split('_')[3].split('.')[0]  # Remove file extension
import math
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import os
from scipy.stats import ttest_rel

from midi_state_analysis.folder_utils import find_midi_data_folder

# Find the MIDI data folder and look for fingergeschicklichkeit.csv in the parent directory
midi_folder = find_midi_data_folder(start_path='.')
if midi_folder:
    csv_path = os.path.join(os.path.dirname(midi_folder), "fingergeschicklichkeit.csv")
else:
    # Fallback to old path if MIDI folder not found
    csv_path = "src/data_analysis_pipeline/Data/fingergeschicklichkeit.csv"

df_finger = pd.read_csv(csv_path)

# JE13CL is a special case, played wrong sequence therefore just take the his played sequence calculated in saving_JE13CL.py
Fingertest1_correct = 16
Fingertest2_correct = 26

df_finger.loc[df_finger['Participant_ID'] == 'JE13CL', 'Fingertest1_correct'] = Fingertest1_correct
df_finger.loc[df_finger['Participant_ID'] == 'JE13CL', 'Fingertest2_correct'] = Fingertest2_correct




## Statistical Analysis

df_finger_clean = df_finger.rename(columns=lambda x: x.replace('-', '_'))

# Create long format data for ANOVA with Timepoint (Pretest vs Posttest)
data_long = []
for idx, row in df_finger_clean.iterrows():
    participant_id = row['Participant_ID']
    
    # Pretest (Fingertest1 and Fingertest2)
    for col in ['Fingertest1_correct', 'Fingertest2_correct']:
        if col in df_finger_clean.columns and not pd.isna(row[col]):
            data_long.append({
                'Participant_ID': participant_id,
                'Timepoint': 'Pretest',
                'Test': col,
                'Score': row[col]
            })
    
    # Posttest (Fingertest3 and Fingertest4)
    for col in ['Fingertest3_correct', 'Fingertest4_correct']:
        if col in df_finger_clean.columns and not pd.isna(row[col]):
            data_long.append({
                'Participant_ID': participant_id,
                'Timepoint': 'Posttest',
                'Test': col,
                'Score': row[col]
            })

df_long = pd.DataFrame(data_long)

# Paired t-test: Fingertest1 vs Fingertest3
if 'Fingertest1_correct' in df_finger_clean.columns and 'Fingertest3_correct' in df_finger_clean.columns:
    t_stat, p_val = ttest_rel(df_finger_clean['Fingertest1_correct'], df_finger_clean['Fingertest3_correct'])
    print(f"\nPaired t-test (Fingertest1 vs Fingertest3):")
    print(f"  t-statistic = {t_stat:.2f}")
    print(f"  p-value = {p_val:.4f}")
    print(f"  Result: {'Significant difference' if p_val < 0.05 else 'No significant difference'}")

# ANOVA: Pretest vs Posttest
print(f"\n{'='*60}")
print("ANOVA: Pretest vs Posttest")
print(f"{'='*60}")

# Check normality for each timepoint
for timepoint in df_long['Timepoint'].unique():
    data = df_long[df_long['Timepoint'] == timepoint]['Score']
    stat, p = shapiro(data)
    print(f"\nShapiro-Wilk Test for {timepoint}:")
    print(f"  W = {stat:.4f}, p = {p:.4f}")
    print(f"  {'Normally distributed' if p > 0.05 else 'NOT normally distributed'}")

# Perform ANOVA
model = smf.ols('Score ~ C(Timepoint)', data=df_long).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(f"\nANOVA Results:")
print(anova_table)

if anova_table['PR(>F)'][0] < 0.05:
    print("\n→ Significant difference between Pretest and Posttest! (p < 0.05)")
else:
    print("\n→ No significant difference between Pretest and Posttest (p >= 0.05)")
    # Mann-Whitney U as alternative
    pretest_scores = df_long[df_long['Timepoint'] == 'Pretest']['Score']
    posttest_scores = df_long[df_long['Timepoint'] == 'Posttest']['Score']
    u_stat, p_mwu = mannwhitneyu(pretest_scores, posttest_scores, alternative='two-sided')
    print(f"\nMann-Whitney U Test (alternative):")
    print(f"  U = {u_stat:.2f}, p = {p_mwu:.4f}")

# --------- plot the results -----------
print(f"\n{'='*60}")
print("Generating Plots...")
print(f"{'='*60}")

# Create boxplot for Pretest vs Posttest comparison
fig, ax = plt.subplots(figsize=(8, 6))
sns.boxplot(x='Timepoint', y='Score', data=df_long, ax=ax, palette='Set2')
sns.stripplot(x='Timepoint', y='Score', data=df_long, color='black', size=4, jitter=True, ax=ax, alpha=0.6)
ax.set_title('Fingergeschicklichkeit: Pretest vs Posttest', fontsize=16, fontweight='bold')
ax.set_xlabel('Timepoint', fontsize=14)
ax.set_ylabel('Correct Sequences', fontsize=14)
ax.tick_params(axis='both', labelsize=12)
plt.tight_layout()
plt.show()

# Select columns to plot individually
cols = [c for c in df_finger_clean.columns if 'correct' in c or 'keys' in c]
num_plots = len(cols)

# Set grid size
cols_per_row = 4  # Adjust this to control layout
rows = math.ceil(num_plots / cols_per_row)

# Create subplots
fig, axes = plt.subplots(nrows=rows, ncols=cols_per_row, figsize=(6 * cols_per_row, 5 * rows))
axes = axes.flatten()  # Flatten in case of multi-row layout

# Plot each distribution
for i, col in enumerate(cols):
    ax = axes[i]
    sns.boxplot(y=df_finger_clean[col], ax=ax)
    sns.stripplot(y=df_finger_clean[col], color='black', size=6, jitter=True, ax=ax)
    ax.set_title(f'{col}', fontsize=16)
    ax.set_ylabel('correct sequences' if 'correct' in col else 'key presses', fontsize=14)

    ax.tick_params(axis='y', labelsize=16)

    # Set y-axis limits
    if 'correct' in col:
        ax.set_ylim(3, 35)
    elif 'keys' in col:
        ax.set_ylim(50, 180)

# Remove empty subplots
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()

# Save each boxplot individually

# Define output path
output_dir = r"C:\Users\tobia\OneDrive\AA Uni\ISPW_Erlacher\Bacherlorarbeit\Verschriftlichung\Grafiken"

# Ensure directory exists
os.makedirs(output_dir, exist_ok=True)

# Save each boxplot individually
for col in cols:
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.boxplot(y=df_finger_clean[col], ax=ax)
    sns.stripplot(y=df_finger_clean[col], color='black', size=4, jitter=True, ax=ax)

    # Title and axis formatting
    ax.set_title(f'{col}', fontsize=16)
    
    # Set custom y-label
    if col in ['Fingertest1_correct', 'Fingertest2_correct', 'Fingertest3_correct', 'Fingertest4_correct']:
        ax.set_ylabel('Correct Sequences', fontsize=14)
    elif 'keys' in col:
        ax.set_ylabel('Key Presses', fontsize=14)
    else:
        ax.set_ylabel(col.replace('_', ' ').title(), fontsize=14)

    # Axis ticks
    ax.tick_params(axis='y', labelsize=12)

    # Set y-limits
    if col in ['Fingertest3_correct', 'Fingertest4_correct']:  # the post-test ones
        ax.set_ylim(10, 35)
    elif 'correct' in col:
        ax.set_ylim(5, 30)
    elif 'keys' in col:
        ax.set_ylim(60, 180)

    # Save figure
    filename = f"{col}.png"
    filepath = os.path.join(output_dir, filename)
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close(fig)