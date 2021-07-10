import os, re
import numpy as np
import pandas as pd

# Contains utility functions to be used in jupyter notebooks

# File names of all csv files
all_files = [
    'lifeExpectancyAtBirth', 'HALElifeExpectancyAtBirth', 'maternalMortalityRatio',
    'birthAttendedBySkilledPersonal', 'infantMortalityRate', 'neonatalMortalityRate',
    'under5MortalityRate', 'incedenceOfMalaria', 'incedenceOfTuberculosis',
    'hepatitusBsurfaceAntigen', 'interventionAgianstNTDs', 'newHivInfections',
    '30-70cancerChdEtc', 'crudeSuicideRates', 'AlcoholSubstanceAbuse',
    'roadTrafficDeaths', 'reproductiveAgeWomen', 'adolescentBirthRate',
    'uhcCoverage', 'dataAvailibilityForUhc', 'population10SDG3.8.2',
    'population25SDG3.8.2', 'airPollutionDeathRate', 'mortalityRateUnsafeWash',
    'mortalityRatePoisoning', 'tobaccoAge15', 'medicalDoctors', 'nursingAndMidwife',
    'Dentists', 'Pharmacists', 'eliminateViolenceAgainstWomen', 'basicDrinkingWaterServices',
    'atLeastBasicSanitizationServices', 'safelySanitization', 'basicHandWashing',
    'cleanFuelAndTech'
]

class MyUtils():
    def __init__(self):
        # RE expression for bracketed information within the dataset
        self.rebrackets = re.compile(r'\[[\d.]+\-[\d.]+\]')
    def get_data(self, fname, indicator=False):
        # Utility function that takes file name and returns a dataframe
        dfnew = pd.read_csv(os.path.join('dataset', f"{fname}.csv"))
        if 'Indicator' in dfnew.columns.tolist() and not indicator:
            dfnew.drop('Indicator', axis=1, inplace=True)
        return dfnew
    def collate_period(self, period):
        # Collate data for a certain year
        dfnew = pd.DataFrame(columns=['Location'])
        dfnew.set_index('Location', inplace=True)
        for fname in all_files:
            concat_list = [dfnew]
            # Get raw dataframe
            dff = self.get_data(fname, indicator=True)
            dff = dff[dff['Period'] == period]
            # Data cleaning
            if 'Dim1' in dfnew.columns.tolist():
                if 'Both sexes' in set(dff['Dim1']):
                    dff = dff[dff['Dim1'] == 'Both sexes']
                elif 'Total' in set(dff['Dim1']):
                    dff = dff[dff['Dim1'] == 'Total']
                dff.drop('Dim1', axis=1, inplace=True)
            for index, row in dff.set_index('Location').iterrows():
                if index in dfnew.index.tolist():
                    dfnew.loc[index, row['Indicator']] = row['First Tooltip']
                else:
                    new_row = pd.DataFrame([[index, row['First Tooltip']]], columns=['Location', row['Indicator']])
                    new_row.set_index('Location', inplace=True)
                    concat_list.append(new_row)
            # Concatenate data from different csv files
            dfnew = pd.concat(concat_list)
        return dfnew
    def collate_latest(self):
        # Same as above but takes the latest data of each location instead
        dfnew = pd.DataFrame(columns=['Location'])
        dfnew.set_index('Location', inplace=True)
        for fname in all_files:
            concat_list = [dfnew]
            dff = self.get_data(fname, indicator=True)
            if 'Dim1' in dfnew.columns.tolist():
                if 'Both sexes' in set(dff['Dim1']):
                    dff = dff[dff['Dim1'] == 'Both sexes']
                elif 'Total' in set(dff['Dim1']):
                    dff = dff[dff['Dim1'] == 'Total']
                dff.drop('Dim1', axis=1, inplace=True)
            for locationstr in set(dff['Location']):
                dfflocation = dff[dff['Location'] == locationstr]
                latestperiod = dfflocation['Period'].max()
                dffindex = dfflocation[dfflocation['Period'] == latestperiod].index[0]
                row = dfflocation.loc[dffindex]
                if locationstr in dfnew.index.tolist():
                    dfnew.loc[locationstr, row['Indicator']] = row['First Tooltip']
                else:
                    new_row = pd.DataFrame([[locationstr, row['First Tooltip']]], columns=['Location', row['Indicator']])
                    new_row.set_index('Location', inplace=True)
                    concat_list.append(new_row)
            dfnew = pd.concat(concat_list)
        return dfnew
    def remove_brackets(self, numstr):
        # Utility function to remove brackets from a value if the value is string
        try:
            re_match = self.rebrackets.search(numstr)
            try:
                numstr = numstr[:re_match.start()].strip()
                return float(numstr)
            except AttributeError:
                return np.nan
        except TypeError:
            return numstr
    def df_latest_cleaned(self):
        # Get latest data of each location and cleans it further
        df = self.collate_latest()
        df = df[df.isna().sum(axis=1) < 10]
        cols = df.columns[df.dtypes == np.object].tolist()
        for _, row in df.iterrows():
            for col in cols:
                df.loc[row.name, col] = self.remove_brackets(row[col])
        # Fill unknown values with average
        df = df.fillna(df.mean())
        return df
    def df_difference(self, df1, df2, diff, cols=None, set_index=None):
        # Compare difference of a certain column for DataFrames of different time periods or genders
        if set_index != None:
            df1 = df1.set_index(set_index)
            df2 = df2.set_index(set_index)
        if cols == None:
            cols = df1.columns.tolist()
            cols.remove(diff)
        dfnew = pd.DataFrame(columns=[set_index] + cols)
        indexname = df1.index.name
        for index, row in df2.iterrows():
            if index in df1.index.tolist():
                rowdict = {col: row[col] for col in cols}
                rowdict[indexname] = index
                rowdict['Diff'] = df1.loc[index, diff] - row[diff]
                dfnew = dfnew.append(rowdict, ignore_index=True)
        return dfnew
    def column_lists(self):
        # Print all column names
        for fname in all_files:
            dff = self.get_data(fname, indicator=True)
            print(dff.columns)

my_utils = MyUtils()
