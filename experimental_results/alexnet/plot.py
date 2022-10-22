import matplotlib.pyplot as plt
import numpy as np

accs = ["m32p32", "m32p64", "m32p96", "m64p64"]

def find_res1(acc_name):
    fp = f"res1_{acc_name}.csv"
    data = np.loadtxt(fp, str, delimiter=",")
    data = data[1:, :]
    return data

def find_res2( acc_name):
    fp = f"res2_{acc_name}.csv"
    data = np.loadtxt(fp, str, delimiter=",")
    data = data[1:, :]
    return data

def find_conv_eff(acc_name):
    data = find_res1(acc_name)
    layers = list(data[:,0])
    effs = list(data[:,6])
    effs = [float(it) for it in effs]
    conv_layers, conv_effs = [], []
    for i in range(len(layers)):
        if "Conv" in layers[i]:
            conv_layers.append(layers[i])
            conv_effs.append(effs[i]/100)
    return conv_layers, conv_effs

def find_conv_throughput(acc_name):
    data = find_res1(acc_name)
    layers = list(data[:,0])
    throughputs = list(data[:,5])
    throughputs = [float(it) for it in throughputs]
    conv_layers, conv_throughputs = [], []
    for i in range(len(layers)):
        if "Conv" in layers[i]:
            conv_layers.append(layers[i])
            conv_throughputs.append(throughputs[i])
    return conv_layers, conv_throughputs

def find_normalized_latency(acc_name):
    data = find_res1(acc_name)
    layer_types = list(data[:,1])
    contribs = list(data[:,3])
    contribs = [float(it) for it in contribs]
    ret = {
        "Conv": 0, "Fc": 0, "Pool": 0, "Add": 0
    }
    for i in range(len(layer_types)):
        if "Conv" in layer_types[i]:
            ret["Conv"] += contribs[i]/100
        if "Pool" in layer_types[i]:
            ret["Pool"] += contribs[i]/100
        if "Add" in layer_types[i]:
            ret["Add"] += contribs[i]/100
        if "Fc" in layer_types[i]:
            ret["Fc"] += contribs[i]/100
    return ret

def find_conv_eff2():
    conv_effs = []
    for acc_name in accs:
        conv_layers, tmp = find_conv_eff(acc_name)
        conv_effs.append(tmp)
    return conv_layers, conv_effs

def find_conv_throughput2():
    conv_throughputs = []
    for acc_name in accs:
        conv_layers, tmp = find_conv_throughput(acc_name)
        conv_throughputs.append(tmp)
    return conv_layers, conv_throughputs

def find_normalized_latency2():
    ret = []
    for acc_name in accs:
        ret.append(find_normalized_latency(acc_name))
    return ret

def plot_conv_throughput():
    conv_layers, conv_throughputs = find_conv_throughput2()

    colors = ['#FF0000', '#008A00', '#0000FF', '#FF00FF']
    markers = ["D", "o", "*", "d"]
    spine_width = 3
    for i in range(len(accs)):
        plt.plot(range(len(conv_layers)), conv_throughputs[i], color=colors[i], marker=markers[i], markersize=10, linewidth=3)
    for i in range(len(accs)):
        plt.plot([0,len(conv_layers)-1], [819.2*(i+1), 819.2*(i+1)], color=colors[i], linestyle="-.", linewidth=3)
    plt.ylim((0,3500))
    
    ax = plt.gca()
    ax.xaxis.set_visible(False)

    ax.tick_params(which='both', width=3, length=7, direction='in')
    ax.yaxis.set_tick_params(labelsize=20)
    plt.yticks([0,500,1000,1500,2000,2500,3000,3500], ["$\mathbf{0}$","$\mathbf{500}$","$\mathbf{1000}$","$\mathbf{1500}$","$\mathbf{2000}$","$\mathbf{2500}$","$\mathbf{3000}$","$\mathbf{3500}$"])

    ax.spines['top'].set_linewidth(spine_width)
    ax.spines['bottom'].set_linewidth(spine_width)
    ax.spines['left'].set_linewidth(spine_width)
    ax.spines['right'].set_linewidth(spine_width)
    
    plt.subplots_adjust(right=0.99, top=0.97, bottom=0.03)
    
    plt.savefig(f"throughput.png")

def plot_normalized_latency():
    normalized_latencys = find_normalized_latency2()
    colors = ['c', 'm', 'y', "#6A00FF"]
    width = 0.75
    spine_width = 6

    plt.figure(figsize=(2.4,4.8))
    for i in range(len(accs)):
        normalized_latency = normalized_latencys[i]
        plt.bar([i], normalized_latency["Conv"], bottom=0, color=colors[0], width=width)
        plt.bar([i], normalized_latency["Fc"], bottom=normalized_latency["Conv"], color=colors[1], width=width)
        plt.bar([i], normalized_latency["Pool"], bottom=normalized_latency["Conv"]+normalized_latency["Fc"], color=colors[2], width=width)
        plt.bar([i], normalized_latency["Add"], bottom=normalized_latency["Conv"]+normalized_latency["Fc"]+normalized_latency["Pool"], color=colors[3], width=width)
    plt.xlim((-0.5,3.5))
    plt.ylim((0,1))

    ax = plt.gca()
    ax.yaxis.set_visible(False)
    ax.tick_params(which='both', width=6, length=10, direction='in')
    ax.xaxis.set_tick_params(labelsize=20)
    plt.xticks([0,1,2,3], ["M32P32","M32P64", "M32P96", "M64P64"], rotation=60)

    ax.spines['top'].set_linewidth(0)
    ax.spines['bottom'].set_linewidth(spine_width)
    ax.spines['left'].set_linewidth(0)
    ax.spines['right'].set_linewidth(0)

    plt.subplots_adjust(left=0.03, right=0.97, top=0.97, bottom=0.25)

    plt.savefig(f"normalized_latency.png")

plot_conv_throughput()
plot_normalized_latency()