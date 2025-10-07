#!/usr/bin/env python3
"""
Data Analysis Tool - AI Generated Code
This module provides comprehensive data analysis capabilities for CSV files.
Author: AI Assistant
Date: Generated automatically
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Any
import warnings
import os
import sys
from datetime import datetime

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class DataAnalyzer:
    """
    A comprehensive data analysis class that provides various statistical
    and visualization methods for analyzing datasets.
    
    This class follows standard object-oriented programming principles
    and includes error handling for robust data processing.
    """
    
    def __init__(self, file_path: str = None):
        """
        Initialize the DataAnalyzer with optional file path.
        
        Args:
            file_path (str, optional): Path to the CSV file to analyze
        """
        self.data = None
        self.file_path = file_path
        self.analysis_results = {}
        
        if file_path:
            self.load_data(file_path)
    
    def load_data(self, file_path: str) -> bool:
        """
        Load data from a CSV file with comprehensive error handling.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"Error: File {file_path} not found.")
                return False
            
            # Load the data with pandas
            self.data = pd.read_csv(file_path)
            self.file_path = file_path
            
            print(f"Successfully loaded data from {file_path}")
            print(f"Dataset shape: {self.data.shape}")
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def basic_info(self) -> Dict[str, Any]:
        """
        Generate basic information about the dataset.
        
        Returns:
            Dict[str, Any]: Dictionary containing basic dataset information
        """
        if self.data is None:
            print("No data loaded. Please load data first.")
            return {}
        
        info_dict = {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'memory_usage': self.data.memory_usage(deep=True).sum()
        }
        
        # Store results for future reference
        self.analysis_results['basic_info'] = info_dict
        
        return info_dict
    
    def statistical_summary(self) -> pd.DataFrame:
        """
        Generate comprehensive statistical summary of numerical columns.
        
        Returns:
            pd.DataFrame: Statistical summary of the dataset
        """
        if self.data is None:
            print("No data loaded. Please load data first.")
            return pd.DataFrame()
        
        # Get only numerical columns for statistical analysis
        numerical_cols = self.data.select_dtypes(include=[np.number])
        
        if numerical_cols.empty:
            print("No numerical columns found for statistical analysis.")
            return pd.DataFrame()
        
        # Generate comprehensive statistics
        summary = numerical_cols.describe()
        
        # Add additional statistics
        summary.loc['variance'] = numerical_cols.var()
        summary.loc['skewness'] = numerical_cols.skew()
        summary.loc['kurtosis'] = numerical_cols.kurtosis()
        
        # Store results
        self.analysis_results['statistical_summary'] = summary
        
        return summary
    
    def detect_outliers(self, method: str = 'iqr') -> Dict[str, List]:
        """
        Detect outliers in numerical columns using specified method.
        
        Args:
            method (str): Method to use ('iqr' or 'zscore')
            
        Returns:
            Dict[str, List]: Dictionary with outlier indices for each column
        """
        if self.data is None:
            print("No data loaded. Please load data first.")
            return {}
        
        numerical_cols = self.data.select_dtypes(include=[np.number])
        outliers = {}
        
        for col in numerical_cols.columns:
            if method.lower() == 'iqr':
                # Interquartile Range method
                Q1 = numerical_cols[col].quantile(0.25)
                Q3 = numerical_cols[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_indices = numerical_cols[
                    (numerical_cols[col] < lower_bound) | 
                    (numerical_cols[col] > upper_bound)
                ].index.tolist()
                
            elif method.lower() == 'zscore':
                # Z-score method
                z_scores = np.abs((numerical_cols[col] - numerical_cols[col].mean()) / numerical_cols[col].std())
                outlier_indices = numerical_cols[z_scores > 3].index.tolist()
            
            else:
                print(f"Unknown method: {method}. Using IQR method.")
                continue
            
            outliers[col] = outlier_indices
        
        self.analysis_results['outliers'] = outliers
        return outliers
    
    def correlation_analysis(self) -> pd.DataFrame:
        """
        Perform correlation analysis on numerical columns.
        
        Returns:
            pd.DataFrame: Correlation matrix
        """
        if self.data is None:
            print("No data loaded. Please load data first.")
            return pd.DataFrame()
        
        numerical_cols = self.data.select_dtypes(include=[np.number])
        
        if numerical_cols.shape[1] < 2:
            print("Need at least 2 numerical columns for correlation analysis.")
            return pd.DataFrame()
        
        correlation_matrix = numerical_cols.corr()
        self.analysis_results['correlation_matrix'] = correlation_matrix
        
        return correlation_matrix
    
    def create_visualizations(self, save_plots: bool = False) -> None:
        """
        Create comprehensive visualizations of the dataset.
        
        Args:
            save_plots (bool): Whether to save plots to files
        """
        if self.data is None:
            print("No data loaded. Please load data first.")
            return
        
        numerical_cols = self.data.select_dtypes(include=[np.number])
        categorical_cols = self.data.select_dtypes(include=['object', 'category'])
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. Distribution plots for numerical columns
        if not numerical_cols.empty:
            n_cols = min(3, len(numerical_cols.columns))
            n_rows = (len(numerical_cols.columns) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
            if n_rows == 1 and n_cols == 1:
                axes = [axes]
            elif n_rows == 1:
                axes = axes
            else:
                axes = axes.flatten()
            
            for i, col in enumerate(numerical_cols.columns):
                if i < len(axes):
                    axes[i].hist(numerical_cols[col].dropna(), bins=30, alpha=0.7, edgecolor='black')
                    axes[i].set_title(f'Distribution of {col}')
                    axes[i].set_xlabel(col)
                    axes[i].set_ylabel('Frequency')
            
            # Hide empty subplots
            for i in range(len(numerical_cols.columns), len(axes)):
                axes[i].axis('off')
            
            plt.tight_layout()
            if save_plots:
                plt.savefig('distributions.png', dpi=300, bbox_inches='tight')
            plt.show()
        
        # 2. Correlation heatmap
        if not numerical_cols.empty and len(numerical_cols.columns) > 1:
            plt.figure(figsize=(10, 8))
            correlation_matrix = numerical_cols.corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5)
            plt.title('Correlation Matrix')
            plt.tight_layout()
            if save_plots:
                plt.savefig('correlation_matrix.png', dpi=300, bbox_inches='tight')
            plt.show()
    
    def generate_report(self, output_file: str = None) -> str:
        """
        Generate a comprehensive analysis report.
        
        Args:
            output_file (str, optional): File path to save the report
            
        Returns:
            str: The generated report as a string
        """
        if self.data is None:
            return "No data loaded. Please load data first."
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("DATA ANALYSIS REPORT")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"File: {self.file_path}")
        report_lines.append("")
        
        # Basic information
        basic_info = self.basic_info()
        report_lines.append("BASIC INFORMATION:")
        report_lines.append("-" * 20)
        report_lines.append(f"Dataset shape: {basic_info.get('shape', 'N/A')}")
        report_lines.append(f"Number of columns: {len(basic_info.get('columns', []))}")
        report_lines.append(f"Memory usage: {basic_info.get('memory_usage', 0) / 1024:.2f} KB")
        report_lines.append("")
        
        # Missing values
        missing_vals = basic_info.get('missing_values', {})
        if any(missing_vals.values()):
            report_lines.append("MISSING VALUES:")
            report_lines.append("-" * 15)
            for col, count in missing_vals.items():
                if count > 0:
                    percentage = (count / len(self.data)) * 100
                    report_lines.append(f"{col}: {count} ({percentage:.2f}%)")
            report_lines.append("")
        
        # Statistical summary
        stats = self.statistical_summary()
        if not stats.empty:
            report_lines.append("STATISTICAL SUMMARY:")
            report_lines.append("-" * 20)
            report_lines.append(stats.round(3).to_string())
            report_lines.append("")
        
        # Outliers
        outliers = self.detect_outliers()
        if outliers:
            report_lines.append("OUTLIER DETECTION:")
            report_lines.append("-" * 18)
            for col, indices in outliers.items():
                if indices:
                    report_lines.append(f"{col}: {len(indices)} outliers detected")
            report_lines.append("")
        
        report_text = "\n".join(report_lines)
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write(report_text)
                print(f"Report saved to {output_file}")
            except Exception as e:
                print(f"Error saving report: {str(e)}")
        
        return report_text

# Example usage and main function
def main():
    """
    Main function demonstrating the usage of DataAnalyzer class.
    This is a typical AI-generated main function with comprehensive examples.
    """
    print("Data Analysis Tool - AI Generated")
    print("=" * 40)
    
    # Example usage (commented out as no actual file is provided)
    # analyzer = DataAnalyzer()
    # 
    # if analyzer.load_data('sample_data.csv'):
    #     # Perform basic analysis
    #     basic_info = analyzer.basic_info()
    #     print("Basic Info:", basic_info)
    #     
    #     # Statistical summary
    #     stats = analyzer.statistical_summary()
    #     print("\nStatistical Summary:")
    #     print(stats)
    #     
    #     # Detect outliers
    #     outliers = analyzer.detect_outliers('iqr')
    #     print(f"\nOutliers detected: {sum(len(v) for v in outliers.values())}")
    #     
    #     # Correlation analysis
    #     corr = analyzer.correlation_analysis()
    #     print("\nCorrelation matrix shape:", corr.shape)
    #     
    #     # Create visualizations
    #     analyzer.create_visualizations(save_plots=True)
    #     
    #     # Generate report
    #     report = analyzer.generate_report('analysis_report.txt')
    #     print("\nReport generated successfully!")
    
    print("Example usage code is available in the main() function.")
    print("Please provide a CSV file path to use this tool.")

if __name__ == "__main__":
    main()