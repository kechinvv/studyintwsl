import statistics

import pandas as pd

from research_class_task.script.alg_class import main2

aggr = {'easy': [], 'hard': [], 'zpd': []}
m_aggr = {'easy': [], 'hard': [], 'zpd': []}
d_aggr = {'easy': [], 'hard': [], 'zpd': []}


def data_analyze():
    data = pd.read_csv("../data.csv")
    for i, row in data.iterrows():
        if row['easy'] == 1:
            aggr['easy'].append([float(it) for it in row['data'][1:-1].split(', ')])
        elif row['hard'] == 1:
            aggr['hard'].append([float(it) for it in row['data'][1:-1].split(', ')])
        elif row['zpd'] == 1:
            aggr['zpd'].append([float(it) for it in row['data'][1:-1].split(', ')])
    print("easy: {}; hard: {}; zpd: {}".format(len(aggr['easy']), len(aggr['hard']), len(aggr['zpd'])))
    for l_e, l_h, l_z in zip(aggr['easy'], aggr['hard'], aggr['zpd']):
        m_aggr['easy'].append(statistics.fmean(l_e))
        m_aggr['hard'].append(statistics.fmean(l_h))
        m_aggr['zpd'].append(statistics.fmean(l_z))

        d_aggr['easy'].append(statistics.stdev(l_e))
        d_aggr['hard'].append(statistics.stdev(l_h))
        d_aggr['zpd'].append(statistics.stdev(l_z))
    print(
        "easy mean (max, mean, min, median, d): {}; {};{}; {}; {};\n".format(max(m_aggr['easy']),
                                                                             statistics.fmean(m_aggr['easy']),
                                                                             min(m_aggr['easy']),
                                                                             statistics.median(m_aggr['easy']),
                                                                             statistics.stdev(m_aggr['easy'])))
    print("hard mean (max, mean, min, median, d): {}; {}; {}; {}; {};\n".format(max(m_aggr['hard']),
                                                                                statistics.fmean(m_aggr['hard']),
                                                                                min(m_aggr['hard']),
                                                                                statistics.median(m_aggr['hard']),
                                                                                statistics.stdev(m_aggr['hard'])))
    print("zpd mean (max, mean, min, median, d): {}; {}; {}; {}; {};\n\n\n".format(max(m_aggr['zpd']),
                                                                                   statistics.fmean(m_aggr['zpd']),
                                                                                   min(m_aggr['zpd']),
                                                                                   statistics.median(m_aggr['zpd']),
                                                                                   statistics.stdev(m_aggr['zpd'])))

    print("easy d (max, mean, min, median, d): {}; {}; {}; {}; {};\n".format(max(d_aggr['easy']),
                                                                             statistics.fmean(d_aggr['easy']),
                                                                             min(d_aggr['easy']),
                                                                             statistics.median(d_aggr['easy']),
                                                                             statistics.stdev(d_aggr['easy'])))
    print("hard d (max, mean, min, median, d): {}; {};{}; {}; {};\n".format(max(d_aggr['hard']),
                                                                            statistics.fmean(d_aggr['hard']),
                                                                            min(d_aggr['hard']),
                                                                            statistics.median(d_aggr['hard']),
                                                                            statistics.stdev(d_aggr['hard'])))
    print(
        "zpd d (max, mean, min, median, d): {}; {}; {}; {}; {};".format(max(d_aggr['zpd']),
                                                                        statistics.fmean(d_aggr['zpd']),
                                                                        min(d_aggr['zpd']),
                                                                        statistics.median(d_aggr['zpd']),
                                                                        statistics.stdev(d_aggr['zpd'])))


def test_accuracy():
    data = pd.read_csv("../data.csv")
    yes = 0.0
    no = 0
    for i, row in data.iterrows():
        res = main2(row['data'])
        if row['easy'] == 1 and res == 2 or row['hard'] == 1 and res == 1 or row['zpd'] == 1 and res == 0:
            yes += 1.0
        else:
            no += 1
    print(yes)
    print("Accuracy = {}".format(yes/6000.0))

if __name__ == '__main__':
    #test_accuracy()
    data_analyze()
    # main()
