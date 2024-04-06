import matplotlib.pyplot as plt
import numpy as np

import re

def to_snake_case(text):
    # Remove the text inside parentheses
    text_no_parentheses = re.sub(r'\(.*\)', '', text).strip()
    # Convert the remaining text to snake case
    snake_case_text = re.sub(r'\s+', '_', text_no_parentheses).lower()
    return snake_case_text

def draw_plots(v1, v1b, v2, v2b, v3, v3b, xlabel, title):
    nodes = np.array([5, 10])
    configurations = ['CAPACITY=5', 'CAPACITY=10', 'CAPACITY=20']
    
    
    data = {}
    data[configurations[0]] = np.array([v1, v1b])
    data[configurations[1]] = np.array([v2, v2b])
    data[configurations[2]] = np.array([v3, v3b])


    # Create a new plot
    fig, ax = plt.subplots()

    # Plot each set of data with a different color/marker
    colors = ['blue', 'green', 'purple']
    markers = ['o', 's', '*']

    for i, config in enumerate(configurations):
        ax.plot(nodes, data[config], label=f'{config}', color=colors[i], marker=markers[i])

    # Set the x-axis and y-axis labels
    ax.set_xlabel(xlabel)
    #ax.set_ylabel('Throughput (transactions per second)')

    # Set the title of the graph
    ax.set_title(title)

    # Set x-axis to only show 5 and 10
    ax.set_xticks([5, 10])

    # Display the legend
    ax.legend()

    # Display grid
    plt.grid(True)

    # Save the plot
    plt.savefig(f'./graphs/{to_snake_case(title)}.png')


#Plot for throughput 
# Regular expression to match the throughput line
throughput_pattern = re.compile(r'Throughput: (\d+\.\d+)')
def access_throughput_values(num_clients, node):
    throughput_values = []
    with open(f'./results/{num_clients}_clients_node_{node}.txt', 'r') as f:
        for line in f:
            # Search for the throughput pattern in each line
            match = throughput_pattern.search(line)
            if match:
                # If a match is found, extract the throughput value and add it to the list
                throughput_value = float(match.group(1))
                throughput_values.append(throughput_value)
    return throughput_values[:3]

v1_lst = []
v2_lst = []
v3_lst = []
for i in range(5):
    results = access_throughput_values(5, i)
    v1_lst.append(results[0])
    v2_lst.append(results[1])
    v3_lst.append(results[2])
    
v1b_lst = []
v2b_lst = []
v3b_lst = []
for i in range(10):
    results = access_throughput_values(10, i)
    v1b_lst.append(results[0])
    v2b_lst.append(results[1])
    v3b_lst.append(results[2])


# Plot for throughput
v1 = np.mean(v1_lst)
v2 = np.mean(v2_lst)
v3 = np.mean(v3_lst)

v1b = np.mean(v1b_lst)
v2b = np.mean(v2b_lst)
v3b = np.mean(v3b_lst)
# v1 = np.mean([9.331358, 15.375154, 9.378872, 13.259394, 8.774589])
# v2 = np.mean([10.391538, 17.164397, 9.729683, 14.340055, 9.930661])
# v3 = np.mean([10.529440, 18.788317, 9.428368, 13.337049, 9.718499])

# v1b = np.mean([10.625859, 18.565225, 8.952322, 12.168245, 9.236935, 9.213880, 8.383090, 8.559336, 9.066058, 7.106778])
# v2b = np.mean([9.517590, 17.766291, 8.801946, 12.542743, 9.313786, 8.492372, 7.572207, 8.341033, 8.368959, 7.209342])
# v3b = np.mean([10.259409, 16.378631, 8.285317, 11.578684, 8.775040, 8.333500, 7.968240, 8.245580, 8.034943, 6.964961])

draw_plots(v1, v1b, v2, v2b, v3, v3b, 'Number of Nodes', 'Throughput (transactions per second)')


blocktime_pattern = re.compile(r'Block time: (\d+\.\d+)')
def access_blocktime_values(num_clients, node):
    blocktime_values = []
    with open(f'./results/{num_clients}_clients_node_{node}.txt', 'r') as f:
        for line in f:
            # Search for the block time pattern in each line
            match = blocktime_pattern.search(line)
            if match:
                # If a match is found, extract the block time value and add it to the list
                blocktime_value = float(match.group(1))
                blocktime_values.append(blocktime_value)
    return blocktime_values[:3]

# Plot for block time
results = access_blocktime_values(5, 0)
v1 = results[0]
v2 = results[1]
v3 = results[2]

results = access_blocktime_values(10, 0)
v1b = results[0]
v2b = results[1]
v3b = results[2]

# v1 = 0.520344
# v2 = 0.566399
# v3 = 1.030447
# v1b = 0.681229
# v2b = 1.101646
# v3b = 2.004743

draw_plots(v1, v1b, v2, v2b, v3, v3b, 'Number of Nodes', 'Block Time (seconds)')
