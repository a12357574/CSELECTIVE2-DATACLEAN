import pandas as pd
import numpy as np

class DataCleaner:
    """
    A utility class for cleaning and preprocessing data in a Pandas DataFrame.
    """

    def __init__(self, df):
        """
        Initialize the DataCleaner with a Pandas DataFrame.

        Parameters:
        df (pd.DataFrame): The DataFrame to clean.
        """
        self.df = df.copy()

    def standardize_columns(self):
        """
        Standardize column names by removing leading/trailing spaces,
        converting to lowercase, and replacing spaces with underscores.
        """
        self.df.columns = (
            self.df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )
        return self

    def handle_missing_values(self, strategy="drop", fill_value=None):
        """
        Handle missing values in the DataFrame.

        Parameters:
        strategy (str): The strategy for handling missing values. Options are 'mean', 'median', 'mode', 'drop' or 'fill'.
        fill_value (any): The value to fill when strategy is 'fill'.

        Returns:
        self
        """
        if strategy =="drop":
            self.df.dropna(axis=0, how='any', inplace=True)
        elif strategy == "mean":
            self.df.fillna(self.df.mean(), inplace=True)
        elif strategy == "median":
            self.df.fillna(self.df.median(), inplace=True)
        elif strategy == "mode":
            self.df.fillna(self.df.mode().iloc[0], inplace=True)
        elif strategy == "fill":
            if fill_value is not None:
                self.df.fillna(fill_value, inplace=True)
        else:
            raise ValueError("Invalid strategy for handling missing values.")
        return self

    def drop_duplicates(self):
        """
        Drop duplicate rows from the DataFrame.
        """
        self.df.drop_duplicates(inplace=True)
        return self

    def remove_outliers(self, columns=None):
        """
        Remove outliers from the specified numeric columns using the IQR method.

        Parameters:
        columns (list): List of column names to check for outliers. If None, all numeric columns are used.

        Returns:
        self
        """
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns

        for col in columns:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            self.df = self.df[
                ~((self.df[col] < (Q1 - 1.5 * IQR)) | (self.df[col] > (Q3 + 1.5 * IQR)))
            ]
        return self

    def get_cleaned_data(self):
        """
        Return the cleaned DataFrame.

        Returns:
        pd.DataFrame: The cleaned DataFrame.
        """
        return self.df
