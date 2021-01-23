import os
import pandas as pd

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
        pass
    def get_data(self, fname, indicator=False):
        dfnew = pd.read_csv(os.path.join('dataset', f"{fname}.csv"))
        if 'Indicator' in dfnew.columns.tolist() and not indicator:
            dfnew.drop('Indicator', axis=1, inplace=True)
        return dfnew
    def collate_data(self, period):
        dfnew = pd.DataFrame(columns=['Location'])
        dfnew.set_index('Location', inplace=True)
        for fname in all_files:
            dff = self.get_data(fname, indicator=True)
            dff = dff[dff['Period'] == period]
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
                    dfnew = dfnew.append(new_row)
        return dfnew
    def df_difference(self, df1, df2, diff, cols=None, set_index=None):
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
        for fname in all_files:
            dff = self.get_data(fname, indicator=True)
            print(dff.columns)

my_utils = MyUtils()
