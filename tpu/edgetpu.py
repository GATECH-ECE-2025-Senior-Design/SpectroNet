from pycoral.utils.edgetpu import list_edge_tpus

devices = list_edge_tpus()
if devices:
    print("Edge TPU is connected!")
    for dev in devices:
        print(f"Device: {dev}")
else:
    print("No Edge TPU detected.")