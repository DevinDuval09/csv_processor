import datetime as dt
import os
from DataFile import DataFile

def report_time(method, repititions, *args, **kwargs):
    times = []
    for rep in range(repititions):
        start = dt.datetime.now()
        method(*args, **kwargs)
        end = dt.datetime.now()
        runtime = end - start
        times.append(runtime.total_seconds())
    report = f'''
            Function call:  {method.__name__}
            Args:           {args}
            Kwargs:         {kwargs}
            Sample size:    {repititions}
            Average:        {sum(times) / len(times)}
            Spread:         {max(times) - min(times)}
            '''
    print(report)

if __name__=="__main__":
    file_path = os.path.dirname(__file__) + "/Data.csv"
    report_time(DataFile.create, 10, file_path)