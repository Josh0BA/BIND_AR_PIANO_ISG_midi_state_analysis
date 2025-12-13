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
import matplotlib.pyplot as plt  
import math
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import os
from scipy.stats import ttest_rel

df_finger = pd.read_csv("src/data_analysis_pipeline/Data/fingergeschicklichkeit.csv")


# add groupe column to the dataframes
# Sample category list as a string
category_list = """
AA10MA Klassisch
BE01CL AR
BE13NA Klassisch
BE17MA AR
BI21FL Klassisch
BU01FR Klassisch
DA27SV Klassisch
DI03CA AR
FO09MA AR
GE03KA AR
GI16CA AR
JE13CL Klassisch
LU03GA Klassisch
SU13BA Klassisch
SU22PA AR
VA10SI Klassisch
WA24AN AR
ZU17AL AR
"""

#Convert to dictionary
category_dict = dict(line.split() for line in category_list.strip().split('\n'))

# Convert the dictionary to a DataFrame
df_finger['Category'] = df_finger[df_finger.columns[0]].map(category_dict)

# remove contestants that did not complete the study
df_finger = df_finger[df_finger['Category'].notna()]

# JE13CL is a special case, played wrong sequence therefore just take the his played sequence calculated in saving_JE13CL.py
Finger_1_1_correct = 16
Finger_1_2_correct = 26

df_finger.loc[df_finger['Participant_ID'] == 'JE13CL', 'Finger_1-1_correct'] = Finger_1_1_correct
df_finger.loc[df_finger['Participant_ID'] == 'JE13CL', 'Finger_1-2_correct'] = Finger_1_2_correct




## Anovatest

df_finger_clean = df_finger.rename(columns=lambda x: x.replace('-', '_'))

# ttest
# T-Test
klassisch = df_finger_clean[df_finger_clean['Category'] == 'Klassisch']
t_stat, p_val = ttest_rel(klassisch['Finger_1_1_correct'], klassisch['Finger_5_1_correct'])
print(f"Klassische Gruppe Pre vs. Post: p = {p_val:.4f}")
print(f"t(8) = {t_stat:.2f}")

# List of columns to test
cols_to_test = [col for col in df_finger_clean.columns if ('correct' in col or 'keys' in col)]

# Run ANOVA for each and collect significant columns
significant_cols = []
for col in cols_to_test:
    print(f"\n--- Prüfung: {col} ---")
    
    # Normalverteilung je Gruppe
    for group in df_finger_clean['Category'].unique():
        stat, p = shapiro(df_finger_clean[df_finger_clean['Category'] == group][col])
        print(f"Shapiro-Wilk für {group}: p = {p:.4f}")
    
    # ANOVA
    model = smf.ols(f'{col} ~ C(Category)', data=df_finger_clean).fit()
    anova = sm.stats.anova_lm(model, typ=2)
    p_value = anova['PR(>F)'][0]
    print(f"ANOVA: p = {p_value:.4f}")
    
    if p_value < 0.05:
        print(" → Signifikanter Unterschied! (ANOVA)")
        # Optional: Post-hoc schon erledigt durch Tukey
    else:
        # Wenn ANOVA nicht signifikant oder Normalverteilung fraglich
        # prüfe zusätzlich Mann-Whitney
        group1 = df_finger_clean[df_finger_clean['Category'] == 'Klassisch'][col]
        group2 = df_finger_clean[df_finger_clean['Category'] == 'AR'][col]
        stat, p_mwu = mannwhitneyu(group1, group2, alternative='two-sided')
        print(f"Mann-Whitney-U-Test: p = {p_mwu:.4f}")



# Plot all Tukey HSD results in one figure
if significant_cols:
    fig, axes = plt.subplots(nrows=len(significant_cols), figsize=(8, 4 * len(significant_cols)))
    if len(significant_cols) == 1:
        axes = [axes]  # make it iterable
    for ax, col in zip(axes, significant_cols):
        tukey = pairwise_tukeyhsd(endog=df_finger_clean[col], groups=df_finger_clean['Category'], alpha=0.05)
        tukey.plot_simultaneous(ax=ax)
        ax.set_title(f'Tukey HSD: {col}')
    plt.tight_layout()
    plt.show()

# --------- plot the results -----------
# Select columns to plot
cols = [c for c in df_finger_clean.columns if 'correct' in c or 'keys' in c]
num_plots = len(cols)

# Set grid size
cols_per_row = 4  # Adjust this to control layout
rows = math.ceil(num_plots / cols_per_row)

# Create subplots
fig, axes = plt.subplots(nrows=rows, ncols=cols_per_row, figsize=(6 * cols_per_row, 5 * rows))
axes = axes.flatten()  # Flatten in case of multi-row layout

# Plot each boxplot
for i, col in enumerate(cols):
    ax = axes[i]
    sns.boxplot(x='Category', y=col, data=df_finger_clean, ax=ax)
    sns.stripplot(x='Category', y=col, data=df_finger_clean, color='black', size=6, jitter=True, ax=ax)
    ax.set_title(f'{col} by Category', fontsize=16)
    ax.set_xlabel('', fontsize=16)
    ax.set_ylabel('correct sequences', fontsize=14)

    ax.tick_params(axis='x', labelsize=16, rotation=45)
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
    sns.boxplot(x='Category', y=col, data=df_finger_clean, ax=ax)
    sns.stripplot(x='Category', y=col, data=df_finger_clean, color='black', size=4, jitter=True, ax=ax)

    # Title and axis formatting
    ax.set_title(f'{col} by Category', fontsize=16)
    ax.set_xlabel('')
    
    # Set custom y-label
    if col == 'Finger_1_1_correct':
        ax.set_ylabel('Correct Sequences', fontsize=14)
    elif col == 'Finger_1_2_correct':
        ax.set_ylabel('Correct Sequences', fontsize=14)
    elif col == 'Finger_5_1_correct':
        ax.set_ylabel('Correct Sequences', fontsize=14)
    elif col == 'Finger_5_2_correct':
        ax.set_ylabel('Correct Sequences', fontsize=14)
    elif 'keys' in col:
        ax.set_ylabel('Key Presses', fontsize=14)
    else:
        ax.set_ylabel(col.replace('_', ' ').title(), fontsize=14)

    # Axis ticks
    ax.tick_params(axis='x', labelsize=12, rotation=45)
    ax.tick_params(axis='y', labelsize=12)

    # Set y-limits
    if col in ['Finger_5_1_correct', 'Finger_5_2_correct']:  # the top-right ones
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