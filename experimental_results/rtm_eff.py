import numpy as np
import matplotlib.pyplot as plt
import math

models = ["alexnet", "zfnet", "squeezenet1_0", "vovnet27s", "selecsls42b", "resnet18", "resnet34", "resnet50", "vgg11", "vgg13", "vgg16", "vgg19"]
algo_sizes = [3088, 12944, 12704, 25088, 12544, 9408, 9408, 28224, 32982, 51744,51744,51744,]
labels = ["$\mathbf{AlexNet}$", "$\mathbf{ZFNet}$", "$\mathbf{SqueezeNet}$", "$\mathbf{VoVNet}$", "$\mathbf{SelecSLS}$", "$\mathbf{ResNet18}$", "$\mathbf{ResNet34}$", "$\mathbf{ResNet50}$", "$\mathbf{Vgg11}$", "$\mathbf{Vgg13}$", "$\mathbf{Vgg16}$", "$\mathbf{Vgg19}$"]

def get_layer_info(model_name):
    ret = {}
    data = np.loadtxt(f"{model_name}/layer_info.csv", str, delimiter=",")
    for i in range(1, len(data)):
        ret.update({
            data[i][0]: (
                data[i][1], 
                int(data[i][2]), int(data[i][3]), int(data[i][4]), int(data[i][5]), 
                int(data[i][6]), int(data[i][7]), int(data[i][8]), int(data[i][9]), 
                int(data[i][10]), int(data[i][11]), int(data[i][12]), int(data[i][13])
            )
        })
    return ret

def cal_linear_size(model_name):
    total_size = int(224*224/32)
    last_tensor_size = 0

    for k, v in get_layer_info(model_name).items():
        if ("Conv" in k) or ("Gemm" in k) or ("MaxPool" in k) or ("AveragePool" in k):
            OC,INC,INH_,INW_,KH,KW,strideH,strideW,padL,padR,padU,padD = v[1:]
            OH = (INH_+padU+padD-KH)//strideH+1
            OW = (INW_+padL+padR-KW)//strideW+1
            tensor_size = int((OC/4)*(math.ceil(OH*OW/32)))
            total_size += tensor_size
            last_tensor_size = tensor_size
        elif ("Add" in k):
            total_size += last_tensor_size
        else:
            raise
    return total_size

def plot():
    data_linear, data_algo = [], []
    for model_name, algo_size in zip(models,algo_sizes):
        data_linear.append(cal_linear_size(model_name))
        data_algo.append(algo_size)

    min_ratio, min_idx = 1000, -1
    for i in range(len(data_linear)):
        model_name, lin, algo = models[i], data_linear[i], data_algo[i]
        ratio = lin/algo
        if ratio < min_ratio:
            min_ratio, min_idx = ratio, i
    print(models[min_idx], data_linear[min_idx], data_algo[min_idx], min_ratio)

    max_ratio, max_idx = 0, -1
    for i in range(len(data_linear)):
        model_name, lin, algo = models[i], data_linear[i], data_algo[i]
        ratio = lin/algo
        if ratio > max_ratio:
            max_ratio, max_idx = ratio, i
    print(models[max_idx], data_linear[max_idx], data_algo[max_idx], max_ratio)

    plt.figure(figsize=(4.8,6.4))

    width = 0.75
    spine_width = 3
    colors = ['#FFCC99', '#6A00FF']
    plt.bar([it-(width/4) for it in range(len(models))], data_linear, width=width/2, color=colors[0],label="Linear")
    plt.bar([it+(width/4) for it in range(len(models))], data_algo, width=width/2, color=colors[1],label="Algorithm. 1")
    plt.plot([-1,len(models)],[65536,65536], linestyle="--", color=colors[1])

    plt.xticks(range(len(models)), labels, rotation=75)
    ax = plt.gca()
    ax.tick_params(which='both', width=3, length=0, direction='in')
    ax.yaxis.set_tick_params(labelsize=15)
    ax.xaxis.set_tick_params(labelsize=13)
    plt.yticks([0,20000,40000,60000,80000,100000,120000,140000], ["$\mathbf{0}$","$\mathbf{20000}$","$\mathbf{40000}$","$\mathbf{60000}$","$\mathbf{80000}$","$\mathbf{100000}$","$\mathbf{120000}$","$\mathbf{140000}$"])

    ax.spines['top'].set_linewidth(0)
    ax.spines['bottom'].set_linewidth(spine_width)
    ax.spines['left'].set_linewidth(spine_width)
    ax.spines['right'].set_linewidth(0)

    plt.xlim((-0.5, len(models)-0.5))
    
    plt.subplots_adjust(left=0.2, right=0.97, top=0.97, bottom=0.2)
    plt.savefig("rtm_eff.png")

plot()