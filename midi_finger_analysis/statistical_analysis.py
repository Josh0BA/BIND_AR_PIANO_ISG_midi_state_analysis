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

df_finger = pd.read_csv("src/data_analysis_pipeline/Data/fingergeschicklichkeit.csv")
df_sun = pd.read_csv("src/data_analysis_pipeline/Data/risingsun_score.csv")
df_blues = pd.read_csv("src/data_analysis_pipeline/Data/blues_score.csv")


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

# --------- fuctions -----------
def analyze_scores(df):
    df_numeric = df.drop(columns=['Participant_ID', 'Category'])

    # Sample size and degrees of freedom
    n = len(df_numeric)
    dfree = n - 1

    # Confidence level
    confidence = 95
    alpha = (100 - confidence) / 100  # e.g. 0.05 for 95% CI

    # Calculate stats
    mean = df_numeric.mean()
    std = df_numeric.std()  # Standard Deviation
    se = std / np.sqrt(n)  # Standard Error

    # TINV equivalent: two-tailed t critical value
    t_critical = t.ppf(1 - alpha / 2, dfree)

    # Confidence interval bounds
    ci_lower = mean - t_critical * se
    ci_upper = mean + t_critical * se

    # Combine into summary table
    df_summary = pd.DataFrame({
        'Mean': mean,
        'Std Dev': std,
        'Std Error': se,
        'CI Lower (95%)': ci_lower,
        'CI Upper (95%)': ci_upper,
        'T Critical': t_critical
    })

    df_numeric = df.select_dtypes(include=np.number)
    for col in df_numeric.columns:
        stat, p = shapiro(df_numeric[col])
        normality = p # if p < 0.05, the data is not normally distributed
        df_summary.loc[col, 'Normality'] = normality
   
    return df_summary

def ttest(df1, df2): #df1 = df_klassisch, df2 = df_ar
    # Sample sizes
    n1 = len(df1)
    n2 = len(df2)

    # Store results
    results = []

    for col in df1.index:
        # Means and standard deviations
        mean1 = df1.loc[col, 'Mean']
        mean2 = df2.loc[col, 'Mean']
        sd1 = df1.loc[col, 'Std Dev']
        sd2 = df2.loc[col, 'Std Dev']

        # Welch's t-test calculation
        se_diff = np.sqrt((sd1**2 / n1) + (sd2**2 / n2))
        t_stat = (mean1 - mean2) / se_diff

        # Degrees of freedom (Welch-Satterthwaite equation)
        df_num = (sd1**2 / n1 + sd2**2 / n2)**2
        df_den = ((sd1**2 / n1)**2 / (n1 - 1)) + ((sd2**2 / n2)**2 / (n2 - 1))
        df_effective = df_num / df_den

        # Two-tailed p-value
        p_value = 2 * t.sf(np.abs(t_stat), df_effective)

        # Calculate Cohen's d
        pooled_sd = np.sqrt((sd1**2 + sd2**2) / 2)
        cohen_d_value = (mean1 - mean2) / pooled_sd if pooled_sd != 0 else np.nan

        # Interpret effect size
        if np.isnan(cohen_d_value):
            effect_size_label = "N/A"
        elif abs(cohen_d_value) < 0.2:
            effect_size_label = "Negligible"
        elif abs(cohen_d_value) < 0.5:
            effect_size_label = "Small"
        elif abs(cohen_d_value) < 0.8:
            effect_size_label = "Medium"
        else:
            effect_size_label = "Large"


        results.append({
            'Measure': col,
            'Mean klassisch': mean1,
            'Mean ar': mean2,
            't-statistic': t_stat,
            'df': df_effective,
            'p-value': p_value,
            'Significant (p < 0.05)': p_value < 0.05,
            "Cohen's d": cohen_d_value,
            'Effect Size': effect_size_label
        })

    return pd.DataFrame(results)

def auto_stat_test_from_summary(df_summary_klassisch, df_summary_ar, df_raw_klassisch, df_raw_ar):
    # Use numeric columns from raw data
    df1 = df_raw_klassisch.select_dtypes(include=np.number)
    df2 = df_raw_ar.select_dtypes(include=np.number)

    results = []

    for col in df1.columns:
        group1 = df1[col].dropna()
        group2 = df2[col].dropna()

        # Get p-values from the summary
        p_norm_klassisch = df_summary_klassisch.loc[col, 'Normality']
        p_norm_ar = df_summary_ar.loc[col, 'Normality']

        # Decide test based on normality
        if p_norm_klassisch >= 0.05 and p_norm_ar >= 0.05:
            # Welch's t-test
            t_stat, p_value = ttest_ind(group1, group2, equal_var=False)

            # Means and SDs
            mean1, mean2 = group1.mean(), group2.mean()
            sd1, sd2 = group1.std(), group2.std()

            # Cohen's d
            pooled_sd = np.sqrt((sd1**2 + sd2**2) / 2)
            cohen_d = (mean1 - mean2) / pooled_sd if pooled_sd != 0 else np.nan

            # Effect size label
            if np.isnan(cohen_d):
                effect_label = "N/A"
            elif abs(cohen_d) < 0.2:
                effect_label = "Negligible"
            elif abs(cohen_d) < 0.5:
                effect_label = "Small"
            elif abs(cohen_d) < 0.8:
                effect_label = "Medium"
            else:
                effect_label = "Large"

            results.append({
                'Measure': col,
                'Test': 'Welch t-test',
                'p-value': p_value,
                'Significant (p < 0.05)': p_value < 0.05,
                'Cohen\'s d': cohen_d,
                'Effect Size': effect_label
            })

        else:
            # Mann–Whitney U test
            u_stat, p_value = mannwhitneyu(group1, group2, alternative='two-sided')

            results.append({
                'Measure': col,
                'Test': 'Mann-Whitney U',
                'p-value': p_value,
                'Significant (p < 0.05)': p_value < 0.05,
                'Cohen\'s d': None, #not neede because Mann–Whitney U test is non-parametric therefofe no effect size can be calculated
                'Effect Size': 'N/A'
            })

    return pd.DataFrame(results)

def remove_outliers_z(df): # apply to all numeric columns (excluding ID and Category)
    df_numeric = df.select_dtypes(include=np.number)
    z_scores = np.abs(zscore(df_numeric))
    mask = (z_scores < 3).all(axis=1)  # keep only rows where all values are within 3 std
    return df[mask]

def check_normality_shapiro(df, group_name=""):
    df_numeric = df.select_dtypes(include=np.number)
    for col in df_numeric.columns:
        stat, p = shapiro(df_numeric[col])
        print(f"{group_name} - {col}: W={stat:.3f}, p={p:.3f} {'(Not normal)' if p < 0.05 else '(Normal)'}")

def grubbs_test(values, alpha=0.05):
    """
    Applies one-sided Grubbs' test for a single outlier.
    Returns the index of the outlier, or None if no outlier is found.
    """
    n = len(values)
    if n < 3:
        return None

    mean_y = np.mean(values)
    std_y = np.std(values, ddof=1)
    abs_diffs = np.abs(values - mean_y)
    max_dev_idx = abs_diffs.idxmax()
    G_calculated = abs_diffs[max_dev_idx] / std_y

    # Critical value from Grubbs' distribution
    t_crit = stats.t.ppf(1 - alpha / (2 * n), n - 2)
    G_critical = ((n - 1) / np.sqrt(n)) * np.sqrt(t_crit**2 / (n - 2 + t_crit**2))

    if G_calculated > G_critical:
        return max_dev_idx
    else:
        return None

def replace_outliers_with_nan(raw_df, summary_df, alpha=0.05, verbose=False):
    """
    Replaces outlier values with NaN in raw_df, based on normality info from summary_df.
    Uses Grubbs' test for normal variables, IQR method otherwise.
    
    Parameters:
    - raw_df: original data with numeric columns and 'Participant_ID'
    - summary_df: DataFrame with index = variable names and a 'Normality' column
    - alpha: significance level for Grubbs test (default 0.05)
    - verbose: if True, prints which values were set to NaN
    """
    df_clean = raw_df.copy()
    df_clean.set_index("Participant_ID", inplace=True)
    numeric_cols = df_clean.select_dtypes(include=np.number).columns

    for col in numeric_cols:
        if col not in summary_df.index:
            continue
        
        values = df_clean[col].dropna()
        if len(values) < 3:
            continue  # Not enough data to test
        
        p_normal = summary_df.loc[col, "Normality"]
        is_normal = p_normal > 0.05

        if is_normal:
            # Grubbs test
            outlier_idx = grubbs_test(values, alpha=alpha)
            if outlier_idx is not None:
                df_clean.loc[outlier_idx, col] = np.nan
                if verbose:
                    print(f"[Grubbs] Outlier in '{col}' at participant {outlier_idx} set to NaN")
        else:
            # IQR method
            Q1 = values.quantile(0.25)
            Q3 = values.quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outlier_mask = (values < lower) | (values > upper)
            for idx in values.index[outlier_mask]:
                df_clean.loc[idx, col] = np.nan
                if verbose:
                    print(f"[IQR] Outlier in '{col}' at participant {idx} set to NaN")

    df_clean.reset_index(inplace=True)
    return df_clean

# ----------- prepare data and clean --------------

# Convert to dictionary
category_dict = dict(line.split() for line in category_list.strip().split('\n'))

# Convert the dictionary to a DataFrame
df_finger['Category'] = df_finger[df_finger.columns[0]].map(category_dict)
df_sun['Category'] = df_sun[df_sun.columns[0]].map(category_dict)
df_blues['Category'] = df_blues[df_blues.columns[0]].map(category_dict)

# raw split into seperate groups
df_finger_klassisch_raw = df_finger[df_finger['Category'] == 'Klassisch']
df_finger_ar_raw = df_finger[df_finger['Category'] == 'AR']
df_finger_combined_raw = pd.concat([df_finger_klassisch_raw, df_finger_ar_raw], axis=0)
df_sun_klassisch_raw = df_sun[df_sun['Category'] == 'Klassisch']
df_sun_ar_raw = df_sun[df_sun['Category'] == 'AR']
df_blues_klassisch_raw = df_blues[df_blues['Category'] == 'Klassisch']
df_blues_ar_raw = df_blues[df_blues['Category'] == 'AR']

# remove contestants that did not complete the study
df_finger = df_finger[df_finger['Category'].notna()]
df_sun = df_sun[df_sun['Category'].notna()]
df_blues = df_blues[df_blues['Category'].notna()]

# JE13CL is a special case, played wrong sequence therefore just take the his played sequence calculated in saving_JE13CL.py
Finger_1_1_correct = 16
Finger_1_2_correct = 26

df_finger.loc[df_finger['Participant_ID'] == 'JE13CL', 'Finger_1-1_correct'] = Finger_1_1_correct
df_finger.loc[df_finger['Participant_ID'] == 'JE13CL', 'Finger_1-2_correct'] = Finger_1_2_correct



# separate the data into two groups based on the category
df_finger_klassisch = df_finger[df_finger['Category'] == 'Klassisch']
df_finger_ar = df_finger[df_finger['Category'] == 'AR']
df_finger_combined = pd.concat([df_finger_klassisch, df_finger_ar], axis=0)

# calculate the mean, standard deviation, standard error and confidence interval for each group
df_finger_summary_klassisch = analyze_scores(df_finger_klassisch)
df_finger_summary_ar = analyze_scores(df_finger_ar)
df_finger_summary_combined = analyze_scores(df_finger_combined)

print(df_finger_summary_combined)

# remove outliers using Grubbs test and IQR method



df_finger_combinded_clean = replace_outliers_with_nan(df_finger_combined_raw, df_finger_summary_combined, alpha=0.05, verbose=True)
df_finger_klassisch_clean = replace_outliers_with_nan(df_finger_klassisch_raw, df_finger_summary_klassisch, alpha=0.05, verbose=True)
df_finger_ar_clean = replace_outliers_with_nan(df_finger_ar_raw, df_finger_summary_ar, alpha=0.05, verbose=True)
    
# test for statistical significance
df_finger_ttest_summary = ttest(df_finger_summary_klassisch, df_finger_summary_ar)
df_finger_analysis = auto_stat_test_from_summary(df_finger_summary_klassisch, df_finger_summary_ar, df_finger_klassisch, df_finger_ar)
df_finger_analysis_clean = auto_stat_test_from_summary(df_finger_summary_klassisch, df_finger_summary_ar, df_finger_klassisch_clean, df_finger_ar_clean)


##-----------analyze songscore House of the Rising Sun -------------------##
print(df_sun)

df_sun_klassisch = df_sun[df_sun['Category'] == 'Klassisch']
df_sun_ar = df_sun[df_sun['Category'] == 'AR']

# calculate the mean, standard deviation, standard error and confidence interval for each group
df_sun_summary_klassisch = analyze_scores(df_sun_klassisch)
df_sun_summary_ar = analyze_scores(df_sun_ar)

df_sun_klassisch_clean = replace_outliers_with_nan(df_sun_klassisch_raw, df_sun_summary_klassisch, alpha=0.05, verbose=True)
df_sun_ar_clean = replace_outliers_with_nan(df_sun_ar_raw, df_sun_summary_ar, alpha=0.05, verbose=True)

# test for statistical significance
df_sun_ttest_summary = ttest(df_sun_summary_klassisch, df_sun_summary_ar)
df_sun_analysis = auto_stat_test_from_summary(df_sun_summary_klassisch, df_sun_summary_ar, df_sun_klassisch, df_sun_ar)
df_sun_analysis_clean = auto_stat_test_from_summary(df_sun_summary_klassisch, df_sun_summary_ar, df_sun_klassisch_clean, df_sun_ar_clean)


##-----------analyze songscore Blues NO1 -------------------##
df_blues_klassisch = df_blues[df_blues['Category'] == 'Klassisch']
df_blues_ar = df_blues[df_blues['Category'] == 'AR']

# calculate the mean, standard deviation, standard error and confidence interval for each group
df_blues_summary_klassisch = analyze_scores(df_blues_klassisch)
df_blues_summary_ar = analyze_scores(df_blues_ar)

df_blues_klassisch_clean = replace_outliers_with_nan(df_blues_klassisch_raw, df_blues_summary_klassisch, alpha=0.05, verbose=True)
df_blues_ar_clean = replace_outliers_with_nan(df_blues_ar_raw, df_blues_summary_ar, alpha=0.05, verbose=True)

# test for statistical significance
df_blues_ttest_summary = ttest(df_blues_summary_klassisch, df_blues_summary_ar)
df_blues_analysis = auto_stat_test_from_summary(df_blues_summary_klassisch, df_blues_summary_ar, df_blues_klassisch, df_blues_ar)
df_blues_analysis_clean = auto_stat_test_from_summary(df_blues_summary_klassisch, df_blues_summary_ar, df_blues_klassisch_clean, df_blues_ar_clean)



# -------- print the results -----------
# print(df_finger_summary_klassisch)
# print(df_finger_summary_ar)
# print(df_finger_ttest_summary)
# print(df_finger_analysis)
# print(df_finger_analysis_clean)

# print(df_sun_summary_klassisch)
# print(df_sun_summary_ar)
# print(df_sun_ttest_summary)
# print(df_sun_analysis)
# print(df_sun_analysis_clean)

# print(df_blues_summary_klassisch)
# print(df_blues_summary_ar)
# print(df_blues_ttest_summary)
# print(df_blues_analysis)
# print(df_blues_analysis_clean)




