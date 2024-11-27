import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import io
import tempfile
import os



class PDFReport(FPDF):

    def header(self):
        self.set_font("Arial", "BU", 12)
        self.cell(0, 10, "Data Analysis Report", 0, 1, "C")
        self.ln(7)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page %s' % self.page_no(), 0, 0, 'C')
    
    def add_section(self, title):
        self.set_font("Arial", "BU", 10)
        self.cell(0, 10, title, 0, 1)
        self.ln(1)

    # This function is used to create table for given pandas series
    def add_table(self, data):
        self.set_font("Arial", "", 9)
        col_widths = [110, 30]  

        self.set_font("Arial", "BU", 9)
        self.cell(col_widths[0], 10, "Column Name", border=1)
        self.cell(col_widths[1], 10, "Missing Values", border=1, align="C")
        self.ln()

        self.set_font("Arial", "", 9)
        for col_name, missing_count in data.items():
            self.cell(col_widths[0], 10, col_name, border=1)
            self.cell(col_widths[1], 10, str(missing_count), border=1, align="C")
            self.ln()
        
    # This function is used to compare two list(before, after) by putting it in table
    def comparision_table(self, before: list, after: list):
        self.set_font("Arial", "BU", 9)
        column_width = (self.w - 2 * self.l_margin) / 2

        self.cell(column_width, 10, "Before", border=1, align="C")
        self.cell(column_width, 10, "After", border=1, align="C")
        self.ln()

        self.set_font("Arial", "", 9)

        for col_name in before:
            col_name_after = col_name if col_name in after else ""

            self.cell(column_width, 10, col_name, border=1)
            self.cell(column_width, 10, col_name_after, border=1)
            self.ln()

    # This function is used to display list of column_names in given no. of columns
    def add_multicolumn_list(self, items, num_columns=2):
        self.set_font("Arial", "", 9)
        effective_page_width = self.w - 2 * self.l_margin
        column_width = effective_page_width / num_columns  
        num_rows = math.ceil(len(items) / num_columns)

        for row in range(num_rows):
            for col in range(num_columns):
                index = row + col * num_rows
                if index < len(items):
                    self.cell(column_width, 10, items[index], border=0)
            self.ln(5)
            
    # This function creates boxplot
    def add_plots(self, df, numeric_columns):

        y_position = 35  

        for i in range(0, len(numeric_columns), 2):
            plt.clf()  # Clear the figure to avoid overlapping plots
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            
            for j in range(2):
                if i + j < len(numeric_columns):
                    col = numeric_columns[i + j]
                    sns.boxplot(x=df[col], ax=axes[j])
                    axes[j].set_title(f"Box Plot of {col}", fontsize=12)
                    axes[j].tick_params(axis='x', labelrotation=45)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
                plt.tight_layout()
                plt.savefig(tmpfile.name, format='png')
                tmpfile_path = tmpfile.name

            self.image(tmpfile_path, x=10, y=y_position, w=190)

            y_position += 80  

            if y_position > 250:  
                self.add_page()
                y_position = 30  

            os.remove(tmpfile_path)
            
    # this function create histogram
    def hist_plots(self, df, cols):

        y_position = 35 

        for i in range(0, len(cols), 2):
            plt.clf()
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            
            for j in range(2):
                if i + j < len(cols):
                    col = cols[i + j]
                    sns.histplot(df[col], kde=True)
                    axes[j].set_title(f"Distribution of {col}", fontsize=12)
                    axes[j].tick_params(axis='x')

            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
                plt.tight_layout()
                plt.savefig(tmpfile.name, format='png')
                tmpfile_path = tmpfile.name
            plt.close(fig)
            
            self.image(tmpfile_path, x=10, y=y_position, w=190)
            y_position += 80  

            os.remove(tmpfile_path)



def generate_pdf(df):
    pdf = PDFReport()

    # 1. Columns with Missing Values
    pdf.add_page()
    missing = df.isnull().sum()
    missing_values = missing[missing > 0].to_dict() 
    pdf.add_section("1. Columns with Missing Values")
    pdf.add_table(missing_values)
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    
    # 2. Displaying numeric columns
    pdf.add_page()
    pdf.add_section("2. Numeric Columns")
    pdf.add_multicolumn_list(numeric_columns, num_columns=2)
    
    
    # 3. Columns with Duplicates (Before and After)
    pdf.add_page()
    pdf.add_section("3. Columns with Duplicates (Before and After)")
    before_duplicates = df.columns.tolist()
    df = df.loc[:, ~df.columns.duplicated()]
    after_duplicates = df.columns.tolist()
    pdf.comparision_table(before_duplicates, after_duplicates)
    
    
    # 4. Constant Columns (Before and After)
    pdf.add_page()
    pdf.add_section("4. Constant Columns (Before and After)")
    before_constants = df.columns.tolist()
    constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
    df = df.drop(columns=constant_cols)
    after_constants = df.columns.tolist()
    pdf.comparision_table(before_constants, after_constants)
    
    
    # 5. Box plot for all numeric columns
    pdf.add_page()
    pdf.add_section("5. Box plot for all numeric columns")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    pdf.add_plots(df, numeric_cols)
    
    
    # 6. Histogram for any 6 numeric columns
    pdf.add_page()
    pdf.add_section("6. Histogram for any 6 numeric columns")
    if len(numeric_cols) >= 6:
        cols = np.random.choice(numeric_cols, size=6, replace=False)
    else:
        cols = numeric_cols
    pdf.hist_plots(df, cols)
    
    
    # Save the PDF
    pdf.output("data-analysis-report.pdf")
    print("pdf generated successfully")

