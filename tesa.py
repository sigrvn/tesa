#!/usr/bin/env python3
# tesa - TimeEdit Schema Analyzer

from argparse import ArgumentParser
import pandas as pd

class Schema:
    def __init__(self, filepath, lang='se'):
        self.df = pd.read_csv(filepath, skiprows=[0,1,2])
        self.df = self.df.drop(labels=['Slutdatum', 'Program', 'Grupp', 'Karta', 'Utrustning '], axis=1)
        self.df['start_datetime'] = self.df['Startdatum'] + ' ' + self.df['Starttid']
        self.df.sort_values(by='start_datetime', inplace=True)
        self.lang = lang

    def __repr__(self):
        return repr(self.df)

    @property
    def holidays(self):
        return self.df[self.df['Starttid'] == '00:00']

    @property
    def exams(self):
        if self.lang == 'se':
            return self.df[self.df['Moment'] == 'Tentamen']
        return self.df[self.df['Moment'] == 'Exam']

    def find_conflicts(self):
        self.num_conflicts = 0
        for i, row in self.df.iterrows():
            next_rows = self.df.iloc[i+1:]
            overlapping_rows = next_rows[next_rows['start_datetime'] == row['start_datetime']]
            if not overlapping_rows.empty:
                print(f"CONFLICT at {row['start_datetime']} between [{row['Kurs']}] and {[k for k in overlapping_rows['Kurs']]}")
                self.num_conflicts += 1
        print(f"Found {self.num_conflicts} schedule conflicts in total.")

if __name__ == '__main__':
    parser = ArgumentParser(description='A command-line tool to examine schemas from TimeEdit')
    parser.add_argument('csvfile', help='The file to parse')
    parser.add_argument('-D', '--dump', action='store_true', help='Dump all rows & columns to stdout')
    args = parser.parse_args()

    if args.dump:
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

    schema = Schema(args.csvfile)

    print('Holidays:', schema.holidays)
    print('Exams:', schema.exams)
    print('Classes:', schema)

    schema.find_conflicts()

