<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
</head>
<body>
  <h1>Indian Bail Cases EDA</h1>
  <p>
    This repository presents an <strong>exploratory data analysis (EDA)</strong> of bail applications in Indian High Courts. The dataset includes over 150,000 cases, capturing metadata, statutes, outcomes, demographics, and more. The scripts and visualizations here uncover key trends about bail outcomes, durations, statutory impacts, demographic splits, and criminal history.
  </p>
  
  <h2>Repository Contents</h2>
  <ul>
    <li>
      <strong>Data Preprocessing</strong> <br>
      Cleans missing values, parses dates, handles categorical/numeric fields, and engineers features (e.g., age bins, custody days).
    </li>
    <li>
      <strong>Univariate Analysis</strong> <br>
      Explores distributions: age groups, bail types, outcomes, criminal records, withdrawal rates, health issues, statutes, and crimes.
    </li>
    <li>
      <strong>Bivariate Analysis</strong> <br>
      Examines bail type vs. outcome, age vs. outcome, health vs. outcome, criminal record vs. outcome, statutes vs. outcomes, and more.
    </li>
    <li>
      <strong>Multivariate Analysis</strong> <br>
      Uses stacked/grouped bar charts, violin plots, 3D scatter plots for comparison across bail type, age, statutes, custody duration, and outcomes.
    </li>
    <li>
      <strong>Visualization</strong> <br>
      Static: <code>matplotlib</code>, <code>seaborn</code> <br>
      Interactive: <code>plotly</code>
    </li>
    <li>
      <strong>Code Organization</strong> <br>
      Well-commented Jupyter notebook cells with logical stepwise division.
    </li>
  </ul>
  
  <h2>Key Features</h2>
  <ul>
    <li>Comprehensive EDA: Covers univariate, bivariate, and multivariate explorations.</li>
    <li>Robust Data Cleaning: Effectively manages missing/anomalous entries.</li>
    <li>
      Domain Insights: 
      <ul>
        <li>Grant rates, health impacts, influential statutes, time to judgment.</li>
      </ul>
    </li>
    <li>Publication-Ready Plots: Thoughtful color schemes and detailed labeling.</li>
  </ul>
  
  <h2>Getting Started</h2>
  <h3>Requirements</h3>
  <ul>
    <li>Python 3.8+</li>
    <li>pandas</li>
    <li>numpy</li>
    <li>matplotlib</li>
    <li>seaborn</li>
    <li>plotly</li>
  </ul>
  
  <h3>Usage</h3>
  <ol>
    <li>Place the dataset (e.g., <code>bail_with_crime_classification.csv</code>) at the correct path (<code>/content/drive/MyDrive/IBPS/</code> or update as needed).</li>
    <li>Run the Jupyter notebook or script to start EDA and visualization.</li>
  </ol>
  
  <h3>Customization</h3>
  <ul>
    <li>Adjust file paths as per your environment.</li>
    <li>Edit plotting sections to focus on different slices or aspects of the data.</li>
  </ul>
  
  <h2>Example Plots</h2>
  <ul>
    <li>Age and outcome distributions</li>
    <li>Statute/crime bar charts</li>
    <li>Case and custody duration (histograms, pie charts)</li>
    <li>Outcome probabilities by statute/crime</li>
    <li>3D visualizations: age, duration, custody, colored by outcome</li>
  </ul>
  
  
  
  <blockquote>
    <em>For questions, suggestions, or collaborations, please create an issue or pull request!</em>
  </blockquote>
</body>
</html>
