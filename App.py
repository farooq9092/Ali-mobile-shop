import streamlit as st
from graphviz import Digraph
import time

st.set_page_config(page_title="TCP/IP + OSI Advanced Simulator v3", layout="wide")

st.title("🌐 TCP/IP + OSI Advanced Simulator v3")
st.write("Interactive Lab Simulator: Sender → Routers → Receiver with OSI/TCP-IP view & animation")

# Sidebar
st.sidebar.header("Simulation Settings")
protocol = st.sidebar.selectbox("Transport Protocol", ["TCP", "UDP"])
message = st.sidebar.text_input("Enter Message", "Hello World")
src_ip = st.sidebar.text_input("Source IP", "192.168.1.10")
dst_ip = st.sidebar.text_input("Destination IP", "192.168.1.20")
src_port = st.sidebar.text_input("Source Port", "5000")
dst_port = st.sidebar.text_input("Destination Port", "80")
show_osi = st.sidebar.checkbox("Show OSI Model Layers")
simulate = st.sidebar.button("Start Simulation")

# Optional Packet Loss / Delay
simulate_delay = st.sidebar.slider("Network Delay (sec)", 0.0, 3.0, 1.0)
simulate_loss = st.sidebar.slider("Packet Loss (%)", 0, 50, 0)

routers = ["Router1", "Router2"]  # Multiple routers

def encapsulate(data):
    if protocol == "TCP":
        transport = f"TCP(src={src_port}, dst={dst_port})[{data}]"
    else:
        transport = f"UDP(src={src_port}, dst={dst_port})[{data}]"
    internet = f"IP(src={src_ip}, dst={dst_ip})[{transport}]"
    network_access = f"ETH_FRAME[{internet}]"
    return data, transport, internet, network_access

def network_diagram(packet_stage=None):
    g = Digraph()
    g.node("A", "Sender")
    for r in routers:
        g.node(r, r)
    g.node("B", "Receiver")
    g.edge("A", routers[0], label=packet_stage or "Packet")
    for i in range(len(routers)-1):
        g.edge(routers[i], routers[i+1], label=packet_stage or "Forward")
    g.edge(routers[-1], "B", label=packet_stage or "Forward")
    return g

def simulate_packet_flow():
    app, transport, internet, frame = encapsulate(message)
    stages = [("Application Layer", app),
              ("Transport Layer", transport),
              ("Internet Layer", internet),
              ("Network Access Layer", frame)]
    
    # Encapsulation display
    st.subheader("1️⃣ Encapsulation Process")
    if show_osi:
        osi_dict = {
            "Application": app,
            "Presentation": f"[Format]{app}",
            "Session": f"[Session]{app}",
            "Transport": transport,
            "Network": internet,
            "Data Link": frame,
            "Physical": "Bits on medium"
        }
        for l, val in osi_dict.items():
            st.write(f"**{l}** → {val}")
    else:
        col1, col2, col3, col4 = st.columns(4)
        for col, (layer, val) in zip([col1,col2,col3,col4], stages):
            col.write(f"**{layer}** → {val}")

    st.divider()
    
    st.subheader("2️⃣ Network Path Simulation")
    # Animate packet through routers
    for i, r in enumerate(["Sender"] + routers + ["Receiver"]):
        st.write(f"Packet at: {r}")
        st.graphviz_chart(network_diagram(packet_stage=f"Stage {i+1}"))
        time.sleep(simulate_delay)
        # Simulate packet loss
        if simulate_loss > 0 and i != 0 and i != len(routers)+1:
            import random
            if random.randint(0,100) < simulate_loss:
                st.warning(f"Packet lost at {r}! Simulation stopped.")
                return
    
    st.divider()
    
    st.subheader("3️⃣ Decapsulation at Receiver")
    try:
        step1 = frame.replace("ETH_FRAME[", "").rstrip("]")
        step2 = step1.split("[",1)[1].rstrip("]") if "[" in step1 else step1
        step3 = step2.split("[",1)[1].rstrip("]") if "[" in step2 else step2
        st.success("Application Received Message: " + step3)

        if show_osi:
            osi_decaps = {
                "Physical Layer": "Bits received from medium",
                "Data Link Layer": f"ETH_FRAME stripped → {step1}",
                "Network Layer": f"IP Header stripped → {step2}",
                "Transport Layer": f"{protocol} Header stripped → {step3}",
                "Session Layer": "[Session info processed]",
                "Presentation Layer": "[Data format converted]",
                "Application Layer": step3
            }
            for l, val in osi_decaps.items():
                st.write(f"**{l}** → {val}")
    except Exception as e:
        st.error("Error during decapsulation: " + str(e))

if simulate and message:
    simulate_packet_flow()
else:
    st.info("Enter message and click Start Simulation")
