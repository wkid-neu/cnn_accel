from prettytable import PrettyTable
import numpy as np

info_fp = "layer_info.csv"
latency_fp = "layer_latency_m32p32.csv"
res1_fp = "res1_m32p32.csv"
res2_fp = "res2_m32p32.csv"
res_txt_fp = "res_m32p32.txt"

def get_n_op_conv(
    OC, INC, INH_, INW_,
    KH, KW, strideH, strideW, 
    padL, padR, padU, padD
):
    OH = (INH_+padU+padD-KH)//strideH+1
    OW = (INW_+padL+padR-KW)//strideW+1
    n_pixels = OC*OH*OW
    n_op_pixel = INC*KH*KW*2
    return n_pixels*n_op_pixel

def get_layer_latency():
    ret = {}
    latency_data = np.loadtxt(latency_fp, str, delimiter=",")
    for i in range(1, len(latency_data)):
        ret.update({latency_data[i][0]: int(latency_data[i][1])})
    return ret

def get_layer_info():
    ret = {}
    data = np.loadtxt(info_fp, str, delimiter=",")
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

def main():
    layer_latency = get_layer_latency()
    layer_info = get_layer_info()

    # latency_ms
    layer_latency_ms = {}
    for k, v in layer_latency.items():
        layer_latency_ms.update({k: v/(10**6)})
    
    # latency_contrib
    latency_contrib = {}
    layer_latency_list = [v for k, v in layer_latency.items()]
    for k, v in layer_latency.items():
        latency_contrib.update({k: v/sum(layer_latency_list)})

    # Operations(MOP)
    n_ops = {}
    for k, v in layer_info.items():
        n_op = 0
        if "Conv" in k:
            n_op = get_n_op_conv(v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10], v[11], v[12])
        n_ops.update({k: n_op})
    mops = {}
    for k, v in n_ops.items():
        mops.update({k: v/(10**6)})

    # throughput(GOP/s)
    gop_s = {}
    for k, v in layer_latency.items():
        gop_s.update({k: n_ops[k]/layer_latency[k]})
    
    # dsp efficiency
    effs = {}
    for k, v in layer_latency.items():
        effs.update({k: gop_s[k]/(32*32*0.398*2)})
    
    # total latency 
    total_latency = sum(layer_latency.values())
    
    # conv_latency
    conv_latency = 0
    for k, v in layer_latency.items():
        if "Conv" in k:
            conv_latency += v
    
    # other_latency
    other_latency = total_latency - conv_latency

    # total_ops
    total_ops = sum(n_ops.values())

    # conv_ops
    conv_ops = total_ops

    # other_ops
    other_ops = 0

    # total_throughput
    total_throughput = total_ops/total_latency

    # conv_throughput
    conv_throughput = conv_ops/conv_latency

    # other_throughput
    other_throughput = other_ops/other_latency
    
    # FPS
    fps = (10**9)/total_latency
    
    #
    # pretty table
    #
    table = PrettyTable([
        "layer_name", "layer_type", "latency(ms)", "latency_contrib(%)", "operations(MOP)", "throughput(GOP/s)", "efficiency(%)"
    ])
    for layer_name in layer_latency.keys():
        table.add_row([
            layer_name, layer_info[layer_name][0], 
            "{:.3f}".format(layer_latency_ms[layer_name]),
            "{:.2f}".format(latency_contrib[layer_name]*100),
            "{:.3f}".format(mops[layer_name]),
            "{:.2f}".format(gop_s[layer_name]),
            "{:.2f}".format(effs[layer_name]*100),
        ])
    print(table)

    print("total_latency: {:.3f} ms".format(total_latency/(10**6)))
    print("conv_latency: {:.3f} ms ({:.0f}%)".format(conv_latency/(10**6), conv_latency*100/total_latency))
    print("other_latency: {:.3f} ms ({:.0f}%)".format(other_latency/(10**6), other_latency*100/total_latency))
    print("total_ops: {:.3f} GOP".format(total_ops/(10**9)))
    print("conv_ops: {:.3f} GOP ({:.0f}%)".format(conv_ops/(10**9), conv_ops*100/total_ops))
    print("other_ops: {:.3f} GOP ({:.0f}%)".format(other_ops/(10**9), other_ops*100/total_ops))
    print("total_throughput: {:.3f} GOP/s".format(total_throughput))
    print("conv_throughput: {:.3f} GOP/s".format(conv_throughput))
    print("other_throughput: {:.3f} GOP/s".format(other_throughput))
    print("FPS: {:.2f} Frame/s".format(fps))

    #
    # csv
    #
    with open(res1_fp, mode="w", encoding="utf-8") as f:
        f.write("layer_name,layer_type,latency(ms),latency_contrib(%),operations(MOP),throughput(GOP/s),efficiency(%)\n")
        for layer_name in layer_latency.keys():
            f.write("{},{},{},{},{},{},{}\n".format(
                layer_name, layer_info[layer_name][0], 
                "{:.3f}".format(layer_latency_ms[layer_name]),
                "{:.2f}".format(latency_contrib[layer_name]*100),
                "{:.3f}".format(mops[layer_name]),
                "{:.2f}".format(gop_s[layer_name]),
                "{:.2f}".format(effs[layer_name]*100)
            ))
    with open(res2_fp, mode="w", encoding="utf-8") as f:
        f.write("total_latency,conv_latency,other_latency,total_ops,conv_ops,other_ops,total_throughput,conv_throughput,other_throughput,FPS\n")
        f.write("{},{},{},{},{},{},{},{},{},{}".format(
            "{:.3f} ms".format(total_latency/(10**6)),
            "{:.3f} ms ({:.0f}%)".format(conv_latency/(10**6), conv_latency*100/total_latency),
            "{:.3f} ms ({:.0f}%)".format(other_latency/(10**6), other_latency*100/total_latency),
            "{:.3f} GOP".format(total_ops/(10**9)),
            "{:.3f} GOP ({:.0f}%)".format(conv_ops/(10**9), conv_ops*100/total_ops),
            "{:.3f} GOP ({:.0f}%)".format(other_ops/(10**9), other_ops*100/total_ops),
            "{:.3f} GOP/s".format(total_throughput),
            "{:.3f} GOP/s".format(conv_throughput),
            "{:.3f} GOP/s".format(other_throughput),
            "{:.2f} Frame/s".format(fps)
        ))
    
    #
    # txt
    #
    with open(res_txt_fp, mode="w", encoding="utf-8") as f:
        f.write(str(table))
        f.write("\n\n")
        f.write("total_latency: {:.3f} ms\n".format(total_latency/(10**6)))
        f.write("conv_latency: {:.3f} ms ({:.0f}%)\n".format(conv_latency/(10**6), conv_latency*100/total_latency))
        f.write("other_latency: {:.3f} ms ({:.0f}%)\n\n".format(other_latency/(10**6), other_latency*100/total_latency))
        f.write("total_ops: {:.3f} GOP\n".format(total_ops/(10**9)))
        f.write("conv_ops: {:.3f} GOP ({:.0f}%)\n".format(conv_ops/(10**9), conv_ops*100/total_ops))
        f.write("other_ops: {:.3f} GOP ({:.0f}%)\n\n".format(other_ops/(10**9), other_ops*100/total_ops))
        f.write("total_throughput: {:.3f} GOP/s\n".format(total_throughput))
        f.write("conv_throughput: {:.3f} GOP/s\n".format(conv_throughput))
        f.write("other_throughput: {:.3f} GOP/s\n\n".format(other_throughput))
        f.write("FPS: {:.2f} Frame/s\n".format(fps))

main()